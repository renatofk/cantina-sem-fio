import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from decimal import Decimal
from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import CaraPassaDevice, CaraPassaEvent, History, Meal, Student, Transaction


EVENT_TYPE = "biometric.subject_recognized.v1"


class InvalidWebhook(ValueError):
    pass


class BusinessRuleRejected(ValueError):
    pass


@dataclass
class ConsumptionResult:
    history: History
    transaction: Transaction | None


def canonical_body(payload):
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()


def validate_signature(raw_body, timestamp_header, signature_header):
    if not timestamp_header or not signature_header:
        raise InvalidWebhook("Cabeçalhos de assinatura ausentes")
    timestamp = parse_datetime(timestamp_header)
    if timestamp is None:
        raise InvalidWebhook("Timestamp de assinatura inválido")
    if timezone.is_naive(timestamp):
        timestamp = timezone.make_aware(timestamp, dt_timezone.utc)
    delta = abs((datetime.now(dt_timezone.utc) - timestamp.astimezone(dt_timezone.utc)).total_seconds())
    if delta > settings.CARAPASSA_TIMESTAMP_TOLERANCE_SECONDS:
        raise InvalidWebhook("Timestamp fora da tolerância")
    try:
        payload = json.loads(raw_body)
    except (TypeError, json.JSONDecodeError) as exc:
        raise InvalidWebhook("JSON inválido") from exc
    signed = timestamp_header.encode() + b"." + canonical_body(payload)
    expected = "sha256=" + hmac.new(
        settings.CARAPASSA_WEBHOOK_SECRET.encode(), signed, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        raise InvalidWebhook("Assinatura inválida")
    return payload


def validate_payload(payload):
    required = {
        "event_id", "event_type", "tenant_id", "school_id", "subject_id",
        "device_id", "occurred_at", "confidence", "distance", "model_version",
    }
    if not isinstance(payload, dict) or required - payload.keys():
        raise InvalidWebhook("Payload incompleto")
    if payload["event_type"] != EVENT_TYPE:
        raise InvalidWebhook("event_type não suportado")
    for field in ("event_id", "tenant_id", "school_id", "subject_id", "device_id"):
        try:
            UUID(str(payload[field]))
        except (TypeError, ValueError, AttributeError) as exc:
            raise InvalidWebhook(f"{field} inválido") from exc
    try:
        Decimal(str(payload["confidence"]))
        Decimal(str(payload["distance"]))
    except (TypeError, ValueError) as exc:
        raise InvalidWebhook("Métricas biométricas inválidas") from exc
    occurred_at = parse_datetime(payload["occurred_at"])
    if occurred_at is None:
        raise InvalidWebhook("occurred_at inválido")
    payload["_occurred_at"] = occurred_at
    return payload


def register_consumption(student, occurred_at):
    if student.status != "active":
        raise BusinessRuleRejected("Aluno inativo")
    local_dt = timezone.localtime(occurred_at) if timezone.is_aware(occurred_at) else occurred_at
    meal = Meal.objects.filter(start_time__lte=local_dt.time(), end_time__gte=local_dt.time()).first()
    if meal is None:
        raise BusinessRuleRejected("Nenhuma refeição disponível neste horário")
    key = f"{student.pk}:{meal.pk}:{local_dt.date().isoformat()}"
    if History.objects.filter(consumption_key=key).exists():
        raise BusinessRuleRejected("Refeição já registrada neste período")

    wallet = list(
        Student.objects.select_for_update()
        .filter(user=student.user, plan="avulso")
        .order_by("pk")
    ) if student.user_id else [Student.objects.select_for_update().get(pk=student.pk)]
    locked_student = next((item for item in wallet if item.pk == student.pk), student)
    if locked_student.plan == "avulso" and locked_student.balance < meal.price:
        raise BusinessRuleRejected("Saldo insuficiente")

    history = History.objects.create(
        student=locked_student, meal=meal, detected_at=occurred_at,
        approved_by=None, consumption_key=key,
    )
    debit = None
    if locked_student.plan == "avulso":
        debit = Transaction.objects.create(
            history=history, valor=-meal.price, username=locked_student.user, type="debito"
        )
        for member in wallet:
            member.balance = member.balance - Decimal(meal.price)
            member.save(update_fields=("balance",))
    return ConsumptionResult(history, debit)


def process_webhook(payload):
    clean_payload = {key: value for key, value in payload.items() if not key.startswith("_")}
    with transaction.atomic():
        event, created = CaraPassaEvent.objects.get_or_create(
            event_id=payload["event_id"],
            defaults={
                "event_type": payload["event_type"], "tenant_id": payload["tenant_id"],
                "school_id": payload["school_id"], "subject_id": payload["subject_id"],
                "device_id": payload["device_id"], "occurred_at": payload["_occurred_at"],
                "confidence": payload["confidence"], "distance": payload["distance"],
                "model_version": payload["model_version"], "payload": clean_payload,
            },
        )
        if not created:
            return event, False

        device = CaraPassaDevice.objects.filter(
            tenant_id=payload["tenant_id"], school_id=payload["school_id"],
            device_id=payload["device_id"], active=True,
        ).first()
        student = Student.objects.filter(integration_id=payload["subject_id"]).first()
        event.device_mapping, event.student = device, student
        if device is None or student is None:
            missing = "dispositivo" if device is None else "aluno"
            event.processing_status = CaraPassaEvent.Status.ERROR
            event.processing_error = f"Mapeamento de {missing} inexistente"
        else:
            try:
                result = register_consumption(student, payload["_occurred_at"])
                event.history, event.transaction = result.history, result.transaction
                event.processing_status = CaraPassaEvent.Status.PROCESSED
                event.processed_at = timezone.now()
            except BusinessRuleRejected as exc:
                event.processing_status = CaraPassaEvent.Status.REJECTED
                event.processing_error = str(exc)
                event.processed_at = timezone.now()
        event.save()
        return event, True

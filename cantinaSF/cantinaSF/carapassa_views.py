import json
import logging
from uuid import UUID

import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .carapassa import InvalidWebhook, process_webhook, validate_payload, validate_signature
from .models import Student


logger = logging.getLogger(__name__)


@login_required
@require_POST
def carapassa_face_status(request):
    """Same-origin proxy for the CaraPassa bulk face-status endpoint."""
    try:
        body = json.loads(request.body or b"{}")
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "JSON inválido"}, status=400)

    subject_ids = body.get("subject_ids")
    if not isinstance(subject_ids, list) or not subject_ids or len(subject_ids) > 100:
        return JsonResponse({"error": "Informe entre 1 e 100 alunos"}, status=400)
    try:
        subject_ids = [str(UUID(value)) for value in subject_ids]
    except (TypeError, ValueError, AttributeError):
        return JsonResponse({"error": "subject_id inválido"}, status=400)

    if not request.user.is_staff and not request.user.groups.filter(id=3).exists():
        return JsonResponse({"error": "Sem permissão"}, status=403)

    allowed = Student.objects.filter(integration_id__in=subject_ids)
    if request.user.groups.filter(id=3).exists():
        allowed = allowed.filter(user=request.user)
    allowed_ids = {str(value) for value in allowed.values_list("integration_id", flat=True)}
    if len(allowed_ids) != len(set(subject_ids)):
        return JsonResponse({"error": "Aluno não encontrado ou sem permissão"}, status=403)
    if not settings.CARAPASSA_API_KEY:
        return JsonResponse({"error": "Integração CaraPassa não configurada"}, status=503)

    try:
        response = requests.post(
            settings.CARAPASSA_FACE_STATUS_URL,
            json={"subject_ids": list(allowed_ids)},
            headers={"Authorization": f"Bearer {settings.CARAPASSA_API_KEY}"},
            timeout=settings.CARAPASSA_FACE_STATUS_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload.get("subjects"), list):
            raise ValueError("Resposta sem a lista subjects")
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Falha ao consultar status facial no CaraPassa: %s", exc)
        return JsonResponse({"error": "Não foi possível consultar o CaraPassa"}, status=502)

    return JsonResponse(payload)


@csrf_exempt
@require_POST
def carapassa_webhook(request):
    if not settings.CARAPASSA_ENABLED:
        return JsonResponse({"error": "Integração desabilitada"}, status=404)
    if not settings.CARAPASSA_WEBHOOK_SECRET:
        return JsonResponse({"error": "Integração não configurada"}, status=503)
    try:
        payload = validate_signature(
            request.body,
            request.headers.get("X-CaraPassa-Timestamp"),
            request.headers.get("X-CaraPassa-Signature"),
        )
        payload = validate_payload(payload)
    except InvalidWebhook as exc:
        status = 401 if "assinatura" in str(exc).lower() or "timestamp" in str(exc).lower() else 400
        logger.warning("Webhook CaraPassa recusado: %s", exc)
        return JsonResponse({"error": str(exc)}, status=status)

    event, created = process_webhook(payload)
    logger.info(
        "Webhook CaraPassa event_id=%s status=%s duplicate=%s subject_id=%s device_id=%s error=%s",
        event.event_id,
        event.processing_status,
        not created,
        event.subject_id,
        event.device_id,
        event.processing_error or "-",
    )
    return JsonResponse(
        {"status": event.processing_status, "duplicate": not created}, status=200
    )

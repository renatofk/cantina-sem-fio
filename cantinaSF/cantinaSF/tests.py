import hashlib
import hmac
import json
import uuid
from unittest.mock import patch
from datetime import datetime, timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse

from .carapassa import canonical_body
from .carapassa import process_webhook, validate_payload
from .models import CaraPassaDevice, CaraPassaEvent, Course, History, Meal, Student, Transaction


@override_settings(
    CARAPASSA_ENABLED=True,
    CARAPASSA_WEBHOOK_SECRET="test-secret",
    CARAPASSA_TIMESTAMP_TOLERANCE_SECONDS=300,
)
class CaraPassaWebhookTests(TestCase):
    def setUp(self):
        self.tenant_id, self.school_id, self.device_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        self.user = get_user_model().objects.create_user(username="parent", password="x")
        course = Course.objects.create(course_name="1A", teacher="Teacher")
        self.student = Student.objects.create(
            name="Ana", last_name="Silva", plan="avulso", birthday="2012-01-01",
            status="active", user=self.user, courses=course, balance=Decimal("50.00"),
        )
        Meal.objects.create(meal_name="Almoço", price=Decimal("12.00"), start_time="11:00", end_time="14:00")
        CaraPassaDevice.objects.create(
            tenant_id=self.tenant_id, school_id=self.school_id, device_id=self.device_id, name="Cantina 1"
        )

    def payload(self, **changes):
        data = {
            "event_id": str(uuid.uuid4()), "event_type": "biometric.subject_recognized.v1",
            "tenant_id": str(self.tenant_id), "school_id": str(self.school_id),
            "subject_id": str(self.student.integration_id), "device_id": str(self.device_id),
            "occurred_at": datetime.now(timezone.utc).replace(hour=15, minute=0).isoformat(),
            "confidence": 0.95, "distance": 0.31, "model_version": "face-api-128-v1",
        }
        data.update(changes)
        return data

    def post(self, payload, secret="test-secret", timestamp=None):
        timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        body = canonical_body(payload)
        signature = "sha256=" + hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()
        return self.client.post(
            reverse("carapassa_webhook"), data=body, content_type="application/json",
            HTTP_X_CARAPASSA_TIMESTAMP=timestamp, HTTP_X_CARAPASSA_SIGNATURE=signature,
        )

    def test_success_debits_and_records(self):
        response = self.post(self.payload())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CaraPassaEvent.objects.get().processing_status, "processed")
        self.student.refresh_from_db()
        self.assertEqual(self.student.balance, Decimal("38.00"))
        self.assertEqual(History.objects.count(), 1)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_invalid_signature(self):
        self.assertEqual(self.post(self.payload(), secret="wrong").status_code, 401)
        self.assertFalse(CaraPassaEvent.objects.exists())
    def test_replay_is_idempotent(self):
        payload = self.payload()
        self.assertEqual(self.post(payload).status_code, 200)
        response = self.post(payload)
        self.assertTrue(response.json()["duplicate"])
        self.assertEqual(History.objects.count(), 1)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_unknown_student_is_persisted_without_debit(self):
        response = self.post(self.payload(subject_id=str(uuid.uuid4())))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CaraPassaEvent.objects.get().processing_status, "error")
        self.assertFalse(Transaction.objects.exists())

    def test_insufficient_balance_rolls_back_consumption(self):
        self.student.balance = Decimal("1.00")
        self.student.save(update_fields=("balance",))
        response = self.post(self.payload())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CaraPassaEvent.objects.get().processing_status, "rejected")
        self.assertFalse(History.objects.exists())
        self.assertFalse(Transaction.objects.exists())

    def test_second_event_same_meal_period_is_not_charged(self):
        self.post(self.payload())
        response = self.post(self.payload())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CaraPassaEvent.objects.filter(processing_status="rejected").count(), 1)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_transaction_failure_rolls_back_everything(self):
        payload = validate_payload(self.payload())
        with patch("cantinaSF.carapassa.Transaction.objects.create", side_effect=RuntimeError("db error")):
            with self.assertRaises(RuntimeError):
                process_webhook(payload)
        self.student.refresh_from_db()
        self.assertEqual(self.student.balance, Decimal("50.00"))
        self.assertFalse(History.objects.exists())
        self.assertFalse(CaraPassaEvent.objects.exists())


@override_settings(
    CARAPASSA_API_KEY="test-api-key",
    CARAPASSA_FACE_STATUS_URL="https://carapassa.test/api/subjects/face-status",
    CARAPASSA_FACE_STATUS_TIMEOUT_SECONDS=15,
)
class CaraPassaFaceStatusTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(id=3, name="Responsáveis")
        self.user = get_user_model().objects.create_user(username="parent-status", password="x")
        self.user.groups.add(self.group)
        self.student = Student.objects.create(
            name="Bia", last_name="Souza", plan="assinatura", birthday="2012-01-01",
            status="active", user=self.user,
        )
        self.client.force_login(self.user)

    @patch("cantinaSF.carapassa_views.requests.post")
    def test_proxies_bulk_status_without_exposing_api_key(self, post):
        post.return_value.raise_for_status.return_value = None
        post.return_value.json.return_value = {
            "subjects": [{
                "subject_id": str(self.student.integration_id),
                "face_registered": True,
                "registered_at": "2026-08-12T18:00:00Z",
            }]
        }
        response = self.client.post(
            reverse("carapassa_face_status"),
            data=json.dumps({"subject_ids": [str(self.student.integration_id)]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["subjects"][0]["face_registered"])
        post.assert_called_once_with(
            "https://carapassa.test/api/subjects/face-status",
            json={"subject_ids": [str(self.student.integration_id)]},
            headers={"Authorization": "Bearer test-api-key"},
            timeout=15,
        )

    def test_rejects_invalid_subject_id(self):
        response = self.client.post(
            reverse("carapassa_face_status"),
            data=json.dumps({"subject_ids": ["invalid"]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_parent_cannot_query_another_parents_student(self):
        other = Student.objects.create(
            name="Caio", last_name="Lima", plan="assinatura", birthday="2011-01-01",
            status="active",
        )
        response = self.client.post(
            reverse("carapassa_face_status"),
            data=json.dumps({"subject_ids": [str(other.integration_id)]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)


@override_settings(
    CARAPASSA_API_KEY="test-api-key",
    CARAPASSA_DELETE_SUBJECT_URL="https://carapassa.test/v1/subjects/{subject_id}",
    CARAPASSA_DELETE_TIMEOUT_SECONDS=30,
)
class CaraPassaSubjectDeletionTests(TestCase):
    @patch("cantinaSF.carapassa_client.requests.delete")
    def test_delete_subject_uses_authenticated_endpoint(self, delete):
        from .carapassa_client import delete_subject

        subject_id = uuid.uuid4()
        delete.return_value.status_code = 204
        delete.return_value.raise_for_status.return_value = None
        delete_subject(subject_id)
        delete.assert_called_once_with(
            f"https://carapassa.test/v1/subjects/{subject_id}",
            headers={"Authorization": "Bearer test-api-key"},
            timeout=30,
        )

    @patch("cantinaSF.carapassa_client.requests.delete")
    def test_missing_remote_subject_is_already_deleted(self, delete):
        from .carapassa_client import delete_subject

        delete.return_value.status_code = 404
        delete_subject(uuid.uuid4())
        delete.return_value.raise_for_status.assert_not_called()

    @patch("cantinaSF.carapassa_client.requests.delete")
    def test_remote_failure_blocks_deletion(self, delete):
        import requests
        from .carapassa_client import CaraPassaSubjectDeletionError, delete_subject

        delete.side_effect = requests.ConnectionError("offline")
        with self.assertRaises(CaraPassaSubjectDeletionError):
            delete_subject(uuid.uuid4())

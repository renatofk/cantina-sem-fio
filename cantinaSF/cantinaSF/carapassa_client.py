import logging

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


class CaraPassaSubjectDeletionError(RuntimeError):
    pass


def delete_subject(subject_id):
    """Delete a biometric subject. A missing subject is already deleted."""
    if not settings.CARAPASSA_API_KEY:
        raise CaraPassaSubjectDeletionError("A integração CaraPassa não está configurada")

    url = settings.CARAPASSA_DELETE_SUBJECT_URL.format(subject_id=subject_id)
    try:
        response = requests.delete(
            url,
            headers={"Authorization": f"Bearer {settings.CARAPASSA_API_KEY}"},
            timeout=settings.CARAPASSA_DELETE_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        logger.warning("Falha ao remover subject %s do CaraPassa: %s", subject_id, exc)
        raise CaraPassaSubjectDeletionError(
            "Não foi possível contatar o CaraPassa; o aluno não foi excluído"
        ) from exc

    if response.status_code == 404:
        return
    try:
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning(
            "CaraPassa recusou a remoção do subject %s: HTTP %s",
            subject_id,
            response.status_code,
        )
        raise CaraPassaSubjectDeletionError(
            "O CaraPassa não confirmou a remoção; o aluno não foi excluído"
        ) from exc

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from .models import Student
from .carapassa import BusinessRuleRejected, register_consumption
from django.db import transaction
from django.contrib.auth import get_user_model
import json
from django.shortcuts import render
from django.conf import settings

def capture_photo_view(request, student_id, student_name):
    return render(request, 'capture_photo.html', {'student_id': student_id, 'student_name': student_name})

User = get_user_model()

@csrf_exempt
def registrar_presencas(request):
    if request.method == 'OPTIONS':
        # Responde à preflight
        response = JsonResponse({'ok': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    if request.method != "POST":
        print(f"Método não permitido: {request.method}")
        return JsonResponse({"error": "Método [{request.method}] não permitido. Só se permite POST"}, status=405)
    
    # Valida o token de segurança
    token = request.headers.get("KIOSK-SECRET-KEY")
    kiosk_secret = settings.KIOSK_SECRET_KEY
    if token != kiosk_secret:
        return JsonResponse({"error": "Token inválido"}, status=403)

    try:
        presencas = json.loads(request.body)
        results = []
        for p in presencas:
            datetime_obj = parse_datetime(p.get("datetime", ""))
            if not datetime_obj:
                results.append({"student_id": p.get("student_id"), "status": "invalid_datetime"})
                continue
            try:
                with transaction.atomic():
                    student = Student.objects.get(id=p["student_id"])
                    register_consumption(student, datetime_obj)
                results.append({"student_id": student.pk, "status": "processed"})
            except (Student.DoesNotExist, BusinessRuleRejected) as exc:
                results.append({"student_id": p.get("student_id"), "status": "rejected", "reason": str(exc)})

        return JsonResponse({"status": "ok", "results": results})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

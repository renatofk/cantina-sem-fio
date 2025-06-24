from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from .models import Student, Meal, History, Transaction
from django.contrib.auth import get_user_model
import json
from decimal import Decimal
from django.shortcuts import render

def capture_photo_view(request, student_id, student_name):
    return render(request, 'capture_photo.html', {'student_id': student_id, 'student_name': student_name})

User = get_user_model()

@csrf_exempt
def registrar_presencas(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        presencas = json.loads(request.body)
        for p in presencas:
            student = Student.objects.get(id=p["student_id"])
            print(f"Processando presença para o aluno: {student.name}")
            datetime_obj = parse_datetime(p["datetime"])
            print(f"Data e hora: {datetime_obj}")
            if not datetime_obj:
                continue

            # Encontrar refeição correspondente
            hora = datetime_obj.time()
            print(f"Hora atual: {hora}")
            refeicao = Meal.objects.filter(start_time__lte=hora, end_time__gte=hora).first()
            print(f"Refeição encontrada: {refeicao}")
            if not refeicao:
                continue
            print(f"Estudante: {student.plan}")
            # Criar histórico
            history = History.objects.create(
                student=student,
                meal=refeicao,
                detected_at=datetime_obj,
                approved_by=None  # Ou algum user default
            )
            print(f"Histórico criado: {history}")
            # Se plano for avulso, criar transação
            if student.plan == "avulso":
                valor = refeicao.price
                print(f"Valor da refeição: {valor}")
                Transaction.objects.create(
                    history=history,
                    valor=valor,
                    username=None  # Ou defina um admin default
                )
                # Atualizar saldo
                student.balance -= Decimal(valor)
                student.save()

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

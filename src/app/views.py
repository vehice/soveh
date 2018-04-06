from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from accounts.models import *
from backend.models import *


@login_required
def home(request):
    return render(request, "app/home.html", {})


@login_required
def show_users(request):
    users = User.objects.all()
    usuarios = []
    for usuario in users:
        aux = {
            'user':
            usuario.first_name.title() + " " + usuario.last_name.title(),
            'email': usuario.email,
            'id': usuario.id,
            'estado': usuario.is_active,
            'admin': usuario.is_superuser
        }
        usuarios.append(aux)
    return render(request, 'app/users.html', {'users': usuarios})


@login_required
def show_empresas(request):
    return render(request, 'app/empresas.html', {})


@login_required
def show_analisis(request):
    return render(request, 'app/analisis.html', {})


@login_required
def show_ingresos(request):
    return render(request, 'app/ingresos.html', {})


@login_required
def new_ingreso(request):

    species = Specie.objects.all()
    larvalStages = LarvalStage.objects.all()
    fixtatives = Fixative.objects.all()
    waterSources = WaterSource.objects.all()
    questionReceptionCondition = QuestionReceptionCondition.objects.filter(
        status='a')
    exams = Exam.objects.all()
    organs = Organ.objects.all()

    return render(
        request, 'app/nuevo_ingreso.html', {
            'specie_list': species,
            'larvalStage_list': larvalStages,
            'fixtative_list': fixtatives,
            'waterSource_list': waterSources,
            'questionReceptionCondition_list': questionReceptionCondition,
            'exam_list': exams,
            'organ_list': organs
        })

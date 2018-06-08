from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from accounts.models import *
from backend.models import *
from workflows.models import *


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
    return render(request, 'app/users.html', {'user_list': usuarios})


@login_required
def show_clientes(request):
    customers = Customer.objects.all()
    return render(request, 'app/clientes.html', {'customer_list': customers})


@login_required
def show_analisis(request):
    exams = Exam.objects.all()
    return render(request, 'app/analisis.html', {'exam_list': exams})


@login_required
def show_ingresos(request):
    up = UserProfile.objects.filter(user=request.user).first()

    if up.user.is_staff:
        form = Form.objects.filter(content_type__model='entryform')
    else:
        form = Form.objects.filter(
            content_type__model='entryform',
            state__step__actors__profile=up.profile)

    return render(request, 'app/ingresos.html', {'entryForm_list': form})


@login_required
def show_ingresos_by_id(request, form_id):
    up = UserProfile.objects.filter(user=request.user).first()

    if up.user.is_staff:
        form = Form.objects.filter(content_type__model='entryform')
    else:
        form = Form.objects.filter(
            content_type__model='entryform',
            state__step__actors__profile=up.profile)

    return render(request, 'app/ingresos.html', {'entryForm_list': form})


@login_required
def new_ingreso(request):
    flow = Flow.objects.get(pk=1)
    entryform = EntryForm.objects.create()
    form = Form.objects.create(
        content_object=entryform, flow=flow, state=flow.step_set.first().state)

    return show_workflow_main_form(request, form_id=form.id)


@login_required
def show_workflow_main_form(request, form_id):
    form = Form.objects.get(pk=form_id)
    entryform_id = form.content_object.id

    return render(request, 'app/workflow_main.html', {
        'form': form,
        'form_id': form_id,
        'entryform_id': entryform_id
    })


@login_required
def show_workflow_analysis_form(request, form_id):
    form = Form.objects.get(pk=form_id)
    analysis = form.content_object
    analysis_id = analysis.id
    exam_name = analysis.exam.name
    entryform_id = analysis.entryform_id

    return render(
        request, 'app/workflow_analysis.html', {
            'form': form,
            'form_id': form_id,
            'analysis_id': analysis_id,
            'exam_name': exam_name,
            'entryform_id': entryform_id,
        })

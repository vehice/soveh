from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse

from accounts.models import *
from backend.models import *
from workflows.models import *

import datetime


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
        form = Form.objects.filter(content_type__model='entryform').order_by('-object_id')
    else:
        form = Form.objects.filter(
            content_type__model='entryform',
            state__step__actors__profile=up.profile).order_by('-object_id')

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
    no_caso = "V0{0}".format(entryform.pk)
    entryform.no_caso = no_caso
    entryform.save()
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

def make_pdf_file(id):
    import pdfkit
    import os
    from django.conf import settings

    d = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    options = {
            'quiet': '',
            'page-size': "A4",
            'viewport-size': "1280x1024",
            'encoding': "UTF-8",
            'margin-top': "5mm",
            'margin-left': "5mm",
            'margin-right': "5mm",
            'margin-bottom': "5mm",
            'no-stop-slow-scripts': '',
            'load-error-handling': "ignore",
            'disable-javascript': ''
        }

    urlsitio = settings.SITE_URL +'/template-report/' + str(id)
    pdf = pdfkit.from_url(urlsitio, False, options=options)
    return pdf

@login_required
def download_report(request, id):
    form = Form.objects.get(pk=id)
    entryform_id = form.content_object.id
    pdf = make_pdf_file(entryform_id)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=testing_informe.pdf'

    return response

def template_report(request, id):
    from django.forms.models import model_to_dict
    report = Report.objects.filter(analysis_id=int(id))

    # dataset = {}
    # for item in report:
    #     if item.organ_id in dataset:
    #         dataset[item.organ_id].push(model_to_dict(item))



    return render(request, 'app/template_report.html',{'report': report})
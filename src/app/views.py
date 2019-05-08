from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Count

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
    editar = up.profile_id in (1,3)
    eliminar = editar and request.user.is_superuser
    check_forms = Form.objects.filter(content_type__model='entryform', state__id=1)
    for f in check_forms:
        if Identification.objects.filter(entryform=f.content_object).count() == 0:
            f.delete()

    form = Form.objects.filter(content_type__model='entryform').order_by('-object_id')
    if up.profile_id == 5:
        ids = EntryForm.objects.filter(sample__sampleexams__patologo_id=up.user_id).values_list('id')
        form_ids = form.filter(object_id__in=ids).values_list('id')
        state_ids = Form.objects.filter(content_type__model='analysisform', parent_id__in=form_ids, state_id__in=[10,11]).values_list('parent_id')
        form = form.filter(id__in=state_ids)

    # else:
    #     form = Form.objects.filter(
    #         content_type__model='entryform',
    #         state__step__actors__profile=up.profile).order_by('-object_id')

    return render(request, 'app/ingresos.html', {'entryForm_list': form, 'edit': editar, 'eliminar': eliminar})


@login_required
def show_ingresos_by_id(request, form_id):
    up = UserProfile.objects.filter(user=request.user).first()

    if up.user.is_staff:
        form =  Form.objects.filter(content_type__model='entryform')
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
    actor = Actor.objects.filter(profile_id=request.user.userprofile.profile_id).first()
    edit = 1 if actor.permission.filter(from_state_id=1, type_permission='w').first() else 0
    if not edit:
        return show_ingresos(request)

    return render(request, 'app/workflow_main.html', {
        'form': form,
        'form_id': form_id,
        'entryform_id': entryform_id,
        'edit': edit
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
            'encoding': "UTF-8",
            'margin-top': "5mm",
            'margin-left': "5mm",
            'margin-right': "5mm",
            'margin-bottom': "5mm",
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
    response['Content-Disposition'] = 'attachment; filename="informe.pdf"'

    return response

def template_report(request, id):
    analisis = AnalysisForm.objects.get(id=int(id))
    report = Report.objects.filter(analysis_id=int(id))
    report_final = ReportFinal.objects.filter(analysis_id=int(id)).last()
    return render(request, 'app/template_report.html',{'analisis': analisis, 'report': report, 'report_final':report_final })

@login_required
def preview_report(request, id):
    form = Form.objects.get(pk=int(id))
    entryform_id = form.content_object.id
    reports = Report.objects.filter(analysis_id=int(entryform_id))
    
    from collections import defaultdict

    res = defaultdict(list)
    for report in reports:
        res[report.identification_id].append(report)

    data = {}
    for key, value in res.items():
        samples = Sample.objects.filter(identification_id=key).order_by('index')
        matrix = []
        first_column = ["MUESTRA / HALLAZGO", ""]
        first_column = first_column + list(map(lambda x: x.identification.cage+"-"+x.identification.group+"-"+str(x.index), samples))
        matrix.append(first_column + [""])
        
        res2 = defaultdict(list)
        for elem in value:
            res2[elem.pathology.name + " en " + elem.organ_location.name].append(elem)

        for key2, value2 in res2.items():
            column = [value2[0].organ.name, key2]
            samples_by_index = {}
            
            for sam in samples:
                samples_by_index[sam.index] = []

            for item in value2:
                if item.identification_id == key:
                    samples_by_index[item.slice.cassette.sample.index].append(item.diagnostic_intensity.name)

            aux = []
            count_hallazgos = 0
            for k, v in samples_by_index.items():
                if len(v) > 0:
                    aux.append(v[0])
                    count_hallazgos += 1
                else:
                    aux.append("")

            column = column + aux
            percent = int(round((count_hallazgos*100) / len(samples),0))
            column.append(str(percent) +"%")
            matrix.append(column)

        data[key] = list(zip(*matrix))
        
    return render(request, 'app/preview_report.html', {'report': reports, 'form_id': form.pk, 'form_parent_id': form.parent.id, 'reports2': data})
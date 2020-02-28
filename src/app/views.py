from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Count
from django.forms.models import model_to_dict

from accounts.models import *
from backend.models import *
from workflows.models import *
from django.db import connection

import datetime
import json

@login_required
def home(request):
    services = Exam.objects.values('id', 'name')
    dates = EntryForm.objects.all().values_list('created_at', flat = True).distinct()
    years = []
    for d in dates:
        if d and not d.year in years: 
            years.append(d.year)
    
    cursor1=connection.cursor()
    data1 = cursor1.execute(
    """
        SELECT e.id, e.`name`, COUNT(*) as count
        FROM backend_sample s
        INNER JOIN backend_analysisform a ON s.entryform_id = a.entryform_id
        INNER JOIN backend_exam e ON a.exam_id = e.id
        INNER JOIN workflows_form f ON a.entryform_id = f.object_id
        WHERE f.flow_id = 1 AND f.deleted = 0
        GROUP BY e.`name`, e.id
        ORDER BY count DESC;
    """)
    top_10 = cursor1.fetchmany(10)
    top_10 = json.dumps(top_10)
    return render(request, "app/home.html", {'services': services, 'years': years, "top_10":top_10})


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

    form = Form.objects.filter(content_type__model='entryform', deleted=False).order_by('-object_id')
    if up.profile_id == 5:
        ids = EntryForm.objects.filter(analysisform__patologo_id=up.user_id).values_list('id')
        form_ids = form.filter(object_id__in=ids).values_list('id')
        state_ids = Form.objects.filter(content_type__model='analysisform', parent_id__in=form_ids, state_id__in=[10,11]).values_list('parent_id')
        form = form.filter(id__in=state_ids)

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
    folio = ('000000'+str(Form.objects.filter(flow_id=1, parent_id=None).count()+1))[-4:]
    no_caso = "V{0}".format(folio)
    entryform.no_caso = no_caso
    entryform.save()
    form = Form.objects.create(
        content_object=entryform, flow=flow, state=flow.step_set.first().state)
    return redirect('/workflow/'+str(form.id))


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
        'edit': edit,
        'closed': 0
    })

def make_pdf_file(id, url):
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
            'margin-bottom': "10mm",
            'load-error-handling': "ignore",
            'disable-javascript': '',
            'footer-center': '[page]',
            # 'footer-html': 'www.google.com'
        }

    urlsitio = settings.SITE_URL + url + str(id)
    print(urlsitio)
    pdf = pdfkit.from_url(urlsitio, False, options=options)
    return pdf

@login_required
def download_report(request, id):
    form = Form.objects.get(pk=id)
    entryform_id = form.content_object.id
    pdf = make_pdf_file(entryform_id, '/template-report/')
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe.pdf"'

    return response

def template_report(request, id):
    analisis = AnalysisForm.objects.get(id=int(id))
    report = Report.objects.filter(analysis_id=int(id))
    report_final = ReportFinal.objects.filter(analysis_id=int(id)).last()
    return render(request, 'app/template_report.html',{'analisis': analisis, 'report': report, 'report_final':report_final })

def download_resumen_report(request, id):
    form = Form.objects.get(pk=id)
    entryform_id = form.content_object.id
    pdf = make_pdf_file(entryform_id, '/template-resumen-report/')
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe.pdf"'

    return response

def template_resumen_report(request, id):
    entryform = EntryForm.objects.values().get(pk=id)
    entryform_object = EntryForm.objects.get(pk=id)
    subflow = entryform_object.get_subflow
    entryform["subflow"] = subflow
    identifications = list(
        Identification.objects.filter(
            entryform=entryform['id']).values())
    
    samples = Sample.objects.filter(
            entryform=entryform['id']).order_by('index')
    
    samples_as_dict = []
    for s in samples:
        s_dict = model_to_dict(s, exclude=['organs', 'sampleexams', 'exams', 'identification'])
        organs = []
        sampleexams = s.sampleexams_set.all()
        sampleExa = {}
        for sE in sampleexams:
            try:
                sampleExa[sE.exam_id]['organ_id'].append({
                    'name':sE.organ.name,
                    'id':sE.organ.id})
            except:
                sampleExa[sE.exam_id]={
                    'exam_id': sE.exam_id,
                    'exam_name': sE.exam.name,
                    'exam_type': sE.exam.exam_type,
                    'sample_id': sE.sample_id,
                    'organ_id': [{
                    'name':sE.organ.name,
                    'id':sE.organ.id}]
                }
            if sE.exam.exam_type == 1:
                try:
                    organs.index(model_to_dict(sE.organ))
                except:
                    organs.append(model_to_dict(sE.organ))
        cassettes = Cassette.objects.filter(sample=s)
        s_dict['organs_set'] = organs
        s_dict['sample_exams_set'] = sampleExa
        cassettes_set = []
        for c in cassettes:
            cassettes_set.append({
                'cassette_name': c.cassette_name,
                'entryform_id': c.entryform_id,
                'id': c.id,
                'index': c.index,
                'sample_id': c.sample_id,
                'organs_set': list(c.organs.values())
            })
        s_dict['cassettes_set'] = cassettes_set
        s_dict['identification'] = model_to_dict(s.identification, exclude=["organs",])
        samples_as_dict.append(s_dict)

    entryform["identifications"] = []
    for ident in entryform_object.identification_set.all():
        ident_json = model_to_dict(ident, exclude=["organs"])
        ident_json['organs_set'] = list(ident.organs.all().values())
        entryform["identifications"].append(ident_json)              

    entryform["analyses"] = list(
        entryform_object.analysisform_set.all().values('id', 'created_at', 'comments', 'entryform_id', 'exam_id', 'exam__name', 'patologo_id', 'patologo__first_name', 'patologo__last_name'))
    entryform["cassettes"] = list(
        entryform_object.cassette_set.all().values())
    entryform["customer"] = model_to_dict(entryform_object.customer) if entryform_object.customer else None
    entryform["larvalstage"] = model_to_dict(entryform_object.larvalstage) if entryform_object.larvalstage else None
    entryform["fixative"] = model_to_dict(entryform_object.fixative) if entryform_object.fixative else None
    entryform["watersource"] = model_to_dict(entryform_object.watersource) if entryform_object.watersource else None
    entryform["specie"] = model_to_dict(entryform_object.specie) if entryform_object.specie else None

    exams_set = list(Exam.objects.all().values())
    organs_set = list(Organ.objects.all().values())

    species_list = list(Specie.objects.all().values())
    larvalStages_list = list(LarvalStage.objects.all().values())
    fixtatives_list = list(Fixative.objects.all().values())
    waterSources_list = list(WaterSource.objects.all().values())
    customers_list = list(Customer.objects.all().values())
    patologos = list(User.objects.filter(userprofile__profile_id__in=[4, 5]).values())
    data = {
        'entryform': entryform,
        'identifications': identifications,
        'samples': samples_as_dict,
        'exams': exams_set,
        'organs': organs_set,
        'species_list': species_list,
        'larvalStages_list': larvalStages_list,
        'fixtatives_list': fixtatives_list,
        'waterSources_list': waterSources_list,
        'customers_list': customers_list,
        'patologos': patologos
    }

    return render(request, 'app/template_resumen_report.html', data)

def sortReport(report):
    return report.organ_id

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
        first_column = [["MUESTRA / HALLAZGO", 1], ""]
        first_column = first_column + list(map(lambda x: x.identification.cage+"-"+x.identification.group+"-"+str(x.index), samples))
        matrix.append(first_column + [""])
        
        res2 = defaultdict(list)
        value.sort(key=sortReport)
        for elem in value:
            res2[elem.pathology.name + " en " + elem.organ_location.name].append(elem)
        
        lastOrgan = ''
        for key2, value2 in res2.items():
            if lastOrgan == value2[0].organ.name:
                column = [['', 1], key2]
                for col in matrix:
                    if col[0][0] == lastOrgan:
                        col[0][1] = col[0][1] + 1
                        break
            else:
                lastOrgan = value2[0].organ.name
                column = [[value2[0].organ.name, 1], key2]
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

# @login_required
def notification(request):
    ctx = {
        'name': "Name s",
        'nro_caso': "caso",
        'etapa_last': 'current_state',
        'etapa_current': 'next_state',
        'url': 'settings.SITE_URL++str(form.id)++next_state.step.tag'
    }
        
    return render(request, 'app/notification.html', ctx)

@login_required
def show_patologos(request):
    up = UserProfile.objects.filter(user=request.user).first()
    analysis = AnalysisForm.objects.all()
    data = []
    patologos = list(User.objects.filter(userprofile__profile_id__in=[4, 5]).values())

    for a in analysis:
        if not a.entryform.forms.first().deleted:
            parte = a.entryform.get_subflow
            
            if parte == "N/A":
                parte = ''
            else:
                parte = ' (Parte ' + parte + ')'
            if up.profile.id != 5 or a.patologo_id == request.user.id:
                data.append({
                    'analisis': a.id,
                    'patologo': a.patologo_id,
                    'closed': a.entryform.forms.first().form_closed,
                    'edit': not a.entryform.forms.first().form_closed and up.profile.id == 1,
                    'no_caso': a.entryform.no_caso + parte, 
                    'exam': a.exam.name
                })
    return render(request, 'app/patologos.html', {'casos': data, 'patologos': patologos})

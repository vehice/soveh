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
from django.conf import settings

from django.db.models import Q

import datetime
import json

@login_required
def home(request):
    services = Exam.objects.values('id', 'name')
    dates = EntryForm.objects.all().values_list('created_at', flat = True).order_by('-created_at').distinct()
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
        WHERE f.flow_id = 1 AND f.cancelled = 0
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

    form = Form.objects.filter(content_type__model='entryform').order_by('-object_id')
    if up.profile_id in (4,5):
        ids = EntryForm.objects.filter(analysisform__patologo_id=up.user_id).values_list('id')
        form_ids = form.filter(object_id__in=ids).values_list('id')
        state_ids = Form.objects.filter(content_type__model='analysisform', parent_id__in=form_ids).values_list('parent_id')
        form = form.filter(id__in=state_ids)

    return render(request, 'app/ingresos.html', {'entryForm_list': form, 'edit': editar, 'eliminar': eliminar })


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
    entryform = EntryForm.objects.create(created_by=request.user)
    no_caso_initial = 3795
    folio = ('000000'+str(Form.objects.filter(flow_id=1, parent_id=None).count()+no_caso_initial))[-4:]
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
    pdf = pdfkit.from_url(urlsitio, False, options=options)
    return pdf

def make_pdf_file2(id, url, filename, userId):
    import pdfkit
    import os

    d = datetime.datetime.today().strftime("%Y%m%d%H%M%S")

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

    if settings.DEBUG:
        file_path = settings.BASE_DIR + settings.MEDIA_URL + "pdfs/" + filename
    else:
        file_path = settings.MEDIA_ROOT + "/pdfs/" + filename

    # print (file_path)
    urlsitio = settings.SITE_URL + url + str(id) + '/' + str(userId)
    print (urlsitio)
    pdfkit.from_url(urlsitio, file_path, options=options)

@login_required
def download_report(request, id):
    pdf = make_pdf_file(id, '/template-report/')
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe.pdf"'

    return response

def template_report(request, id):
    analisis = AnalysisForm.objects.get(id=int(id))
    report = Report.objects.filter(analysis_id=int(id))
    report_final = ReportFinal.objects.filter(analysis_id=int(id)).last()
    return render(request, 'app/template_report.html',{'analisis': analisis, 'report': report, 'report_final':report_final })

def get_resume_file(user, formId, lang):
    form = Form.objects.get(pk=formId)
    entryForm = EntryForm.objects.get(id=form.content_object.id)
    last_case_version = CaseVersion.objects.filter(
        entryform=entryForm).order_by('-generated_at').first()

    lang_option = 1
    for n, l in RESUME_DOCUMENT_LANG:
        if l == lang:
            lang_option = n
    last_doc = DocumentCaseResume.objects.filter(
        entryform=entryForm,
    ).order_by('-created_at').first()

    doc_final = None

    # Primero valido si existe un documento que este al dia con la version del caso, si no existe entonce si o si creo un documento nuevo
    if last_doc:
        if last_doc.case_version.version < last_case_version.version:
            # Caso desactualizado, se debe crear uno nuevo si o si porque aun nadie ha creado un documento con la ultima version del caso
            new_version = last_doc.version + 1
            file_base_name = "Resumen_"+str(entryForm.no_caso)+"_"+lang.upper()+"_v"+str(new_version)+"_"+str(int(datetime.datetime.now().timestamp()))+".pdf"
            file_name = "Resumen_"+str(entryForm.no_caso)+"_"+lang.upper()+"_v"+str(new_version)+".pdf"

            doc_final = DocumentCaseResume.objects.create(
                entryform=entryForm,
                filename=file_name,
                file=file_base_name,
                lang=lang_option,
                case_version=last_case_version,
                version=new_version,
                generated_by=user
            )
            make_pdf_file2(entryForm.pk, "/template-resumen-report/", file_base_name, user.pk)

        else:
            # Caso actualizado, se debe verificar si existe un documento del usuario generado con la ultima version y con el lenguaje solicitado
            temp_doc = DocumentCaseResume.objects.filter(
                entryform=entryForm,
                generated_by=user,
                lang=lang_option,
                case_version=last_case_version,
                version=last_doc.version
            ).first()
            if temp_doc:
                doc_final = temp_doc
            else:
                file_base_name = "Resumen_"+str(entryForm.no_caso)+"_"+lang.upper()+"_v"+str(last_doc.version)+"_"+str(int(datetime.datetime.now().timestamp()))+".pdf"
                file_name = "Resumen_"+str(entryForm.no_caso)+"_"+lang.upper()+"_v"+str(last_doc.version)+".pdf"
                doc_final = DocumentCaseResume.objects.create(
                    entryform=entryForm,
                    filename=file_name,
                    file=file_base_name,
                    lang=lang_option,
                    case_version=last_case_version,
                    version=last_doc.version,
                    generated_by=user
                )
                make_pdf_file2(entryForm.pk, "/template-resumen-report/", file_base_name, user.pk)
    else:
        # Creo el primer documento del caso
        file_base_name = "Resumen_"+str(entryForm.no_caso)+"_"+lang.upper()+"_v1_"+str(int(datetime.datetime.now().timestamp()))+".pdf"

        file_name = "Resumen_"+str(entryForm.no_caso)+"_"+lang.upper()+"_v1.pdf"

        if not last_case_version:
            last_case_version = CaseVersion.objects.create(
                entryform_id = entryForm.id,
                version = 1,
                generated_by_id = user.pk
            )

        doc_final = DocumentCaseResume.objects.create(
            entryform=entryForm,
            filename=file_name,
            file=file_base_name,
            lang=lang_option,
            case_version=last_case_version,
            version=1,
            generated_by=user
        )

        make_pdf_file2(entryForm.pk, "/template-resumen-report/", file_base_name, user.pk)


    return doc_final

def download_resumen_report(request, id):

    var_get = request.GET.copy()
    lang = var_get.get('lang', 'es')

    doc_final = get_resume_file(request.user, id, lang)

    DocumentResumeActionLog.objects.create(
        document=doc_final,
        download_action=True,
        done_by=request.user
    )

    if settings.DEBUG:
        file_path = settings.BASE_DIR + settings.MEDIA_URL + "pdfs/"
    else:
        file_path = settings.MEDIA_ROOT + "/pdfs/"

    with open(file_path + "" + str(doc_final.file), 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename='+str(doc_final.filename)
        return response

def show_log_actions(request, id):
    from django.http import JsonResponse
    actions = DocumentResumeActionLog.objects.filter(document__entryform_id=id)
    action_list = []

    for action in actions:
        action_dict = {}
        action_dict['done_by'] = action.done_by.get_full_name().title()
        type_v = ""
        if action.mail_action:
            type_v = "Envío por Mail"
        else:
            type_v = "Descarga Directa"
        action_dict['type'] = type_v
        action_dict['version'] = action.document.version
        action_dict['action_date'] = action.action_date.strftime('%d/%m/%Y %H:%M')
        action_list.append(action_dict)
    return JsonResponse({'ok': True, 'data': action_list})

def template_resumen_report(request, id, userId):
    entryform = EntryForm.objects.values().get(pk=id)
    entryform_object = EntryForm.objects.get(pk=id)
    
    doc = DocumentCaseResume.objects.filter(
        entryform=entryform_object,
        generated_by_id=userId
    ).order_by('-created_at').first()

    doc_data = model_to_dict(doc)
    # print (doc_data)

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
                a_form = entryform_object.analysisform_set.filter(exam_id=sE.exam_id).first().forms.get()
                is_cancelled = a_form.cancelled
                is_closed = a_form.form_closed
            except:
                is_cancelled = False
                is_closed = False
            
            if not is_cancelled:
                try:
                    sampleExa[sE.exam_id]['organ_id'].append({
                        'name':sE.organ.name,
                        'id':sE.organ.id})
                except:
                    sampleExa[sE.exam_id]={
                        'exam_id': sE.exam_id,
                        'exam_name': sE.exam.name,
                        'exam_type': sE.exam.service_id,
                        'sample_id': sE.sample_id,
                        'organ_id': [{
                        'name':sE.organ.name,
                        'id':sE.organ.id}]
                    }
                if sE.exam.service_id == 1:
                    try:
                        organs.index(model_to_dict(sE.organ))
                    except:
                        organs.append(model_to_dict(sE.organ))
        s_dict['organs_set'] = organs
        s_dict['sample_exams_set'] = sampleExa
        s_dict['identification'] = model_to_dict(s.identification, exclude=["organs", 'organs_before_validations'])
        samples_as_dict.append(s_dict)

    entryform["identifications"] = []
    for ident in entryform_object.identification_set.all():
        ident_json = model_to_dict(ident, exclude=["organs", 'organs_before_validations'])
        ident_json['organs_set'] = list(ident.organs.all().values())
        entryform["identifications"].append(ident_json)              

    entryform["analyses"] = list(
        entryform_object.analysisform_set.filter(exam__isnull=False).values('id', 'created_at', 'comments', 'entryform_id', 'exam_id', 'exam__name', 'patologo_id', 'patologo__first_name', 'patologo__last_name'))
    entryform["cassettes"] = list(
        entryform_object.cassette_set.all().values())
    entryform["customer"] = model_to_dict(entryform_object.customer) if entryform_object.customer else None
    entryform["larvalstage"] = model_to_dict(entryform_object.larvalstage) if entryform_object.larvalstage else None
    entryform["fixative"] = model_to_dict(entryform_object.fixative) if entryform_object.fixative else None
    entryform["watersource"] = model_to_dict(entryform_object.watersource) if entryform_object.watersource else None
    entryform["specie"] = model_to_dict(entryform_object.specie) if entryform_object.specie else None

    patologos = list(User.objects.filter(userprofile__profile_id__in=[4, 5]).values())

    for item in entryform['identifications']:
        servicios = {}
        for item2 in samples_as_dict:
            if item2['identification']['id'] == item['id']:
                for key, value in item2['sample_exams_set'].items():
                    if value['exam_name'] in servicios:
                        for aux in value['organ_id']:
                            servicios[value['exam_name']].append(aux['name'])
                    else:
                        servicios[value['exam_name']] = []
                        for aux in value['organ_id']:
                            servicios[value['exam_name']].append(aux['name'])

        serv = {}
        for key, value in servicios.items():
            organs = {}
            for k in value:
                if k in organs:
                    organs[k] += 1
                else:
                    organs[k] = 1
            if key in serv:
                serv[key].append(organs)
            else:
                serv[key] = [organs]
        
        item['servicios'] = serv
                
    data = {
        'doc_data': doc,
        'entryform': entryform,
        'identifications': identifications,
        'case_created_by': User.objects.get(pk=entryform['created_by_id']).get_full_name(),
        'report_generated_by': User.objects.get(pk=userId).get_full_name(),
        'patologos': patologos
    }

    if doc.lang == 1:
        return render(request, 'app/template_resumen_report_es.html', data)
    elif doc.lang == 2:
        return render(request, 'app/template_resumen_report_en.html', data)
    else:
        return render(request, 'app/template_resumen_report_es.html', data)

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

        # print (matrix)
        
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
                    samples_by_index[item.sample.index].append(item.diagnostic_intensity.name)

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
        # print (data)
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
def show_patologos(request, all):
    up = UserProfile.objects.filter(user=request.user).first()
    if request.user.is_superuser or up.profile_id in (1,2,3):
        analysis = AnalysisForm.objects.filter(exam__isnull=False).select_related("entryform", "exam").order_by('-entryform_id')
    elif up.profile_id in (4,5):
        analysis = AnalysisForm.objects.filter(patologo=request.user, exam__isnull=False).select_related("entryform", "exam").order_by('-entryform_id')
    else:
        analysis = AnalysisForm.objects.filter(exam__isnull=False).select_related("entryform", "exam").order_by('-entryform_id')

    data = []
    patologos = list(User.objects.filter(Q(userprofile__profile_id__in=[4, 5]) | Q(userprofile__is_pathologist=True)).values())
    editar = up.profile_id in (1,2,3)

    selected_analysis = []

    for a in analysis:
        entryform_form = a.entryform.forms.first()
        analysisform_form = a.forms.first()

        if int(all):
            if not entryform_form.cancelled and a.exam.pathologists_assignment and not analysisform_form.cancelled:
                selected_analysis.append({'analysis': a, 'entryform_form': entryform_form, 'analysisform_form': analysisform_form})   
        else:
            if not entryform_form.cancelled and a.exam.pathologists_assignment and not analysisform_form.cancelled and not entryform_form.form_closed:
                selected_analysis.append({'analysis': a, 'entryform_form': entryform_form, 'analysisform_form': analysisform_form})  

    for a in selected_analysis:
        days_open = 0
        days_late = 0
        if not a['analysisform_form'].form_closed:
            # Analisis en curso

            current_date = datetime.datetime.now()
            if a['analysis'].assignment_deadline:
                if a['analysis'].pre_report_started and a['analysis'].pre_report_ended:
                    days_late = (a['analysis'].pre_report_ended_at - a['analysis'].assignment_deadline).days
                elif current_date > a['analysis'].assignment_deadline:
                    days_late = (current_date - a['analysis'].assignment_deadline).days

            days_open = (current_date - a['analysis'].created_at).days
        else:
            # Analisis cerrado
            if a['analysis'].assignment_deadline and a['analysis'].pre_report_ended_at:
                if a['analysis'].pre_report_ended_at > a['analysis'].assignment_deadline:
                    days_late = (a['analysis'].pre_report_ended_at - a['analysis'].assignment_deadline).days

            if a['analysis'].manual_closing_date:
                days_open = (a['analysis'].manual_closing_date - a['analysis'].created_at).days
            else:
                days_open = (a['analysisform_form'].closed_at - a['analysis'].created_at).days
        samples = Sample.objects.filter(entryform=a['analysis'].entryform).values_list('id', flat=True)
        sampleExams_counter = 0
        sampleExams = SampleExams.objects.filter(sample__in=samples, exam=a['analysis'].exam).select_related("organ")
        organ_types = []
        for se in sampleExams:
            sampleExams_counter += 1
            if se.organ.organ_type not in organ_types:
                organ_types.append(se.organ.organ_type)
        organ_types = set(organ_types)
        unit = ""
        if len(organ_types) > 1:
            unit = "Multiple"
        elif len(organ_types) == 1:
            if list(organ_types)[0] == 1:
                unit = "Órgano"
            else:
                unit = sampleExams.first().organ.name
        else:
            unit = "Órgano"

        parte = a['analysis'].entryform.get_subflow
        if parte == "N/A":
            parte = ''
        else:
            parte = ' (Parte ' + parte + ')'

        data.append({
            'analisis': a['analysis'].id,
            'patologo': a['analysis'].patologo_id if a['analysis'].patologo else None,
            'patologo_name': a['analysis'].patologo.first_name +" "+a['analysis'].patologo.last_name if a['analysis'].patologo else "No Asignado",
            'closed': 1 if a['analysisform_form'].form_closed else 0,
            'cancelled': 1 if a['analysisform_form'].cancelled else 0,
            'edit': not a['entryform_form'].form_closed and not a['analysisform_form']. form_closed and up.profile.id == 1,
            'no_caso': a['analysis'].entryform.no_caso + parte, 
            'exam': a['analysis'].exam.name,
            'cliente': a['analysis'].entryform.customer.name,
            'centro': a['analysis'].entryform.center,
            'fecha_ingreso': a['analysis'].created_at.strftime("%d/%m/%Y"),
            'dias_abierto': days_open,
            'nro_organos': sampleExams_counter,
            'entryform': a['analysis'].entryform.id,
            'entryform_form_closed': a['entryform_form'].form_closed,
            'entryform_cancelled': a['entryform_form'].cancelled,
            'unidad': unit,
            'fecha_derivacion': a['analysis'].assignment_done_at.strftime("%d/%m/%Y") if a['analysis'].assignment_done_at else "",
            'fecha_plazo': a['analysis'].assignment_deadline.strftime("%d/%m/%Y") if a['analysis'].assignment_deadline else "",
            'dias_atraso': days_late,
            'estado': a['analysis'].status,
            'nota_diagnostico': str(a['analysis'].entryform.score_diagnostic).replace(",", ".") if a['analysis'].entryform.score_diagnostic else "",
            'nota_informe': str(a['analysis'].entryform.score_report).replace(",", ".") if a['analysis'].entryform.score_report else "",
        })

    return render(request, 'app/patologos.html', {'casos': data, 'patologos': patologos, 'edit': editar, 'all': all})

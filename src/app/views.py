import json
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Q
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View

from accounts.models import *
from backend.models import *
from utils import functions as fn
from workflows.models import *
from django.core.paginator import Paginator


@login_required
def home(request):
    """
    Display website homepage with a list of services and report data

    **Context**

    ``services``
        A list of :model:`backend.Service`
    ``years``
        A list of dates according to all :model:`backend.EntryForm`
    ``top_10``
        Count of last 10 :model:`backend.Exam`

    **Template**

    :template:`app/home.html`
    """
    services = Exam.objects.values("id", "name")
    dates = (
        EntryForm.objects.all()
        .values_list("created_at", flat=True)
        .order_by("-created_at")
        .distinct()
    )
    years = []
    for d in dates:
        if d and not d.year in years:
            years.append(d.year)
    cursor1 = connection.cursor()
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
    """
    )
    top_10 = cursor1.fetchmany(10)
    top_10 = json.dumps(top_10)
    return render(
        request,
        "app/home.html",
        {"services": services, "years": years, "top_10": top_10},
    )


@login_required
def show_users(request):
    """
    Display a listing of Users

    **Context**

    ``user_list``
        A list of :model:`auth.User`

    **Template**

    :template:`app/users.html`
    """
    users = User.objects.all()
    usuarios = []
    for usuario in users:
        aux = {
            "user": usuario.first_name.title() + " " + usuario.last_name.title(),
            "email": usuario.email,
            "id": usuario.id,
            "estado": usuario.is_active,
            "admin": usuario.is_superuser,
        }
        usuarios.append(aux)
    return render(request, "app/users.html", {"user_list": usuarios})


@login_required
def show_clientes(request):
    """
    Display a listing of Customer

    **Context**

    ``customer_list``
        A list of :model:`backend.Customer`

    **Template**

    :template:`app/clientes.html`
    """
    customers = Customer.objects.all()
    return render(request, "app/clientes.html", {"customer_list": customers})


@login_required
def show_analisis(request):
    """
    Display a listing of Exam

    **Context**

    ``exam_list``
        A list of :model:`backend.Exam`

    **Template**

    :template:`app/analisis.html`
    """
    exams = Exam.objects.all()
    return render(request, "app/analisis.html", {"exam_list": exams})


@login_required
def show_ingresos(request):
    """
    Display a listing of EntryForm

    **Context**

    ``entryForm_list``
        A list of :model:`backend.EntryForm`
    ``edit``
        A boolean value to check if the current user can or cannot edit EntryForms
    ``eliminar``
        A boolean value to check if the current user can or cannot delete EntryForms

    **Template**

    :template:`app/ingresos.html`
    """
    up = UserProfile.objects.filter(user=request.user).first()
    editar = up.profile_id in (1, 3) or request.user.is_superuser
    eliminar = request.user.is_superuser
    check_forms = Form.objects.filter(content_type__model="entryform", state__id=1)

    return render(
        request,
        "app/ingresos.html",
        {"edit": editar, "eliminar": eliminar},
    )


@login_required
def tabla_ingresos(request):
    up = UserProfile.objects.filter(user=request.user).first()
    form = Form.objects.filter(content_type__model="entryform").order_by("-object_id")

    draw = int(request.GET.get("draw"))
    length = int(request.GET.get("length"))
    search = request.GET.get("search[value]")
    start = int(request.GET.get("start")) + 1

    if up.profile_id in (4, 5):
        assigned_areas = UserArea.objects.filter(user=request.user, role=0)
        pks = [request.user.id]

        for user_area in assigned_areas:
            users = (
                UserArea.objects.filter(area=user_area.area)
                .exclude(user=request.user)
                .values_list("user", flat=True)
            )
            pks.extend(users)

        pathologists = User.objects.filter(
            Q(userprofile__profile_id__in=(4, 5)) | Q(userprofile__is_pathologist=True)
        ).filter(pk__in=pks)

        ids = EntryForm.objects.filter(
            analysisform__patologo_id__in=pathologists
        ).values_list("id")
        form_ids = form.filter(object_id__in=ids).values_list("id")
        state_ids = Form.objects.filter(
            content_type__model="analysisform", parent_id__in=form_ids
        ).values_list("parent_id")
        form = form.filter(id__in=state_ids)

    if search:
        cases = EntryForm.objects.filter(
            Q(pk__in=form.values_list("object_id", flat=True)),
            Q(no_caso__icontains=search)
            | Q(customer__name__icontains=search)
            | Q(center__icontains=search)
            | Q(no_request__icontains=search)
            | Q(created_at__icontains=search),
        )

        form = form.filter(object_id__in=cases.values_list("id", flat=True))

    form_paginator = Paginator(form, length)

    context = {
        "draw": draw + 1,
        "recordsTotal": form_paginator.count,
        "recordsFiltered": form_paginator.count,
        "data": [],
    }

    for page in form_paginator.page_range:
        page_start = form_paginator.get_page(page).start_index()
        if page_start == start:
            form_page = form_paginator.get_page(page).object_list
            for form in form_page:
                row = {
                    "DT_RowId": f"form-{form.pk}",
                    "case": model_to_dict(
                        form.content_object,
                        fields=[
                            "id",
                            "no_request",
                            "no_caso",
                            "center",
                            "customer",
                            "created_at",
                        ],
                    ),
                    "form": model_to_dict(form),
                    "step": model_to_dict(form.state.step, fields=["name", "tag"]),
                }

                # If no customer is assigned to the entryform
                if form.content_object.customer:
                    row.update(
                        {"customer": model_to_dict(form.content_object.customer)}
                    )

                # Get current analysis progress for the entryform

                analysis_pk = form.content_object.analysisform_set.all().values_list(
                    "id", flat=True
                )
                analysis_forms = Form.objects.filter(
                    content_type__model="analysisform",
                    object_id__in=analysis_pk,
                    form_closed=False,
                    cancelled=False,
                )
                has_in_progress = analysis_forms.count() > 0

                row.update({"progress": has_in_progress})
                context["data"].append(row)

            break

    return JsonResponse(context)


@login_required
def show_estudios(request):
    """
    Display a listing of Research

    **Context**

    ``research_list``
        A list of :model:`backend.Research`
    ``edit``
        A boolean value to check if the current user can or cannot edit EntryForms
    ``eliminar``
        A boolean value to check if the current user can or cannot delete EntryForms

    **Template**

    :template:`app/ingresos.html`
    """
    up = UserProfile.objects.filter(user=request.user).first()
    editar = 1
    eliminar = editar and request.user.is_superuser
    estudios = Research.objects.all()
    clients_available = Customer.objects.all()
    users_available = User.objects.all()

    form = Form.objects.filter(content_type__model="entryform").order_by("-object_id")

    return render(
        request,
        "app/estudios.html",
        {
            "research_list": estudios,
            "can_edit": editar,
            "can_delete": eliminar,
            "clients_available": clients_available,
            "users_available": users_available,
        },
    )


@login_required
def show_ingresos_by_id(request, form_id):
    """
    Display a listing of Research

    **Context**

    ``research_list``
        A list of :model:`backend.Research`
    ``edit``
        A boolean value to check if the current user can or cannot edit EntryForms
    ``eliminar``
        A boolean value to check if the current user can or cannot delete EntryForms

    **Template**

    :template:`app/ingresos.html`
    """
    up = UserProfile.objects.filter(user=request.user).first()

    if up.user.is_staff:
        form = Form.objects.filter(content_type__model="entryform")
    else:
        form = Form.objects.filter(
            content_type__model="entryform", state__step__actors__profile=up.profile
        )

    return render(request, "app/ingresos.html", {"entryForm_list": form})


@login_required
def new_ingreso(request):
    """
    Creates a new :model:`backend.EntryForm` storing the current user and the case number which
    is generated from the count of all :model:`backend.Form` in the initial process with no Parent
    process.

    Redirects to :view:`workflows.flow`
    """
    flow = Flow.objects.get(pk=1)
    entryform = EntryForm.objects.create(created_by=request.user)
    no_caso_initial = 3795
    folio = (
        "000000"
        + str(Form.objects.filter(flow_id=1, parent_id=None).count() + no_caso_initial)
    )[-4:]
    no_caso = "V{0}".format(folio)
    entryform.no_caso = no_caso
    entryform.save()
    form = Form.objects.create(
        content_object=entryform, flow=flow, state=flow.step_set.first().state
    )
    return redirect("/workflow/" + str(form.id))


@login_required
def new_research(request):
    """
    Accepts POST request to create or update a :model:`backend.Research`
    if not id is given it will create a new Research, if an id is given then it will
    search for that Research and update it.
    """
    var_post = request.POST.copy()
    clients = var_post.getlist("clients", [])
    id = var_post.get("id", None)
    name = var_post.get("name")
    init_date = var_post.get("init_date")
    external_responsible = var_post.get("external_responsible")
    internal_responsible = var_post.get("internal_responsible")
    type = var_post.get("type")
    description = var_post.get("description")
    status = int(var_post.get("status"))

    if not id:
        start_counter_research = 59
        research_counter = Research.objects.count()
        next_code = str(start_counter_research + research_counter + 1)

        if len(next_code) == 2:
            code = "E00" + next_code
        elif len(next_code) == 3:
            code = "E0" + next_code
        else:
            code = "E" + next_code

        study = Research.objects.create(
            code=code,
            name=name,
            description=description,
            type=int(type),
            init_date=datetime.strptime(init_date, "%d/%m/%Y %H:%M"),
            status=status,
            external_responsible=external_responsible,
            internal_responsible_id=internal_responsible,
        )
        clients_obj = Customer.objects.filter(id__in=clients)
        for cl in clients_obj:
            study.clients.add(cl)

        return redirect("/research/" + str(study.id))
    else:
        study = Research.objects.get(pk=id)
        study.name = name
        study.description = description
        study.type = int(type)
        study.init_date = datetime.strptime(init_date, "%d/%m/%Y %H:%M")
        study.status = status
        study.external_responsible = external_responsible
        study.internal_responsible_id = internal_responsible
        study.save()

        # Quitando servicios de clientes eliminados
        for c in study.clients.all():
            if str(c.id) not in clients:
                for s in study.services.filter(entryform__customer_id=c):
                    study.services.remove(s)

        study.clients.clear()

        clients_obj = Customer.objects.filter(id__in=clients)
        for cl in clients_obj:
            study.clients.add(cl)

        return redirect("/research/" + str(study.pk))


@login_required
def show_workflow_main_form(request, form_id):
    """
    Display a resource form for :model:`workflow.Form`

    **Context**

    ``form``
        An instance of :model:`workflow.Form`
    ``form_id``
        A pk to a :model:`workflow.Form`
    ``entryform_id``
        A pk to a :model:`backend.EntryForm`
    ``edit``
        A boolean value that's true if the current User can edit the current Form
    ``edit_case``
        A boolean value that's true if the current User can edit the Form's Case

    **Template**

    :template:`app/workflow_main.html`
    """
    form = Form.objects.get(pk=form_id)
    entryform_id = form.content_object.id
    up = UserProfile.objects.filter(user=request.user).first()
    edit_case = not form.form_closed and (
        up.profile.id in (1, 2, 3) or request.user.is_superuser
    )
    actor = Actor.objects.filter(profile_id=request.user.userprofile.profile_id).first()
    edit = (
        1
        if actor.permission.filter(from_state_id=1, type_permission="w").first()
        else 0
    )
    if not edit:
        return show_ingresos(request)

    return render(
        request,
        "app/workflow_main.html",
        {
            "form": form,
            "form_id": form_id,
            "entryform_id": entryform_id,
            "edit": edit,
            "closed": 0,
            "edit_case": edit_case,
        },
    )


def make_pdf_file(id, url):
    import os

    import pdfkit
    from django.conf import settings

    d = datetime.today().strftime("%Y%m%d%H%M%S")
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    options = {
        "quiet": "",
        "page-size": "A4",
        "encoding": "UTF-8",
        "margin-top": "5mm",
        "margin-left": "5mm",
        "margin-right": "5mm",
        "margin-bottom": "10mm",
        "load-error-handling": "ignore",
        "disable-javascript": "",
        "footer-center": "[page]",
        # 'footer-html': 'www.google.com'
    }

    urlsitio = settings.SITE_URL + url + str(id)
    pdf = pdfkit.from_url(urlsitio, False, options=options)
    return pdf


def make_pdf_file2(id, url, filename, userId):
    import pdfkit

    d = datetime.today().strftime("%Y%m%d%H%M%S")

    options = {
        "quiet": "",
        "page-size": "A4",
        "encoding": "UTF-8",
        "margin-top": "5mm",
        "margin-left": "5mm",
        "margin-right": "5mm",
        "margin-bottom": "10mm",
        "load-error-handling": "ignore",
        "disable-javascript": "",
        "footer-center": "[page]",
        # 'footer-html': 'www.google.com'
    }

    if settings.DEBUG:
        file_path = settings.BASE_DIR + settings.MEDIA_URL + "pdfs/" + filename
    else:
        file_path = settings.MEDIA_ROOT + "/pdfs/" + filename

    # print (file_path)
    urlsitio = settings.SITE_URL + url + str(id) + "/" + str(userId)
    pdfkit.from_url(urlsitio, file_path, options=options)


@login_required
def download_report(request, id):
    """
    Creates a PDF file from a template, and generates a file download for it
    """
    pdf = make_pdf_file(id, "/template-report/")
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="informe.pdf"'

    return response


def template_report(request, id):
    """
    Generates the template to be converted to PDF and downloaded

    **Parameters**
    ``id``
        A pk to an instance of :model:`backend.AnalysisForm`

    **Context**

    ``analisis``
        An instance of :model:`backend.AnalysisForm`
    ``report``
        A list of :model:`backend.Report` related to the :model:`backend.AnalysisForm`
    ``report_final``
        The last item for :model:`backend.ReportFinal` related to the :model:`backend.AnalysisForm`

    **Template**

    :template:`app/template_report.html`
    """
    analisis = AnalysisForm.objects.get(id=int(id))
    report = Report.objects.filter(analysis_id=int(id))
    report_final = ReportFinal.objects.filter(analysis_id=int(id)).last()
    return render(
        request,
        "app/template_report.html",
        {"analisis": analisis, "report": report, "report_final": report_final},
    )


@login_required
def download_reception(request, id):
    """Generates a PDF file for a Reception form to be downloaded"""
    pdf = make_pdf_file("{0}/{1}".format(id, request.user.id), "/template-reception/")
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="comprobante.pdf"'

    return response


def get_resume_file(user, formId, lang):
    """Return the pdf file with an overview of the current state of a :model:`backend.AnalysisForm`"""
    form = Form.objects.get(pk=formId)
    entryForm = EntryForm.objects.get(id=form.content_object.id)
    last_case_version = (
        CaseVersion.objects.filter(entryform=entryForm)
        .order_by("-generated_at")
        .first()
    )

    lang_option = 1
    for n, l in RESUME_DOCUMENT_LANG:
        if l == lang:
            lang_option = n
    last_doc = (
        DocumentCaseResume.objects.filter(
            entryform=entryForm,
        )
        .order_by("-created_at")
        .first()
    )

    doc_final = None

    # Primero valido si existe un documento que este al dia con la version del caso,
    # si no existe entonce si o si creo un documento nuevo
    if last_doc:
        if last_doc.case_version.version < last_case_version.version:
            # Caso desactualizado, se debe crear uno nuevo si o si
            # porque aun nadie ha creado un documento con la ultima version del caso
            new_version = last_doc.version + 1
            file_base_name = (
                "Resumen_"
                + str(entryForm.no_caso)
                + "_"
                + lang.upper()
                + "_v"
                + str(new_version)
                + "_"
                + str(int(datetime.now().timestamp()))
                + ".pdf"
            )
            file_name = (
                "Resumen_"
                + str(entryForm.no_caso)
                + "_"
                + lang.upper()
                + "_v"
                + str(new_version)
                + ".pdf"
            )

            doc_final = DocumentCaseResume.objects.create(
                entryform=entryForm,
                filename=file_name,
                file=file_base_name,
                lang=lang_option,
                case_version=last_case_version,
                version=new_version,
                generated_by=user,
            )
            make_pdf_file2(
                entryForm.pk, "/template-resumen-report/", file_base_name, user.pk
            )

        else:
            # Caso actualizado, se debe verificar si existe un documento
            # del usuario generado con la ultima version y con el lenguaje solicitado
            temp_doc = DocumentCaseResume.objects.filter(
                entryform=entryForm,
                generated_by=user,
                lang=lang_option,
                case_version=last_case_version,
                version=last_doc.version,
            ).first()
            if temp_doc:
                doc_final = temp_doc
            else:
                file_base_name = (
                    "Resumen_"
                    + str(entryForm.no_caso)
                    + "_"
                    + lang.upper()
                    + "_v"
                    + str(last_doc.version)
                    + "_"
                    + str(int(datetime.now().timestamp()))
                    + ".pdf"
                )
                file_name = (
                    "Resumen_"
                    + str(entryForm.no_caso)
                    + "_"
                    + lang.upper()
                    + "_v"
                    + str(last_doc.version)
                    + ".pdf"
                )
                doc_final = DocumentCaseResume.objects.create(
                    entryform=entryForm,
                    filename=file_name,
                    file=file_base_name,
                    lang=lang_option,
                    case_version=last_case_version,
                    version=last_doc.version,
                    generated_by=user,
                )
                make_pdf_file2(
                    entryForm.pk, "/template-resumen-report/", file_base_name, user.pk
                )
    else:
        # Creo el primer documento del caso
        file_base_name = (
            "Resumen_"
            + str(entryForm.no_caso)
            + "_"
            + lang.upper()
            + "_v1_"
            + str(int(datetime.now().timestamp()))
            + ".pdf"
        )

        file_name = "Resumen_" + str(entryForm.no_caso) + "_" + lang.upper() + "_v1.pdf"

        if not last_case_version:
            last_case_version = CaseVersion.objects.create(
                entryform_id=entryForm.id, version=1, generated_by_id=user.pk
            )

        doc_final = DocumentCaseResume.objects.create(
            entryform=entryForm,
            filename=file_name,
            file=file_base_name,
            lang=lang_option,
            case_version=last_case_version,
            version=1,
            generated_by=user,
        )

        make_pdf_file2(
            entryForm.pk, "/template-resumen-report/", file_base_name, user.pk
        )

    return doc_final


def download_resumen_report(request, id):
    """Downloads a PDF file for a :model:`backend.AnalysisForm` resume"""
    var_get = request.GET.copy()
    lang = var_get.get("lang", "es")

    doc_final = get_resume_file(request.user, id, lang)

    DocumentResumeActionLog.objects.create(
        document=doc_final, download_action=True, done_by=request.user
    )

    if settings.DEBUG:
        file_path = settings.BASE_DIR + settings.MEDIA_URL + "pdfs/"
    else:
        file_path = settings.MEDIA_ROOT + "/pdfs/"

    with open(file_path + "" + str(doc_final.file), "rb") as pdf:
        response = HttpResponse(pdf.read(), content_type="application/pdf")
        response["Content-Disposition"] = "inline;filename=" + str(doc_final.filename)
        return response


def show_log_actions(request, id):
    from django.http import JsonResponse

    actions = DocumentResumeActionLog.objects.filter(document__entryform_id=id)
    action_list = []

    for action in actions:
        action_dict = {}
        action_dict["done_by"] = action.done_by.get_full_name().title()
        type_v = ""
        if action.mail_action:
            type_v = "Envío por Mail"
        else:
            type_v = "Descarga Directa"
        action_dict["type"] = type_v
        action_dict["version"] = action.document.version
        action_dict["action_date"] = action.action_date.strftime("%d/%m/%Y %H:%M")
        action_list.append(action_dict)
    return JsonResponse({"ok": True, "data": action_list})


def template_reception(request, id, userId):
    entryform = EntryForm.objects.values().get(pk=id)
    entryform_object = EntryForm.objects.get(pk=id)

    subflow = entryform_object.get_subflow
    entryform["subflow"] = subflow
    identifications = list(
        Identification.objects.filter(entryform=entryform["id"]).values()
    )

    samples = Sample.objects.filter(entryform=entryform["id"]).order_by("index")
    entryform["entryform_type"] = (
        entryform_object.entryform_type.name if entryform_object.entryform_type else ""
    )
    entryform["entry_format"] = (
        entryform_object.get_entry_format_display
        if entryform_object.entry_format
        else ""
    )
    samples_as_dict = []
    for s in samples:
        s_dict = model_to_dict(
            s, exclude=["organs", "sampleexams", "exams", "identification"]
        )
        organs = []
        sampleexams = s.sampleexams_set.all()
        sampleExa = {}

        for sE in sampleexams:
            analysis_form = entryform_object.analysisform_set.filter(
                exam_id=sE.exam_id
            ).first()
            try:
                a_form = analysis_form.forms.get()
                is_cancelled = a_form.cancelled
                is_closed = a_form.form_closed
            except:
                is_cancelled = False
                is_closed = False

            if not is_cancelled:
                try:
                    sampleExa[sE.exam_id]["organ_id"].append(
                        {"name": sE.organ.name, "id": sE.organ.id}
                    )
                except:
                    sampleExa[sE.exam_id] = {
                        "exam_id": sE.exam_id,
                        "exam_name": sE.exam.name,
                        "exam_type": sE.exam.service_id,
                        "stain": sE.stain.abbreviation.upper() if sE.stain else "N/A",
                        "sample_id": sE.sample_id,
                        "organ_id": [{"name": sE.organ.name, "id": sE.organ.id}],
                    }
                if sE.exam.service_id == 1:
                    try:
                        organs.index(model_to_dict(sE.organ))
                    except:
                        organs.append(model_to_dict(sE.organ))
        s_dict["organs_set"] = organs
        s_dict["sample_exams_set"] = sampleExa
        s_dict["identification"] = model_to_dict(
            s.identification, exclude=["organs", "organs_before_validations"]
        )
        samples_as_dict.append(s_dict)

    entryform["identifications"] = []
    for ident in entryform_object.identification_set.all():
        ident_json = model_to_dict(
            ident, exclude=["organs", "organs_before_validations"]
        )
        ident_json["organs_set"] = list(ident.organs.all().values())
        entryform["identifications"].append(ident_json)

    entryform["analyses"] = list(
        entryform_object.analysisform_set.filter(exam__isnull=False).values(
            "id",
            "created_at",
            "comments",
            "entryform_id",
            "exam_id",
            "exam__name",
            "patologo_id",
            "patologo__first_name",
            "patologo__last_name",
        )
    )
    entryform["cassettes"] = list(entryform_object.cassette_set.all().values())
    entryform["customer"] = (
        model_to_dict(entryform_object.customer) if entryform_object.customer else None
    )
    entryform["larvalstage"] = (
        model_to_dict(entryform_object.larvalstage)
        if entryform_object.larvalstage
        else None
    )
    entryform["fixative"] = (
        model_to_dict(entryform_object.fixative) if entryform_object.fixative else None
    )
    entryform["watersource"] = (
        model_to_dict(entryform_object.watersource)
        if entryform_object.watersource
        else None
    )
    entryform["specie"] = (
        model_to_dict(entryform_object.specie) if entryform_object.specie else None
    )

    patologos = list(User.objects.filter(userprofile__profile_id__in=[4, 5]).values())

    for item in entryform["identifications"]:
        servicios = {}
        for item2 in samples_as_dict:
            if item2["identification"]["id"] == item["id"]:

                for key, value in item2["sample_exams_set"].items():
                    if value["exam_name"] in servicios:
                        if value["stain"] in servicios[value["exam_name"]]:
                            for aux in value["organ_id"]:
                                servicios[value["exam_name"]][value["stain"]].append(
                                    aux["name"]
                                )
                        else:
                            servicios[value["exam_name"]][value["stain"]] = []
                            for aux in value["organ_id"]:
                                servicios[value["exam_name"]][value["stain"]].append(
                                    aux["name"]
                                )
                    else:
                        servicios[value["exam_name"]] = {value["stain"]: []}

                        for aux in value["organ_id"]:
                            servicios[value["exam_name"]][value["stain"]].append(
                                aux["name"]
                            )

        serv = {}
        for key, value in servicios.items():
            stains = {}
            for key2, value2 in value.items():

                organs = {}
                for k in value2:
                    if k in organs:
                        organs[k] += 1
                    else:
                        organs[k] = 1

                stains[key2] = organs

            new_key = key + " ("
            organs_amount_by_stain = {}
            for stain in value.keys():
                for org, cant in stains[stain].items():
                    if org in organs_amount_by_stain:
                        organs_amount_by_stain[org].append(cant)
                    else:
                        organs_amount_by_stain[org] = [cant]

                new_key += stain + " - "

            serv[new_key[:-3] + ")"] = organs_amount_by_stain

        item["servicios"] = serv

    data = {
        "entryform": entryform,
        "identifications": identifications,
        "case_created_by": User.objects.get(
            pk=entryform["created_by_id"]
        ).get_full_name(),
        "requested": datetime.now(),
        "report_generated_by": User.objects.get(pk=userId).get_full_name(),
        "patologos": patologos,
    }

    return render(request, "app/template_reception.html", data)


def template_resumen_report(request, id, userId):
    entryform = EntryForm.objects.values().get(pk=id)
    entryform_object = EntryForm.objects.get(pk=id)

    doc = (
        DocumentCaseResume.objects.filter(
            entryform=entryform_object, generated_by_id=userId
        )
        .order_by("-created_at")
        .first()
    )

    doc_data = model_to_dict(doc)
    # print (doc_data)

    subflow = entryform_object.get_subflow
    entryform["subflow"] = subflow
    entryform["entry_format"] = entryform_object.get_entry_format_display()
    identifications = list(
        Identification.objects.filter(entryform=entryform["id"]).values()
    )

    samples = Sample.objects.filter(entryform=entryform["id"]).order_by("index")

    samples_as_dict = []
    for s in samples:
        s_dict = model_to_dict(
            s, exclude=["organs", "sampleexams", "exams", "identification"]
        )
        organs = []
        sampleexams = s.sampleexams_set.all()
        sampleExa = {}

        for sE in sampleexams:
            analysis_form = entryform_object.analysisform_set.filter(
                exam_id=sE.exam_id
            ).first()
            try:
                a_form = analysis_form.forms.get()
                is_cancelled = a_form.cancelled
                is_closed = a_form.form_closed
            except:
                is_cancelled = False
                is_closed = False

            if not is_cancelled:
                try:
                    sampleExa[sE.exam_id]["organ_id"].append(
                        {
                            "name": sE.organ.name
                            if doc.lang == 1
                            else sE.organ.name_en
                            if sE.organ.name_en
                            else sE.organ.name,
                            "id": sE.organ.id,
                        }
                    )
                except:
                    sampleExa[sE.exam_id] = {
                        "exam_id": sE.exam_id,
                        "exam_name": sE.exam.name,
                        "exam_type": sE.exam.service_id,
                        "stain": sE.stain.abbreviation.upper() if sE.stain else "N/A",
                        "sample_id": sE.sample_id,
                        "organ_id": [
                            {
                                "name": sE.organ.name
                                if doc.lang == 1
                                else sE.organ.name_en
                                if sE.organ.name_en
                                else sE.organ.name,
                                "id": sE.organ.id,
                            }
                        ],
                    }
                if sE.exam.service_id == 1:
                    try:
                        organs.index(model_to_dict(sE.organ))
                    except:
                        organs.append(model_to_dict(sE.organ))
        s_dict["organs_set"] = organs
        s_dict["sample_exams_set"] = sampleExa
        s_dict["identification"] = model_to_dict(
            s.identification, exclude=["organs", "organs_before_validations"]
        )
        samples_as_dict.append(s_dict)

    entryform["identifications"] = []
    for ident in entryform_object.identification_set.all():
        ident_json = model_to_dict(
            ident, exclude=["organs", "organs_before_validations"]
        )
        ident_json["organs_set"] = list(ident.organs.all().values())
        ident_json["unit_count"] = ident.unit_set.count()
        entryform["identifications"].append(ident_json)

    entryform["analyses"] = list(
        entryform_object.analysisform_set.filter(exam__isnull=False).values(
            "id",
            "created_at",
            "comments",
            "entryform_id",
            "exam_id",
            "exam__name",
            "patologo_id",
            "patologo__first_name",
            "patologo__last_name",
        )
    )
    entryform["cassettes"] = list(entryform_object.cassette_set.all().values())
    entryform["customer"] = (
        model_to_dict(entryform_object.customer) if entryform_object.customer else None
    )
    entryform["larvalstage"] = (
        model_to_dict(entryform_object.larvalstage)
        if entryform_object.larvalstage
        else None
    )
    entryform["fixative"] = (
        model_to_dict(entryform_object.fixative) if entryform_object.fixative else None
    )
    entryform["watersource"] = (
        model_to_dict(entryform_object.watersource)
        if entryform_object.watersource
        else None
    )
    entryform["specie"] = (
        model_to_dict(entryform_object.specie) if entryform_object.specie else None
    )

    patologos = list(User.objects.filter(userprofile__profile_id__in=[4, 5]).values())

    for item in entryform["identifications"]:
        servicios = {}
        for item2 in samples_as_dict:
            if item2["identification"]["id"] == item["id"]:

                for key, value in item2["sample_exams_set"].items():
                    if value["exam_name"] in servicios:
                        if value["stain"] in servicios[value["exam_name"]]:
                            for aux in value["organ_id"]:
                                servicios[value["exam_name"]][value["stain"]].append(
                                    aux["name"]
                                )
                        else:
                            servicios[value["exam_name"]][value["stain"]] = []
                            for aux in value["organ_id"]:
                                servicios[value["exam_name"]][value["stain"]].append(
                                    aux["name"]
                                )
                    else:
                        servicios[value["exam_name"]] = {value["stain"]: []}

                        for aux in value["organ_id"]:
                            servicios[value["exam_name"]][value["stain"]].append(
                                aux["name"]
                            )

        serv = {}
        for key, value in servicios.items():
            stains = {}
            for key2, value2 in value.items():

                organs = {}
                for k in value2:
                    if k in organs:
                        organs[k] += 1
                    else:
                        organs[k] = 1

                stains[key2] = organs

            new_key = key + " ("
            organs_amount_by_stain = {}
            for stain in value.keys():
                for org, cant in stains[stain].items():
                    if org in organs_amount_by_stain:
                        organs_amount_by_stain[org].append(cant)
                    else:
                        organs_amount_by_stain[org] = [cant]

                new_key += stain + " - "

            serv[new_key[:-3] + ")"] = organs_amount_by_stain

        item["servicios"] = serv

    data = {
        "doc_data": doc,
        "entryform": entryform,
        "identifications": identifications,
        "case_created_by": User.objects.get(
            pk=entryform["created_by_id"]
        ).get_full_name(),
        "report_generated_by": User.objects.get(pk=userId).get_full_name(),
        "patologos": patologos,
    }

    if doc.lang == 1:
        return render(request, "app/template_resumen_report_es.html", data)
    elif doc.lang == 2:
        return render(request, "app/template_resumen_report_en.html", data)
    else:
        return render(request, "app/template_resumen_report_es.html", data)


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
        samples = Sample.objects.filter(identification_id=key).order_by("index")
        matrix = []
        first_column = [["MUESTRA / HALLAZGO", 1], ""]
        first_column = first_column + list(
            map(
                lambda x: x.identification.cage
                + "-"
                + x.identification.group
                + "-"
                + str(x.index),
                samples,
            )
        )
        matrix.append(first_column + [""])

        # print (matrix)

        res2 = defaultdict(list)
        value.sort(key=sortReport)
        for elem in value:
            res2[elem.pathology.name + " en " + elem.organ_location.name].append(elem)

        lastOrgan = ""
        for key2, value2 in res2.items():
            if lastOrgan == value2[0].organ.name:
                column = [["", 1], key2]
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
                    samples_by_index[item.sample.index].append(
                        item.diagnostic_intensity.name
                    )

            aux = []
            count_hallazgos = 0
            for k, v in samples_by_index.items():
                if len(v) > 0:
                    aux.append(v[0])
                    count_hallazgos += 1
                else:
                    aux.append("")

            column = column + aux
            percent = int(round((count_hallazgos * 100) / len(samples), 0))
            column.append(str(percent) + "%")
            matrix.append(column)

        data[key] = list(zip(*matrix))
        # print (data)
    return render(
        request,
        "app/preview_report.html",
        {
            "report": reports,
            "form_id": form.pk,
            "form_parent_id": form.parent.id,
            "reports2": data,
        },
    )


# @login_required
def notification(request):
    """DEPRECATED
    Display a template page notifying the User about a pending action they need to perform
    """
    ctx = {
        "name": "Name s",
        "nro_caso": "caso",
        "etapa_last": "current_state",
        "etapa_current": "next_state",
        "url": "settings.SITE_URL++str(form.id)++next_state.step.tag",
    }
    return render(request, "app/notification.html", ctx)


@login_required
def show_patologos(request, all):
    """
    Lists :model:`backend.AnalysisForm` according to the current user,
    allowing different filters to be used to display detailed data related
    to all items.

    **Parameters**
    ``all``
        A pk to an instance of :model:`backend.AnalysisForm`

    **Context**

    ``casos``
        A list of Dictionaries containing detailed information about Cases
    ``patologos``
        A list of :model:`auth.User` filtered by Pathologist role
    ``edit``
        A permision check if the current User can or cannot edit Cases
    ``all``

    **Template**

    :template:`app/patologos.html`
    """
    up = UserProfile.objects.filter(user=request.user).first()
    data = []
    patologos = list(
        User.objects.filter(
            Q(userprofile__profile_id__in=[4, 5]) | Q(userprofile__is_pathologist=True)
        ).values()
    )
    editar = up.profile_id in (1, 2, 3)

    return render(
        request,
        "app/patologos.html",
        {"patologos": patologos, "edit": editar, "all": all},
    )


@login_required
def tabla_patologos(request, all):
    up = UserProfile.objects.filter(user=request.user).first()

    draw = int(request.GET.get("draw"))
    length = int(request.GET.get("length"))
    search = request.GET.get("search[value]")
    start = int(request.GET.get("start")) + 1

    # Get AnalysisForm according to user permissions
    if request.user.is_superuser or up.profile_id in (1, 2, 3):
        analysis = (
            AnalysisForm.objects.filter(exam__isnull=False)
            .select_related("entryform", "exam")
            .order_by("-entryform_id")
        )
    elif up.profile_id in (4, 5):
        assigned_areas = UserArea.objects.filter(user=request.user, role=0)
        pks = [request.user.id]

        for user_area in assigned_areas:
            users = (
                UserArea.objects.filter(area=user_area.area)
                .exclude(user=request.user)
                .values_list("user", flat=True)
            )
            pks.extend(users)

        pathologists = User.objects.filter(
            Q(userprofile__profile_id__in=(4, 5)) | Q(userprofile__is_pathologist=True)
        ).filter(pk__in=pks)

        analysis = (
            AnalysisForm.objects.filter(patologo__in=pathologists, exam__isnull=False)
            .select_related("entryform", "exam")
            .order_by("-entryform_id")
        )

    else:
        analysis = (
            AnalysisForm.objects.filter(exam__isnull=False)
            .select_related("entryform", "exam")
            .order_by("-entryform_id")
        )

    patologos = list(
        User.objects.filter(
            Q(userprofile__profile_id__in=[4, 5]) | Q(userprofile__is_pathologist=True)
        ).values()
    )
    editar = up.profile_id in (1, 2, 3)

    if search:
        analysis = analysis.filter(
            Q(entryform__no_caso__icontains=search)
            | Q(entryform__customer__name__icontains=search)
            | Q(entryform__center__icontains=search)
            | Q(entryform__created_at__icontains=search)
            | Q(exam__name__icontains=search)
            | Q(assignment_done_at__icontains=search)
            | Q(patologo__first_name__icontains=search)
            | Q(patologo__last_name__icontains=search)
        )

    selected_analysis = []

    analysis_paginator = Paginator(analysis, length)

    context = {
        "draw": draw + 1,
        "recordsTotal": analysis_paginator.count,
        "recordsFiltered": analysis_paginator.count,
        "data": [],
    }

    for page in analysis_paginator.page_range:
        page_start = analysis_paginator.get_page(page).start_index()
        if page_start == start:
            analysis_page = analysis_paginator.get_page(page).object_list
            for a in analysis_page:
                entryform_form = a.entryform.forms.first()
                analysisform_form = a.forms.first()

                if int(all):
                    if (
                        entryform_form
                        and not entryform_form.cancelled
                        and analysisform_form
                        and a.exam.pathologists_assignment
                        and not analysisform_form.cancelled
                    ):
                        selected_analysis.append(
                            {
                                "analysis": a,
                                "entryform_form": entryform_form,
                                "analysisform_form": analysisform_form,
                            }
                        )
                else:
                    if (
                        entryform_form
                        and not entryform_form.cancelled
                        and a.exam.pathologists_assignment
                        and analysisform_form
                        and not analysisform_form.cancelled
                        and not entryform_form.form_closed
                    ):
                        selected_analysis.append(
                            {
                                "analysis": a,
                                "entryform_form": entryform_form,
                                "analysisform_form": analysisform_form,
                            }
                        )

    for a in selected_analysis:
        days_open = 0
        days_late = 0
        if not a["analysisform_form"].form_closed:
            # Analisis en curso

            current_date = datetime.now()
            if a["analysis"].assignment_deadline:
                if a["analysis"].pre_report_started and a["analysis"].pre_report_ended:
                    days_late = (
                        a["analysis"].pre_report_ended_at
                        - a["analysis"].assignment_deadline
                    ).days
                elif current_date > a["analysis"].assignment_deadline:
                    days_late = (current_date - a["analysis"].assignment_deadline).days

            days_open = (current_date - a["analysis"].created_at).days
        else:
            # Analisis cerrado
            if a["analysis"].assignment_deadline and a["analysis"].pre_report_ended_at:
                if (
                    a["analysis"].pre_report_ended_at
                    > a["analysis"].assignment_deadline
                ):
                    days_late = (
                        a["analysis"].pre_report_ended_at
                        - a["analysis"].assignment_deadline
                    ).days

            if a["analysis"].manual_closing_date:
                days_open = (
                    a["analysis"].manual_closing_date - a["analysis"].created_at
                ).days
            else:
                days_open = (
                    a["analysisform_form"].closed_at - a["analysis"].created_at
                ).days
        samples = Sample.objects.filter(entryform=a["analysis"].entryform).values_list(
            "id", flat=True
        )
        sampleExams_counter = 0
        sampleExams = SampleExams.objects.filter(
            sample__in=samples, exam=a["analysis"].exam, stain=a["analysis"].stain
        ).select_related("organ")
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

        parte = a["analysis"].entryform.get_subflow
        if parte == "N/A":
            parte = ""
        else:
            parte = " (Parte " + parte + ")"

        context["data"].append(
            {
                "analisis": a["analysis"].id,
                "patologo": a["analysis"].patologo_id
                if a["analysis"].patologo
                else None,
                "patologo_name": a["analysis"].patologo.first_name
                + " "
                + a["analysis"].patologo.last_name
                if a["analysis"].patologo
                else "No Asignado",
                "closed": 1 if a["analysisform_form"].form_closed else 0,
                "cancelled": 1 if a["analysisform_form"].cancelled else 0,
                "edit": not a["entryform_form"].form_closed
                and up.profile.id in (1, 2, 3)
                or request.user.is_superuser,
                "no_caso": a["analysis"].entryform.no_caso + parte,
                "exam": a["analysis"].exam.name,
                "cliente": a["analysis"].entryform.customer.name,
                "centro": a["analysis"].entryform.center,
                "fecha_ingreso": a["analysis"].created_at.strftime("%d/%m/%Y"),
                "dias_abierto": days_open,
                "nro_organos": sampleExams_counter,
                "entryform": a["analysis"].entryform.id,
                "entryform_form_closed": a["entryform_form"].form_closed,
                "entryform_cancelled": a["entryform_form"].cancelled,
                "unidad": unit,
                "fecha_derivacion": a["analysis"].assignment_done_at.strftime(
                    "%d/%m/%Y"
                )
                if a["analysis"].assignment_done_at
                else "",
                "fecha_plazo": a["analysis"].assignment_deadline.strftime("%d/%m/%Y")
                if a["analysis"].assignment_deadline
                else "",
                "dias_atraso": days_late,
                "estado": a["analysis"].status,
                "nota_diagnostico": str(a["analysis"].score_diagnostic).replace(
                    ",", "."
                )
                if a["analysis"].score_diagnostic
                else "",
                "nota_informe": str(a["analysis"].score_report).replace(",", ".")
                if a["analysis"].score_report
                else "",
            }
        )

    return JsonResponse(context)


class ChangeLanguage(View):
    """
    Switches in the language enum in :model:`accounts.UserProfile`
    the current language for localization
    """

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.language == 2:
            user_profile.language = 1
        else:
            user_profile.language = 2
        user_profile.save()
        return JsonResponse({"error": 0})

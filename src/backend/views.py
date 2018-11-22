from django.shortcuts import render
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from distutils.util import strtobool
from django.db.models import F
from django.db.models import Prefetch

from datetime import datetime
from .models import *
from workflows.models import *
from accounts.models import *


class CUSTOMER(View):
    http_method_names = ['post']

    def post(self, request):
        var_post = request.POST.copy()

        if (var_post.get('laboratorio') == "on"):
            laboratorio = 'l'
        else:
            laboratorio = 's'

        customer = Customer.objects.create(
            name=var_post.get('nombre'),
            company=var_post.get('rut'),
            type_customer=laboratorio)
        customer.save()

        return JsonResponse({'ok': True})


class EXAM(View):
    http_method_names = ['post']

    def post(self, request):
        var_post = request.POST.copy()

        exam = Exam.objects.create(name=var_post.get('nombre'), )
        exam.save()

        return JsonResponse({'ok': True})


class ORGAN(View):
    http_method_names = ['get']

    def get(self, request, organ_id=None):
        if organ_id:
            organ = Organ.objects.filter(pk=organ_id)
            organLocations = list(organ.organlocation_set.all().values())
            pathologys = list(organ.pathology_set.all().values())
            diagnostics = list(organ.diagnostic_set.all().values())
            diagnosticDistributions = list(
                organ.diagnosticdistribution_set.all().values())
            diagnosticIntensity = list(
                organ.diagnosticintensity_set.all().values())

        else:
            organs = list(Organ.objects.all().values())

            data = {
                'organs': organs,
            }

        return JsonResponse(data)


class ENTRYFORM(View):
    http_method_names = ['get']

    def get(self, request, id=None):
        if id:
            entryform = EntryForm.objects.values().get(pk=id)
            entryform_object = EntryForm.objects.get(pk=id)
            cacuca = entryform_object.get_subflow
            entryform["subflow"] = cacuca
            identifications = list(
                Identification.objects.filter(
                    entryform=entryform['id']).values())
            organs = list(
                EntryForm.objects.filter(id=id).values(
                    value=F('analysisform__organs__id'),
                    name=F('analysisform__organs__name')).distinct())

            entryform["identifications"] = list(
                entryform_object.identification_set.all().values())
            entryform["answer_questions"] = list(
                entryform_object.answerreceptioncondition_set.all().values())
            entryform["analyses"] = list(
                entryform_object.analysisform_set.all().values())

            cassettes = []
            for cassette in entryform_object.cassette_set.all():
                cassette_organs = [organ.id for organ in cassette.organs.all()]

                cassettes.append({
                    'sample_id':
                    cassette.sample_id,
                    'cassette_name':
                    cassette.cassette_name,
                    'processor_loaded_at':
                    cassette.processor_loaded_at,
                    'organs':
                    cassette_organs
                })

            entryform["cassettes"] = cassettes

            data = {
                'entryform': entryform,
                'identifications': identifications,
                'organs': organs,
            }
        else:
            species = list(Specie.objects.all().values())
            larvalStages = list(LarvalStage.objects.all().values())
            fixtatives = list(Fixative.objects.all().values())
            waterSources = list(WaterSource.objects.all().values())
            questionReceptionCondition = list(
                QuestionReceptionCondition.objects.filter(status='a').values())
            exams = list(Exam.objects.all().values())
            organs = list(Organ.objects.all().values())
            customers = list(Customer.objects.all().values())

            data = {
                'species': species,
                'larvalStages': larvalStages,
                'fixtatives': fixtatives,
                'waterSources': waterSources,
                'exams': exams,
                'organs': organs,
                'questionReceptionCondition': questionReceptionCondition,
                'customers': customers,
            }

        return JsonResponse(data)


class CASSETTE(View):
    http_method_names = ['get']

    def get(self, request, entry_form=None):
        analyses = list(
            AnalysisForm.objects.filter(entryform=entry_form).values_list(
                'id', flat=True))
        exams = list(
            AnalysisForm.objects.filter(entryform=entry_form).values(
                name=F('exam__name'), stain=F('exam__stain')))

        no_slice = len(analyses)

        cassettes_qs = Cassette.objects.filter(
            entryform=entry_form).prefetch_related(Prefetch('organs'))
        cassettes = []

        for cassette in cassettes_qs:
            organs = [organ.name for organ in cassette.organs.all()]

            slices = []
            for slice_new in cassette.slice_set.all():
                slices.append({
                    'start_block': slice_new.start_block,
                    'end_block': slice_new.end_block,
                    'start_slice': slice_new.start_slice,
                    'end_slice': slice_new.end_slice,
                    'slice_name': slice_new.slice_name
                })

            cassettes.append({
                'id': cassette.id,
                'sample_id': cassette.sample_id,
                'cassette_name': cassette.cassette_name,
                'organs': organs,
                'no_slice': no_slice,
                'slices': slices
            })

        data = {'cassettes': cassettes, 'exams': exams, 'analyses': analyses}

        return JsonResponse(data)


class ANALYSIS(View):
    def get(self, request, entry_form=None):
        print ("Entro a analiss")
        analyses_qs = AnalysisForm.objects.filter(entryform=entry_form)
        analyses = []

        for analysis in analyses_qs:
            exam = analysis.exam
            form = analysis.forms.get()

            form_id = form.id

            current_step_tag = form.state.step.tag
            current_step = form.state.step.order
            total_step = form.flow.step_set.count()
            percentage_step = (int(current_step) / int(total_step)) * 100

            slices_qs = analysis.slice_set.all()
            slices = []

            for slice_new in slices_qs:
                slices.append({'name': slice_new.slice_name})

            analyses.append({
                'form_id': form_id,
                'exam_name': exam.name,
                'exam_stain': exam.stain,
                'slices': slices,
                'current_step_tag': current_step_tag,
                'current_step': current_step,
                'total_step': total_step,
                'percentage_step': percentage_step,
                'form_closed': form.form_closed,
                # 'no_caso': analisys.entry_form.no_caso
            })
        data = {'analyses': analyses}

        return JsonResponse(data)


class SLICE(View):
    def get(self, request, analysis_form=None):
        slices_qs = Slice.objects.filter(analysis=analysis_form)
        slices = []

        for slice_new in slices_qs:
            slice_id = slice_new.id
            slice_name = slice_new.slice_name
            # identification_cage = slice_new.cassettes.first(
            # ).identifications.first().cage
            analysis = slice_new.analysis.first()
            cassett = slice_new.cassettes.first()
            organs = [organ.name for organ in analysis.organs.all()]
            paths_count = Report.objects.filter(slice_id=slice_new.pk).count()

            slices.append({
                'slice_id': slice_new.id,
                'slice_name': slice_new.slice_name,
                'identification': cassett.sample_id,
                'start_scan': slice_new.start_scan,
                'end_scan': slice_new.end_scan,
                'start_stain': slice_new.start_stain,
                'end_stain': slice_new.end_stain,
                'slice_store': slice_new.slice_store,
                'box_id': slice_new.box_id,
                'organs': organs,
                'paths_count': paths_count
            })
        # print ("slice")
        data = {'slices': slices}

        return JsonResponse(data)


class WORKFLOW(View):
    http_method_names = ['get', 'post', 'delete']
    def get(self, request, form_id, step_tag):
        form = Form.objects.get(pk=form_id)
        object_form_id = form.content_object.id

        if (form.content_type.name == 'entry form'):
            route = 'app/workflow_main.html'
            data = {
                'form': form,
                'form_id': form_id,
                'entryform_id': object_form_id,
                'set_step_tag': step_tag
            }
        elif (form.content_type.name == 'analysis form'):
            route = 'app/workflow_analysis.html'
            data = {
                'form': form,
                'form_id': form_id,
                'analysis_id': object_form_id,
                'set_step_tag': step_tag,
                'exam_name': form.content_object.exam.name,
                'form_parent_id': form.parent.id
            }

        return render(request, route, data)

    def post(self, request):
        var_post = request.POST.copy()

        up = UserProfile.objects.filter(user=request.user).first()
        form = Form.objects.get(pk=var_post.get('form_id'))

        form_closed = False

        if (var_post.get('form_closed')):
            form_closed = True

        if not form_closed:
            id_next_step = var_post.get('id_next_step')
            previous_step = strtobool(var_post.get('previous_step'))
            next_step = Step.objects.get(pk=id_next_step)

            next_step_permission = False
            process_response = False
            process_answer = True

            for actor in next_step.actors.all():
                if actor.profile == up.profile:
                    if previous_step:
                        next_state = actor.permission.get(
                            to_state=form.state).from_state
                    else:
                        next_state = actor.permission.get(
                            from_state=form.state).to_state

            if not previous_step:
                process_answer = call_process_method(form.content_type.model,
                                                     request)

            if process_answer:
                form.state = next_state
                form.save()

                for actor in form.state.step.actors.all():
                    if actor.profile == up.profile:
                        next_step_permission = True
                process_response = True
            else:
                print("FALLO EL PROCESAMIENTO")

            return JsonResponse({
                'process_response': process_response,
                'next_step_permission': next_step_permission
            })
        else:
            form.form_closed = True
            form.save()

            return JsonResponse({'redirect_flow': True})

    def delete(self, request, form_id):
        Form.objects.get(pk=form_id).delete()
        # object_form_id = form.content_object.id
        return JsonResponse({'ok': True})

class REPORT(View):
    def get(self, request, slice_id):
        if slice_id:
            report_qs = Report.objects.filter(slice=slice_id)

            reports = []
            for report in report_qs:
                reports.append({
                    "report_id":
                    report.id,
                    "organ":
                    report.organ.name,
                    "organ_location":
                    report.organ_location.name,
                    "pathology":
                    report.pathology.name,
                    "diagnostic":
                    report.diagnostic.name,
                    "diagnostic_distribution":
                    report.diagnostic_distribution.name,
                    "diagnostic_intensity":
                    report.diagnostic_intensity.name
                })

            data = {'reports': reports}

        return JsonResponse(data)

    def post(self, request):
        var_post = request.POST.copy()

        analysis_id = var_post.get('analysis_id')
        slice_id = var_post.get('slice_id')
        organ_id = var_post.get('organ')
        organ_location_id = var_post.get('organ_location')
        pathology_id = var_post.get('pathology')
        diagnostic_id = var_post.get('diagnostic')
        diagnostic_distribution_id = var_post.get('diagnostic_distribution')
        diagnostic_intensity_id = var_post.get('diagnostic_intensity')

        report = Report.objects.create(
            analysis_id=analysis_id,
            slice_id=slice_id,
            organ_id=organ_id,
            organ_location_id=organ_location_id,
            pathology_id=pathology_id,
            diagnostic_id=diagnostic_id,
            diagnostic_distribution_id=diagnostic_distribution_id,
            diagnostic_intensity_id=diagnostic_intensity_id,
        )
        report.save()

        return JsonResponse({'ok': True})

    def delete(self, request, report_id):
        if report_id:
            report = Report.objects.get(pk=report_id)
            report.delete()

        return JsonResponse({'ok': True})


def organs_by_slice(request, slice_id=None):
    if slice_id:
        organs_qs = Slice.objects.get(
            pk=slice_id).analysis.first().organs.all()

        organs = []
        for organ in organs_qs:
            organs.append({
                "id":
                organ.id,
                "name":
                organ.name,
                "organ_locations":
                list(organ.organlocation_set.all().values()),
                "pathologys":
                list(organ.pathology_set.all().values()),
                "diagnostics":
                list(organ.diagnostic_set.all().values()),
                "diagnostic_distributions":
                list(organ.diagnosticdistribution_set.all().values()),
                "diagnostic_intensity":
                list(organ.diagnosticintensity_set.all().values())
            })

        data = {'organs': organs}

        return JsonResponse(data)

def set_analysis_comments(request, analysisform_id):
    try:
        analysis = AnalysisForm.objects.get(pk=analysisform_id)
        comments = request.POST.get('comments')
        print (comments)
        analysis.comments = comments
        analysis.save()
        return JsonResponse({'ok': True})
    except:
        return JsonResponse({'ok': False})

# Any process function must to have a switcher for choice which method will be call
def process_entryform(request):
    step_tag = request.POST.get('step_tag')

    # try:
    switcher = {
        'step_1': step_1_entryform,
        'step_2': step_2_entryform,
        'step_3': step_3_entryform,
        'step_4': step_4_entryform
    }

    method = switcher.get(step_tag)

    if not method:
        raise NotImplementedError(
            "Method %s_entryform not implemented" % step_tag)

    method(request)

    return True


def process_analysisform(request):
    step_tag = request.POST.get('step_tag')

    # try:
    switcher = {
        'step_1': step_1_analysisform,
        'step_2': step_2_analysisform,
        'step_3': step_3_analysisform,
        'step_4': step_4_analysisform,
    }

    method = switcher.get(step_tag)

    if not method:
        raise NotImplementedError(
            "Method %s_entryform not implemented" % step_tag)

    method(request)

    return True


# Steps Function for entry forms
def step_1_entryform(request):
    var_post = request.POST.copy()

    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))

    entryform.specie_id = var_post.get('specie')
    entryform.watersource_id = var_post.get('watersource')
    entryform.fixative_id = var_post.get('fixative')
    entryform.larvalstage_id = var_post.get('larvalstage')
    entryform.observation = var_post.get('observation')
    entryform.customer_id = var_post.get('customer')
    entryform.no_order = var_post.get('no_order')
    entryform.created_at = var_post.get('created_at_submit')
    entryform.sampled_at = var_post.get('sampled_at_submit')
    entryform.center = var_post.get('center')
    entryform.save()

    questions_id = [
        v for k, v in var_post.items() if k.startswith("question['id']")
    ]
    answers = [
        v for k, v in var_post.items() if k.startswith("question['answer']")
    ]
    zip_question = zip(questions_id, answers)

    entryform.answerreceptioncondition_set.all().delete()
    for values in zip_question:
        answerquestion = AnswerReceptionCondition.objects.create(
            entryform_id=entryform.id,
            question_id=values[0],
            answer=values[1],
        )

    # Check if user wants split flow
    if strtobool(var_post.get('select_if_divide_flow')):
        if var_post.get('flow_divide_option') == "1":
            identification_cage = var_post.getlist("identification[cage]")
            identification_group = var_post.getlist("identification[group]")
            identification_no_container = var_post.getlist(
                "identification[no_container]")
            identification_no_fish = var_post.getlist("identification[no_fish]")

            zip_identification = list(zip(identification_cage, identification_group,
                                    identification_no_container,
                                    identification_no_fish))

            for i in range(len(zip_identification)):
                # First identification is first subflow and it had some data saved before.
                # Next iterations need to create an entire EntryForm based in the first one.
                if i == 0:
                    entryform.identification_set.all().delete()
                    identificacion = Identification.objects.create(
                        entryform_id=entryform.id,
                        cage=zip_identification[i][0],
                        group=zip_identification[i][1],
                        no_container=zip_identification[i][2],
                        no_fish=zip_identification[i][3],
                    )

                    analysis_id = [
                        v for k, v in var_post.items() if k.startswith("analysis[id]")
                    ]
                    analysis_no_fish = [
                        v for k, v in var_post.items() if k.startswith("analysis[no_fish]")
                    ]
                    analysis_organ = [
                        var_post.getlist(k) for k, v in var_post.items()
                        if k.startswith("analysis[organ]")
                    ]

                    zip_analysis = zip(analysis_id, analysis_no_fish, analysis_organ)

                    analyses_qs = entryform.analysisform_set.all()

                    for analysis in analyses_qs:
                        analysis.forms.get().delete()

                    analyses_qs.delete()

                    flow = Flow.objects.get(pk=2)

                    for values in zip_analysis:
                        analysis = AnalysisForm.objects.create(
                            entryform_id=entryform.id,
                            exam_id=values[0],
                            no_fish=zip_identification[i][3],
                        )

                        analysis.organs.set(values[2])

                        Form.objects.create(
                            content_object=analysis,
                            flow=flow,
                            state=flow.step_set.all()[0].state,
                            parent_id=entryform.forms.first().id)

                else:
                    flow_aux = Flow.objects.get(pk=1)
                    entryform_aux = EntryForm.objects.create()
                    form_aux = Form.objects.create(
                        content_object=entryform_aux, flow=flow_aux, state=flow_aux.step_set.all()[1:2].first().state)
                    entryform_aux.specie_id = var_post.get('specie')
                    entryform_aux.watersource_id = var_post.get('watersource')
                    entryform_aux.fixative_id = var_post.get('fixative')
                    entryform_aux.larvalstage_id = var_post.get('larvalstage')
                    entryform_aux.observation = var_post.get('observation')
                    entryform_aux.customer_id = var_post.get('customer')
                    entryform_aux.no_order = var_post.get('no_order')
                    entryform_aux.created_at = var_post.get('created_at_submit')
                    entryform_aux.sampled_at = var_post.get('sampled_at_submit')
                    entryform_aux.center = var_post.get('center')
                    entryform_aux.no_caso = entryform.no_caso

                    entryform_aux.save()

                    questions_id = [
                        v for k, v in var_post.items() if k.startswith("question['id']")
                    ]
                    answers = [
                        v for k, v in var_post.items() if k.startswith("question['answer']")
                    ]
                    zip_question = zip(questions_id, answers)

                    entryform_aux.answerreceptioncondition_set.all().delete()
                    for values in zip_question:
                        answerquestion = AnswerReceptionCondition.objects.create(
                            entryform_id=entryform_aux.id,
                            question_id=values[0],
                            answer=values[1],
                        )

                    entryform_aux.identification_set.all().delete()
                    identificacion = Identification.objects.create(
                        entryform_id=entryform_aux.id,
                        cage=zip_identification[i][0],
                        group=zip_identification[i][1],
                        no_container=zip_identification[i][2],
                        no_fish=zip_identification[i][3],
                    )

                    analysis_id = [
                        v for k, v in var_post.items() if k.startswith("analysis[id]")
                    ]
                    analysis_no_fish = [
                        v for k, v in var_post.items() if k.startswith("analysis[no_fish]")
                    ]
                    analysis_organ = [
                        var_post.getlist(k) for k, v in var_post.items()
                        if k.startswith("analysis[organ]")
                    ]

                    zip_analysis = zip(analysis_id, analysis_no_fish, analysis_organ)

                    analyses_qs = entryform_aux.analysisform_set.all()

                    for analysis in analyses_qs:
                        analysis.forms.get().delete()

                    analyses_qs.delete()

                    flow = Flow.objects.get(pk=2)

                    for values in zip_analysis:
                        analysis = AnalysisForm.objects.create(
                            entryform_id=entryform_aux.id,
                            exam_id=values[0],
                            no_fish=zip_identification[i][3],
                        )

                        analysis.organs.set(values[2])

                        Form.objects.create(
                            content_object=analysis,
                            flow=flow,
                            state=flow.step_set.all()[0].state,
                            parent_id=entryform_aux.forms.first().id)

        elif var_post.get('flow_divide_option') == "2":
            identification_id = var_post.getlist("identification[id]")
            identification_cage = var_post.getlist("identification[cage]")
            identification_group = var_post.getlist("identification[group]")
            identification_no_container = var_post.getlist("identification[no_container]")
            identification_no_fish = var_post.getlist("identification[no_fish]")

            zip_identification = list(zip(identification_cage, 
                                    identification_group,
                                    identification_no_container,
                                    identification_no_fish,
                                    identification_id))
            subflow_groups = [
                var_post.getlist(k) for k, v in var_post.items()
                if k.startswith("subflow_select[group]")
            ]

            # print (subflow_groups)
            # print (zip_identification)
            for i in range(len(subflow_groups)):
                if i == 0:
                    total_no_fish = 0
                    entryform.identification_set.all().delete()
                    for j in range(len(zip_identification)):
                        new_no_fish = 0
                        for item in subflow_groups[i]:
                            if item.split("_")[0] == zip_identification[j][4]:
                                new_no_fish += 1
                        identificacion = Identification.objects.create(
                            entryform_id=entryform.id,
                            cage=zip_identification[j][0],
                            group=zip_identification[j][1],
                            no_container=zip_identification[j][2],
                            no_fish=new_no_fish,
                        )
                        total_no_fish += new_no_fish

                    analysis_id = [
                        v for k, v in var_post.items() if k.startswith("analysis[id]")
                    ]
                    analysis_no_fish = [
                        v for k, v in var_post.items() if k.startswith("analysis[no_fish]")
                    ]
                    analysis_organ = [
                        var_post.getlist(k) for k, v in var_post.items()
                        if k.startswith("analysis[organ]")
                    ]

                    zip_analysis = zip(analysis_id, analysis_no_fish, analysis_organ)

                    analyses_qs = entryform.analysisform_set.all()

                    for analysis in analyses_qs:
                        analysis.forms.get().delete()

                    analyses_qs.delete()

                    flow = Flow.objects.get(pk=2)

                    for values in zip_analysis:
                        analysis = AnalysisForm.objects.create(
                            entryform_id=entryform.id,
                            exam_id=values[0],
                            no_fish=total_no_fish,
                        )

                        analysis.organs.set(values[2])

                        Form.objects.create(
                            content_object=analysis,
                            flow=flow,
                            state=flow.step_set.all()[0].state,
                            parent_id=entryform.forms.first().id)

                else:
                    flow_aux = Flow.objects.get(pk=1)
                    entryform_aux = EntryForm.objects.create()
                    form_aux = Form.objects.create(
                        content_object=entryform_aux, flow=flow_aux, state=flow_aux.step_set.all()[1:2].first().state)
                    entryform_aux.specie_id = var_post.get('specie')
                    entryform_aux.watersource_id = var_post.get('watersource')
                    entryform_aux.fixative_id = var_post.get('fixative')
                    entryform_aux.larvalstage_id = var_post.get('larvalstage')
                    entryform_aux.observation = var_post.get('observation')
                    entryform_aux.customer_id = var_post.get('customer')
                    entryform_aux.no_order = var_post.get('no_order')
                    entryform_aux.created_at = var_post.get('created_at_submit')
                    entryform_aux.sampled_at = var_post.get('sampled_at_submit')
                    entryform_aux.center = var_post.get('center')
                    entryform_aux.no_caso = entryform.no_caso

                    entryform_aux.save()

                    questions_id = [
                        v for k, v in var_post.items() if k.startswith("question['id']")
                    ]
                    answers = [
                        v for k, v in var_post.items() if k.startswith("question['answer']")
                    ]
                    zip_question = zip(questions_id, answers)

                    entryform_aux.answerreceptioncondition_set.all().delete()
                    for values in zip_question:
                        answerquestion = AnswerReceptionCondition.objects.create(
                            entryform_id=entryform_aux.id,
                            question_id=values[0],
                            answer=values[1],
                        )

                    entryform_aux.identification_set.all().delete()
                    total_no_fish = 0
                    for j in range(len(zip_identification)):
                        new_no_fish = 0
                        for item in subflow_groups[i]:
                            if item.split("_")[0] == zip_identification[j][4]:
                                new_no_fish += 1
                        identificacion = Identification.objects.create(
                            entryform_id=entryform_aux.id,
                            cage=zip_identification[j][0],
                            group=zip_identification[j][1],
                            no_container=zip_identification[j][2],
                            no_fish=new_no_fish,
                        )
                        total_no_fish += new_no_fish

                    analysis_id = [
                        v for k, v in var_post.items() if k.startswith("analysis[id]")
                    ]
                    analysis_no_fish = [
                        v for k, v in var_post.items() if k.startswith("analysis[no_fish]")
                    ]
                    analysis_organ = [
                        var_post.getlist(k) for k, v in var_post.items()
                        if k.startswith("analysis[organ]")
                    ]

                    zip_analysis = zip(analysis_id, analysis_no_fish, analysis_organ)

                    analyses_qs = entryform_aux.analysisform_set.all()

                    for analysis in analyses_qs:
                        analysis.forms.get().delete()

                    analyses_qs.delete()

                    flow = Flow.objects.get(pk=2)

                    for values in zip_analysis:
                        analysis = AnalysisForm.objects.create(
                            entryform_id=entryform_aux.id,
                            exam_id=values[0],
                            no_fish=total_no_fish,
                        )

                        analysis.organs.set(values[2])

                        Form.objects.create(
                            content_object=analysis,
                            flow=flow,
                            state=flow.step_set.all()[0].state,
                            parent_id=entryform_aux.forms.first().id)

    else:
        identification_cage = var_post.getlist("identification[cage]")
        identification_group = var_post.getlist("identification[group]")
        identification_no_container = var_post.getlist(
            "identification[no_container]")
        identification_no_fish = var_post.getlist("identification[no_fish]")

        zip_identification = zip(identification_cage, identification_group,
                                identification_no_container,
                                identification_no_fish)

        entryform.identification_set.all().delete()
        for values in zip_identification:
            identificacion = Identification.objects.create(
                entryform_id=entryform.id,
                cage=values[0],
                group=values[1],
                no_container=values[2],
                no_fish=values[3],
            )

        analysis_id = [
            v for k, v in var_post.items() if k.startswith("analysis[id]")
        ]
        analysis_no_fish = [
            v for k, v in var_post.items() if k.startswith("analysis[no_fish]")
        ]
        analysis_organ = [
            var_post.getlist(k) for k, v in var_post.items()
            if k.startswith("analysis[organ]")
        ]

        zip_analysis = zip(analysis_id, analysis_no_fish, analysis_organ)

        analyses_qs = entryform.analysisform_set.all()

        for analysis in analyses_qs:
            analysis.forms.get().delete()

        analyses_qs.delete()

        flow = Flow.objects.get(pk=2)

        for values in zip_analysis:
            analysis = AnalysisForm.objects.create(
                entryform_id=entryform.id,
                exam_id=values[0],
                no_fish=values[1],
            )

            analysis.organs.set(values[2])

            Form.objects.create(
                content_object=analysis,
                flow=flow,
                state=flow.step_set.all()[0].state,
                parent_id=entryform.forms.first().id)

def step_2_entryform(request):
    var_post = request.POST.copy()

    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))
    processor_loaded_at = var_post.get('processor_loaded_at_submit')

    cassette_sample_id = [
        v for k, v in var_post.items() if k.startswith("cassette[sample_id]")
    ]
    cassette_name = [
        v for k, v in var_post.items()
        if k.startswith("cassette[cassette_name]")
    ]

    print (cassette_name)
    cassette_organs = [
        var_post.getlist(k) for k, v in var_post.items()
        if k.startswith("cassette[organ]")
    ]

    print (cassette_organs)
    cassette_identification_id = [
        var_post.getlist(k) for k, v in var_post.items()
        if k.startswith("cassette[identification_id]")
    ]

    print (cassette_identification_id)

    zip_cassettes = zip(cassette_sample_id, cassette_name, cassette_organs,
                        cassette_identification_id)



    entryform.cassette_set.all().delete()
    for values in zip_cassettes:
        cassette = Cassette.objects.create(
            entryform_id=entryform.id,
            processor_loaded_at=processor_loaded_at,
            sample_id=values[0],
            cassette_name=values[1],
        )
        cassette.save()
        cassette.organs.set(values[2])
        cassette.identifications.set(values[3])


def step_3_entryform(request):
    var_post = request.POST.copy()

    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))

    block_cassette_pk = [
        var_post.getlist(k) for k, v in var_post.items()
        if k.startswith("block_cassette_pk")
    ]
    block_start_block = [
        v for k, v in var_post.items() if k.startswith("block_start_block")
    ]
    block_end_block = [
        v for k, v in var_post.items() if k.startswith("block_end_block")
    ]
    block_start_slice = [
        v for k, v in var_post.items() if k.startswith("block_start_slice")
    ]
    block_end_slice = [
        v for k, v in var_post.items() if k.startswith("block_end_slice")
    ]
    block_cassette_name = [
        v for k, v in var_post.items() if k.startswith("block_cassette_name")
    ]
    block_analyses = [
        var_post.getlist(k) for k, v in var_post.items()
        if k.startswith("analyses")
    ]

    block_analyses = list(set(block_analyses[0]))

    zip_block = zip(block_start_block, block_end_block, block_start_slice,
                    block_end_slice, block_cassette_pk, block_cassette_name)

    entryform.slice_set.all().delete()

    for values in zip_block:
        slice_index = 0
        for index, val in enumerate(block_analyses):
            slice_index = index + 1
            slice_name = values[5] + "-S" + str(slice_index)

            slice_new = Slice.objects.create(
                entryform_id=entryform.id,
                slice_name=slice_name,
                start_block=values[0],
                end_block=values[1],
                start_slice=values[2],
                end_slice=values[3],
            )
            slice_new.save()

            slice_new.cassettes.set(values[4])
            slice_new.analysis.set([val])


def step_4_entryform(request):
    print("step_4")


def step_1_analysisform(request):
    var_post = request.POST.copy()

    stain_slice_id = [
        v for k, v in var_post.items() if k.startswith("stain[slice_id]")
    ]
    stain_start_stain = [
        v for k, v in var_post.items() if k.startswith("stain[start_stain]")
    ]
    stain_end_stain = [
        v for k, v in var_post.items() if k.startswith("stain[end_stain]")
    ]

    zip_stain = zip(stain_slice_id, stain_start_stain, stain_end_stain)

    for values in zip_stain:
        slice_new = Slice.objects.get(pk=values[0])
        slice_new.start_stain = values[1]
        slice_new.end_stain = values[2]

        slice_new.save()


def step_2_analysisform(request):
    var_post = request.POST.copy()

    scan_slice_id = [
        v for k, v in var_post.items() if k.startswith("scan[slice_id]")
    ]
    scan_start_scan = [
        v for k, v in var_post.items() if k.startswith("scan[start_scan]")
    ]
    scan_end_scan = [
        v for k, v in var_post.items() if k.startswith("scan[end_scan]")
    ]
    scan_store = [
        v for k, v in var_post.items() if k.startswith("scan[store]")
    ]

    zip_scan = zip(scan_slice_id, scan_start_scan, scan_end_scan, scan_store)

    for values in zip_scan:
        slice_new = Slice.objects.get(pk=values[0])
        slice_new.start_scan = values[1]
        slice_new.end_scan = values[2]
        slice_new.slice_store = values[3]

        slice_new.save()


def step_3_analysisform(request):
    var_post = request.POST.copy()

    store_slice_id = [
        v for k, v in var_post.items() if k.startswith("store[slice_id]")
    ]
    store_box_id = [
        v for k, v in var_post.items() if k.startswith("store[box_id]")
    ]

    zip_store = zip(store_slice_id, store_box_id)

    for values in zip_store:
        slice_new = Slice.objects.get(pk=values[0])
        slice_new.box_id = values[1]

        slice_new.save()


def step_4_analysisform(request):
    print("Step 4 Analysis Form")


# Generic function for call any process method for any model_form
def call_process_method(model_name, request):
    method_name = "process_" + str(model_name)
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(method_name)
    if not method:
        raise NotImplementedError("Method %s not implemented" % method_name)
    return method(request)

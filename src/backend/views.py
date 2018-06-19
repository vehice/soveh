from django.shortcuts import render
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from distutils.util import strtobool
from utils.functions import renderjson
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
            identifications = list(
                Identification.objects.filter(
                    entryform=entryform['id']).values())
            organs = list(
                EntryForm.objects.filter(id=id).values(
                    value=F('analysisform__organs__id'),
                    name=F('analysisform__organs__name')).distinct())

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

            cassettes.append({
                'id': cassette.id,
                'sample_id': cassette.sample_id,
                'cassette_name': cassette.cassette_name,
                'organs': organs,
                'no_slice': no_slice
            })

        data = {'cassettes': cassettes, 'exams': exams, 'analyses': analyses}

        return JsonResponse(data)


class ANALYSIS(View):
    def get(self, request, entry_form=None):
        analyses_qs = AnalysisForm.objects.filter(entryform=entry_form)
        analyses = []

        for analysis in analyses_qs:
            exam = analysis.exam
            form = analysis.forms.get()

            form_id = form.id

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
                'current_step': current_step,
                'total_step': total_step,
                'percentage_step': percentage_step,
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
            identification_cage = slice_new.cassettes.first(
            ).identifications.first().cage
            analysis = slice_new.analysis.first()
            organs = [organ.name for organ in analysis.organs.all()]

            slices.append({
                'slice_id': slice_id,
                'slice_name': slice_name,
                'identification_cage': identification_cage,
                'organs': organs
            })

        data = {'slices': slices}

        return JsonResponse(data)


class WORKFLOW(View):
    def post(self, request):
        var_post = request.POST.copy()
        print("WORKFLOWWWW")
        print(var_post)

        id_next_step = var_post.get('id_next_step')
        previous_step = strtobool(var_post.get('previous_step'))
        next_step = Step.objects.get(pk=id_next_step)

        next_step_permission = False
        process_response = False
        process_answer = True

        up = UserProfile.objects.filter(user=request.user).first()
        form = Form.objects.get(pk=var_post.get('form_id'))

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


# Any process function must to have a switcher for choice which method will be call
def process_entryform(request):
    step_tag = request.POST.get('step_tag')

    # try:
    switcher = {
        'step_1_main': step_1_entryform,
        'step_2_main': step_2_entryform,
        'step_3_main': step_3_entryform,
        'step_4_main': step_4_entryform
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
        'step_1_analysis': step_1_analysisform,
        'step_2_analysis': step_2_analysisform,
        'step_3_analysis': step_3_analysisform,
        'step_4_analysis': step_4_analysisform,
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
            state=flow.step_set.all()[0].state)


def step_2_entryform(request):
    var_post = request.POST.copy()

    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))

    cassette_sample_id = [
        v for k, v in var_post.items() if k.startswith("cassette[sample_id]")
    ]
    cassette_name = [
        v for k, v in var_post.items()
        if k.startswith("cassette[cassette_name]")
    ]
    cassette_organs = [
        var_post.getlist(k) for k, v in var_post.items()
        if k.startswith("cassette[organ]")
    ]
    cassette_identification_id = [
        var_post.getlist(k) for k, v in var_post.items()
        if k.startswith("cassette[identification_id]")
    ]

    zip_cassettes = zip(cassette_sample_id, cassette_name, cassette_organs,
                        cassette_identification_id)

    entryform.cassette_set.all().delete()
    for values in zip_cassettes:
        cassette = Cassette.objects.create(
            entryform_id=entryform.id,
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
        if k.startswith("block[cassette_pk]")
    ]
    block_start_block = [
        v for k, v in var_post.items() if k.startswith("block[start_block]")
    ]
    block_end_block = [
        v for k, v in var_post.items() if k.startswith("block[end_block]")
    ]
    block_start_slice = [
        v for k, v in var_post.items() if k.startswith("block[start_slice]")
    ]
    block_end_slice = [
        v for k, v in var_post.items() if k.startswith("block[end_slice]")
    ]
    block_cassette_name = [
        v for k, v in var_post.items() if k.startswith("block[cassette_name]")
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

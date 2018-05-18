from django.shortcuts import render
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from utils.functions import renderjson
from django.db.models import F
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


class ENTRYFORM(View):
    http_method_names = ['get']

    def get(self, request, id=None):

        if id:
            entryform = EntryForm.objects.values().get(pk=id)
            identification = list(
                Identification.objects.filter(
                    entryform=entryform['id']).values())
            organs = list(
                EntryForm.objects.filter(id=id).values(
                    value=F('analysis__organs__id'),
                    name=F('analysis__organs__name')).distinct())

            data = {
                'entryform': entryform,
                'identifications': identification,
                'organs': organs
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


class WORKFLOW(View):
    def post(self, request):
        var_post = request.POST.copy()
        next_step_permission = False
        process_response = False

        up = UserProfile.objects.filter(user=request.user).first()
        form = Form.objects.get(pk=var_post.get('form_id'))

        next_state = form.state
        for actor in form.state.step.actors.all():
            if actor.profile == up.profile:
                next_state = actor.permission.get(
                    from_state=form.state).to_state

        process_answer = call_process_method(form.content_type.model, request)

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


# Any process function must to have a switcher for choice which method will be call
def process_entryform(request):
    step_tag = request.POST.get('step_tag')

    # try:
    switcher = {
        'step_1': step_1_entryform,
        'step_2': step_2_entryform,
        'step_3': step_3_entryform
    }

    method = switcher.get(step_tag)

    if not method:
        raise NotImplementedError(
            "Method %s_entryform not implemented" % step_tag)

    method(request)

    return True


# Steps Function for entry forms
def step_1_entryform(request):
    print("step_1")

    var_post = request.POST.copy()
    print(var_post)
    form = Form.objects.get(pk=var_post.get('form_id'))
    entryform = form.content_object

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

    for values in zip_question:
        answerquestion = AnswerReceptionCondition.objects.create(
            entryform_id=entryform.id,
            question_id=values[0],
            answer=values[1],
        )
        answerquestion.save()

    identification_cage = var_post.getlist("identification[cage]")
    identification_group = var_post.getlist("identification[group]")
    identification_no_container = var_post.getlist(
        "identification[no_container]")
    identification_no_fish = var_post.getlist("identification[no_fish]")

    zip_identification = zip(identification_cage, identification_group,
                             identification_no_container,
                             identification_no_fish)

    for values in zip_identification:
        identificacion = Identification.objects.create(
            entryform_id=entryform.id,
            cage=values[0],
            group=values[1],
            no_container=values[2],
            no_fish=values[3],
        )
        identificacion.save()

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

    for values in zip_analysis:
        analysis = Analysis.objects.create(
            entryform_id=entryform.id,
            exam_id=values[0],
            no_fish=values[1],
        )
        analysis.save()
        analysis.organs.set(values[2])


def step_2_entryform(request):
    print("step_2")
    var_post = request.POST.copy()
    print(var_post)
    entryform = var_post.get('entryform_id')

    cassette_sample_id = [
        v for k, v in var_post.items() if k.startswith("cassette[sample_id]")
    ]
    cassette_organs = [
        var_post.getlist(k) for k, v in var_post.items()
        if k.startswith("cassette[organ]")
    ]

    zip_cassettes = zip(cassette_sample_id, cassette_organs)

    for values in zip_cassettes:
        cassette = Cassette.objects.create(
            entryform_id=entryform,
            sample_id=values[0],
        )
        cassette.save()
        cassette.organs.set(values[1])


def step_3_entryform(request):
    print("step_3")
    return 'step_3'


# Generic function for call any process method for any model_form
def call_process_method(model_name, request):
    method_name = "process_" + str(model_name)
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(method_name)
    if not method:
        raise NotImplementedError("Method %s not implemented" % method_name)
    return method(request)

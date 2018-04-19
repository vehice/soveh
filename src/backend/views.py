from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from .models import *
from workflows.models import *


# Create your views here.
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
    http_method_names = ['post']

    def post(self, request):
        var_post = request.POST.copy()

        entry_form = EntryForm.objects.create(
            specie_id=var_post.get('specie'),
            watersource_id=var_post.get('watersource'),
            fixative_id=var_post.get('fixative'),
            larvalstage_id=var_post.get('larvalstage'),
            observation=var_post.get('observation'),
            customer_id=var_post.get('customer'),
            no_order=var_post.get('no_order'),
            created_at=var_post.get('created_at_submit'),
            sampled_at=var_post.get('sampled_at_submit'),
        )
        entry_form.save()

        questions_id = [
            v for k, v in var_post.items() if k.startswith("question['id']")
        ]
        answers = [
            v for k, v in var_post.items()
            if k.startswith("question['answer']")
        ]
        zip_question = zip(questions_id, answers)

        for values in zip_question:
            answerquestion = AnswerReceptionCondition.objects.create(
                entryform_id=entry_form.id,
                question_id=values[0],
                answer=values[1],
            )
            answerquestion.save()

        identification_cage = var_post.getlist("identification['cage']")
        identification_group = var_post.getlist("identification['group']")
        identification_no_container = var_post.getlist(
            "identification['no_container']")
        identification_no_fish = var_post.getlist("identification['no_fish']")

        zip_identification = zip(identification_cage, identification_group,
                                 identification_no_container,
                                 identification_no_fish)

        for values in zip_identification:
            identificacion = Identification.objects.create(
                entryform_id=entry_form.id,
                cage=values[0],
                group=values[1],
                no_container=values[2],
                no_fish=values[3],
            )
            identificacion.save()

        content_type = ContentType.objects.get_for_model(EntryForm)

        # TODO Mejorar esto
        #Info que debe venir
        flow = Flow.objects.get(pk=1)

        Form.objects.create(
            flow=flow,
            state=flow.step_set.all()[0].state,
            object_id=entry_form.id,
            content_type=content_type)

        return JsonResponse({'ok': True})

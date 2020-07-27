from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from distutils.util import strtobool
from django.db.models import F
from django.db.models import Prefetch
from app import views as app_view
from datetime import datetime
from .models import *
from workflows.models import *
from accounts.models import *
from django.forms.models import model_to_dict
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from django.db import connection
import random
import string

# from utils import functions as fn

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
            subflow = entryform_object.get_subflow
            entryform["subflow"] = subflow
            identifications = list(
                Identification.objects.filter(
                    entryform=entryform['id']).values())
            
            samples = Sample.objects.filter(
                    entryform=entryform['id']).order_by('index', 'identification_id')
            
            samples_as_dict = []
            for s in samples:
                s_dict = model_to_dict(s, exclude=['organs', 'sampleexams', 'exams', 'identification', 'organs_before_validations'])
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
                            'exam_type': sE.exam.service_id,
                            'sample_id': sE.sample_id,
                            'organ_id': [{
                            'name':sE.organ.name,
                            'id':sE.organ.id}]
                        }
                    if sE.exam.service_id in [1,2,3]:
                        if sE.organ in s.identification.organs_before_validations.all():
                            try:
                                organs.index(model_to_dict(sE.organ))
                            except:
                                organs.append(model_to_dict(sE.organ))
                        else:
                            for org in s.identification.organs_before_validations.all():
                                if org.organ_type == 2:
                                    try:
                                        organs.index(model_to_dict(org))
                                    except:
                                        organs.append(model_to_dict(org))
                cassettes = Cassette.objects.filter(samples__in=[s])
                s_dict['organs_set'] = organs
                s_dict['sample_exams_set'] = sampleExa
                cassettes_set = []
                for c in cassettes:
                    cassettes_set.append({
                        'cassette_name': c.cassette_name,
                        'entryform_id': c.entryform_id,
                        'id': c.id,
                        'index': c.index,
                        'sample_id': s.id,
                        'organs_set': list(c.organs.values())
                    })
                s_dict['cassettes_set'] = cassettes_set
                s_dict['identification'] = model_to_dict(s.identification, exclude=["organs",'organs_before_validations'])
                s_dict['identification']['organs'] = list(s.identification.organs.all().values())
                s_dict['identification']['organs_bv'] = list(s.identification.organs_before_validations.all().values())
                samples_as_dict.append(s_dict)

            # entryform["identifications"] = list(
            #     entryform_object.identification_set.all().values())
            entryform["identifications"] = []
            for ident in entryform_object.identification_set.all():
                ident_json = model_to_dict(ident, exclude=["organs", "organs_before_validations"])
                ident_json['organs_set'] = list(ident.organs.all().values())
                ident_json['organs_bv_set'] = list(ident.organs_before_validations.all().values())
                entryform["identifications"].append(ident_json)              

            # entryform["analyses"] = list(
            #     entryform_object.analysisform_set.all().values('id', 'created_at', 'comments', 'entryform_id', 'exam_id', 'exam__name', 'patologo_id', 'patologo__first_name', 'patologo__last_name'))
            
            entryform["analyses"] = []
            for analysis in entryform_object.analysisform_set.all():
                aux = {
                    'id': analysis.id,
                    'created_at' : analysis.created_at,
                    'comments' : analysis.comments,
                    'entryform_id' : analysis.entryform_id,
                    'exam_id' : analysis.exam_id,
                    'exam__name' : analysis.exam.name,
                    'patologo_id' : analysis.patologo_id,
                    'patologo__first_name' : analysis.patologo.first_name if analysis.patologo else None,
                    'patologo__last_name' : analysis.patologo.first_name if analysis.patologo else None,
                    'service_comments': []
                }

                for cmm in analysis.service_comments.all():
                    aux['service_comments'].append({
                        'text': cmm.text,
                        'created_at': cmm.created_at.strftime('%d/%m/%Y %H:%M:%S'),
                        'done_by': cmm.done_by.get_full_name()
                    })
                
                entryform["analyses"].append(aux)
            
            entryform["cassettes"] = list(
                entryform_object.cassette_set.all().values())
            entryform["customer"] = model_to_dict(entryform_object.customer) if entryform_object.customer else None
            entryform["larvalstage"] = model_to_dict(entryform_object.larvalstage) if entryform_object.larvalstage else None
            entryform["fixative"] = model_to_dict(entryform_object.fixative) if entryform_object.fixative else None
            entryform["entryform_type"] = model_to_dict(entryform_object.entryform_type) if entryform_object.entryform_type else None
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
            entryform_types = list(EntryForm_Type.objects.all().values())

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
                'patologos': patologos,
                'entryform_types_list': entryform_types
            }
        else:
            species = list(Specie.objects.all().values())
            larvalStages = list(LarvalStage.objects.all().values())
            fixtatives = list(Fixative.objects.all().values())
            waterSources = list(WaterSource.objects.all().values())
            exams = list(Exam.objects.all().values())
            organs = list(Organ.objects.all().values())
            customers = list(Customer.objects.all().values())
            entryform_types = list(EntryForm_Type.objects.all().values())

            data = {
                'species': species,
                'larvalStages': larvalStages,
                'fixtatives': fixtatives,
                'waterSources': waterSources,
                'exams': exams,
                'organs': organs,
                'customers': customers,
                'entryform_types': entryform_types
            }
        # print (data)
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

        # no_slice = len(analyses)

        cassettes_qs = Cassette.objects.filter(
            entryform=entry_form).prefetch_related(Prefetch('organs'))
        cassettes = []

        for cassette in cassettes_qs:
            organs = [organ.name for organ in cassette.organs.all()]
            slices = []

            for slic in Slice.objects.filter(cassette=cassette):
                _slice_mtd = model_to_dict(slic)
                _slice_mtd['exam'] = slic.analysis.exam.name
                slices.append(_slice_mtd)

            samples_as_dict = []
            for s in cassette.samples.all():
                s_dict = model_to_dict(s, exclude=['organs', 'exams', 'identification','organs_before_validations'])
                organs_set = []
                exams_set = []
                for sampleExam in s.sampleexams_set.all():
                    organs_set.append(model_to_dict(sampleExam.organ))
                    if sampleExam.exam.service_id in [1,2,3]:
                        exams_set.append(model_to_dict(sampleExam.exam))
                # cassettes_set = Cassette.objects.filter(sample=s).values()
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
                            'exam_type': sE.exam.service_id,
                            'sample_id': sE.sample_id,
                            'organ_id': [{
                                'name':sE.organ.name,
                                'id':sE.organ.id}]
                        }
                    # organs.append(model_to_dict(sE.organ))
                # s_dict['organs_set'] = organs
                # s_dict['exams_set'] = list(exams)
                s_dict['sample_exams_set'] = sampleExa
                s_dict['organs_set'] = list(organs_set)
                # s_dict['exams_set'] = list(exams_set)
                # s_dict['cassettes_set'] = list(cassettes_set)
                s_dict['identification'] = model_to_dict(s.identification, exclude=["organs", 'organs_before_validations'])
                samples_as_dict.append(s_dict)
            
            cassette_as_dict = model_to_dict(cassette, exclude=['organs', 'organs_before_validations', 'samples'])
            cassette_as_dict['slices_set'] = slices
            cassette_as_dict['organs_set'] = organs
            cassette_as_dict['samples_set'] = samples_as_dict

            cassettes.append(cassette_as_dict)
        
        entryform = EntryForm.objects.values().get(pk=entry_form)
        entryform_object = EntryForm.objects.get(pk=entry_form)
        subflow = entryform_object.get_subflow
        entryform["subflow"] = subflow
        identifications = list(
            Identification.objects.filter(
                entryform=entryform['id']).values())
        
        samples = Sample.objects.filter(
                entryform=entryform['id']).order_by('index')
        
        samples_as_dict = []
        for s in samples:
            s_dict = model_to_dict(s, exclude=['organs', 'exams', 'identification','organs_before_validations'])
            organs_set = []
            exams_set = []
            for sampleExam in s.sampleexams_set.all():
                organs_set.append(model_to_dict(sampleExam.organ))
                if sampleExam.exam.service_id in [1,2,3]:
                    exams_set.append(model_to_dict(sampleExam.exam))
            # cassettes_set = Cassette.objects.filter(sample=s).values()
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
                        'exam_type': sE.exam.service_id,
                        'sample_id': sE.sample_id,
                        'organ_id': [{
                            'name':sE.organ.name,
                            'id':sE.organ.id}]
                    }
                # organs.append(model_to_dict(sE.organ))
            # s_dict['organs_set'] = organs
            # s_dict['exams_set'] = list(exams)
            s_dict['sample_exams_set'] = sampleExa
            s_dict['organs_set'] = list(organs_set)
            # s_dict['exams_set'] = list(exams_set)
            # s_dict['cassettes_set'] = list(cassettes_set)
            s_dict['identification'] = model_to_dict(s.identification, exclude=["organs", 'organs_before_validations'])
            samples_as_dict.append(s_dict)

        entryform["identifications"] = []
        for ident in entryform_object.identification_set.all():
            ident_json = model_to_dict(ident, exclude=["organs", 'organs_before_validations'])
            ident_json['organs_set'] = list(ident.organs.all().values())
            entryform["identifications"].append(ident_json)           
        # entryform["answer_questions"] = list(
        #     entryform_object.answerreceptioncondition_set.all().values())
        entryform["analyses"] = list(
            entryform_object.analysisform_set.all().values('id', 'created_at', 'comments', 'entryform_id', 'exam_id', 'exam__name', 'patologo_id', 'patologo__first_name', 'patologo__last_name'))
        entryform["cassettes"] = list(
            entryform_object.cassette_set.all().values())
        entryform["customer"] = model_to_dict(entryform_object.customer) if entryform_object.customer else None
        entryform["larvalstage"] = model_to_dict(entryform_object.larvalstage) if entryform_object.larvalstage else None
        entryform["fixative"] = model_to_dict(entryform_object.fixative) if entryform_object.fixative else None
        entryform["watersource"] = model_to_dict(entryform_object.watersource) if entryform_object.watersource else None
        entryform["specie"] = model_to_dict(entryform_object.specie) if entryform_object.specie else None
        
        organs_set = list(Organ.objects.all().values())
        exams_set = list(Exam.objects.all().values())
        species_list = list(Specie.objects.all().values())
        larvalStages_list = list(LarvalStage.objects.all().values())
        fixtatives_list = list(Fixative.objects.all().values())
        waterSources_list = list(WaterSource.objects.all().values())
        customers_list = list(Customer.objects.all().values())
        patologos = list(User.objects.filter(userprofile__profile_id__in=[4, 5]).values())
        entryform_types = list(EntryForm_Type.objects.all().values())

        data = {
            'cassettes': cassettes,
            'exams_set': exams_set,
            'exams': exams,
            'analyses': analyses,
            'entryform':entryform,
            'samples': samples_as_dict,
            'organs': organs_set,
            'species_list': species_list,
            'larvalStages_list': larvalStages_list,
            'fixtatives_list': fixtatives_list,
            'waterSources_list': waterSources_list,
            'customers_list': customers_list,
            'patologos': patologos,
            'entryform_types_list': entryform_types
         }

        return JsonResponse(data)


class ANALYSIS(View):
    def get(self, request, entry_form=None):
        analyses_qs = AnalysisForm.objects.filter(entryform=entry_form)
        analyses = []

        for analysis in analyses_qs:
            if request.user.userprofile.profile_id == 5:
                if analysis.patologo_id != request.user.id:
                    continue
            exam = analysis.exam
            form = analysis.forms.get()

            form_id = form.id

            current_step_tag = form.state.step.tag
            current_step = form.state.step.order
            total_step = form.flow.step_set.count()

            if exam.service_id == 2:
                total_step = 2
                percentage_step = (int(current_step) / int(total_step)) * 100
            elif exam.service_id in [3,4,5]:
                total_step = 0
                percentage_step = 0
            else:
                percentage_step = (int(current_step) / int(total_step)) * 100

            slices_qs = analysis.slice_set.all()
            slices = []
            for slice_new in slices_qs:
                slices.append({'name': slice_new.slice_name})

            analyses.append({
                'form_id': form_id,
                'id': analysis.id,
                'exam_name': exam.name,
                'exam_stain': exam.stain,
                'exam_type': exam.service_id,
                'slices': slices,
                'current_step_tag': current_step_tag,
                'current_step': current_step,
                'total_step': total_step,
                'percentage_step': percentage_step,
                'form_closed': form.form_closed,
                'form_reopened': form.form_reopened,
                'service': exam.service_id,
                'service_name': exam.service.name,
                'cancelled': form.cancelled,
                'patologo_name': analysis.patologo.get_full_name() if analysis.patologo else ""
                # 'no_caso': analisys.entry_form.no_caso
            })
        
        
        entryform = EntryForm.objects.values().get(pk=entry_form)
        entryform_object = EntryForm.objects.get(pk=entry_form)
        subflow = entryform_object.get_subflow
        entryform["subflow"] = subflow
        identifications = list(
            Identification.objects.filter(
                entryform=entryform['id']).values())
        
        samples = Sample.objects.filter(
                entryform=entryform['id']).order_by('index')
        
        samples_as_dict = []
        for s in samples:
            s_dict = model_to_dict(s, exclude=['organs', 'exams', 'identification', 'organs_before_validations'])
            organs = []
            sampleexams = s.sampleexams_set.all()
            sampleExa = {}
            for sE in sampleexams:
                if sE.exam.service_id in [1,2,3]:
                    if sE.organ in s.identification.organs_before_validations.all():
                        try:
                            organs.index(model_to_dict(sE.organ))
                        except:
                            organs.append(model_to_dict(sE.organ))
                    else:
                        for org in s.identification.organs_before_validations.all():
                            if org.organ_type == 2:
                                try:
                                    organs.index(model_to_dict(org))
                                except:
                                    organs.append(model_to_dict(org))
            organs_set = organs
            # exams_set = s.exams.all().values()
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
                        'exam_type': sE.exam.service_id,
                        'sample_id': sE.sample_id,
                        'organ_id': [{
                            'name':sE.organ.name,
                            'id':sE.organ.id}]
                    }
                # organs.append(model_to_dict(sE.organ))
            s_dict['sample_exams_set'] = sampleExa
            # cassettes_set = Cassette.objects.filter(sample=s).values()
            s_dict['organs_set'] = list(organs_set)
            # s_dict['exams_set'] = list(exams_set)
            # s_dict['cassettes_set'] = list(cassettes_set)
            s_dict['identification'] = model_to_dict(s.identification, exclude=["organs", 'organs_before_validations'])
            samples_as_dict.append(s_dict)

        entryform["identifications"] = []
        for ident in entryform_object.identification_set.all():
            ident_json = model_to_dict(ident, exclude=["organs", 'organs_before_validations'])
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

        organs_set = list(Organ.objects.all().values())
        exams_set = list(Exam.objects.all().values())

        species_list = list(Specie.objects.all().values())
        larvalStages_list = list(LarvalStage.objects.all().values())
        fixtatives_list = list(Fixative.objects.all().values())
        waterSources_list = list(WaterSource.objects.all().values())
        customers_list = list(Customer.objects.all().values())
        patologos = list(User.objects.filter(userprofile__profile_id__in=[4, 5]).values())
        entryform_types = list(EntryForm_Type.objects.all().values())

        data = {
            'analyses': analyses,
            'entryform':entryform,
            'samples': samples_as_dict,
            'exams_set': exams_set,
            'organs': organs_set,
            'species_list': species_list,
            'larvalStages_list': larvalStages_list,
            'fixtatives_list': fixtatives_list,
            'waterSources_list': waterSources_list,
            'customers_list': customers_list,
            'patologos': patologos,
            'entryform_types_list': entryform_types
        }
        
        return JsonResponse(data)


class SLICE(View):
    def get(self, request, analysis_form=None):
        slices_qs = Slice.objects.filter(analysis=analysis_form)
        slices = []

        for slice_new in slices_qs:
            slice_as_dict = model_to_dict(slice_new, exclude=['cassette'])
            slice_as_dict['cassette'] = model_to_dict(slice_new.cassette, exclude=['organs', 'organs_before_validations', 'samples'])
            slice_as_dict['organs'] = list(slice_new.cassette.organs.all().values())
            samples_as_dict = []
            for s in slice_new.cassette.samples.all():
                s_dict = model_to_dict(s, exclude=['organs', 'exams', 'identification','organs_before_validations'])
                organs_set = []
                exams_set = []
                for sampleExam in s.sampleexams_set.all():
                    organs_set.append(model_to_dict(sampleExam.organ))
                    if sampleExam.exam.service_id in [1,2,3]:
                        exams_set.append(model_to_dict(sampleExam.exam))
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
                            'exam_type': sE.exam.service_id,
                            'sample_id': sE.sample_id,
                            'organ_id': [{
                                'name':sE.organ.name,
                                'id':sE.organ.id}]
                        }
                s_dict['sample_exams_set'] = sampleExa
                s_dict['organs_set'] = list(organs_set)

                s_dict['identification'] = model_to_dict(s.identification, exclude=["organs", 'organs_before_validations'])
                samples_as_dict.append(s_dict)
            
            slice_as_dict['samples'] = samples_as_dict
            slice_as_dict['paths_count'] = Report.objects.filter(slice_id=slice_new.pk).count()
            slice_as_dict['analysis_exam'] = slice_new.analysis.exam.id
            slices.append(slice_as_dict)

        analysis_form = AnalysisForm.objects.get(pk=analysis_form)
        entryform = EntryForm.objects.values().get(pk=analysis_form.entryform.pk)
        entryform_object = EntryForm.objects.get(pk=analysis_form.entryform.pk)
        subflow = entryform_object.get_subflow
        entryform["subflow"] = subflow
        # identifications = list(
        #     Identification.objects.filter(
        #         entryform=entryform['id']).values())
        
        samples = Sample.objects.filter(
                entryform=entryform['id']).order_by('index')
        
        samples_as_dict = []
        for s in samples:
            s_dict = model_to_dict(s, exclude=['organs', 'exams', 'identification','organs_before_validations'])
            organs_set = []
            exams_set = []
            for sampleExam in s.sampleexams_set.all():
                if sampleExam.exam == analysis_form.exam:
                    organs_set.append(model_to_dict(sampleExam.organ))
                    exams_set.append(model_to_dict(sampleExam.exam))

            if len(exams_set) > 0:
            # cassettes_set = Cassette.objects.filter(sample=s).values()
                s_dict['organs_set'] = list(organs_set)
                
                cassettes = Cassette.objects.filter(samples__in=[s]).values_list('id', flat=True)

                exam_slices = Slice.objects.filter(cassette__in=cassettes, analysis=analysis_form)

                s_dict['exam_slices_set'] = []
                for l in exam_slices:
                    exam_slice = model_to_dict(l)
                    exam_slice['paths_count'] = Report.objects.filter(slice_id=l.pk, sample_id=s.id).count()
                    exam_slice['analysis_exam'] = l.analysis.exam.id
                    s_dict['exam_slices_set'].append(exam_slice)
                # s_dict['cassettes_set'] = list(cassettes_set)
                s_dict['identification'] = model_to_dict(s.identification, exclude=["organs", 'organs_before_validations'])
                samples_as_dict.append(s_dict)

        entryform["identifications"] = []
        for ident in entryform_object.identification_set.all():
            ident_json = model_to_dict(ident, exclude=["organs", 'organs_before_validations'])
            ident_json['organs_set'] = list(ident.organs.all().values())
            entryform["identifications"].append(ident_json)   

        entryform["analyses"] = list(
            entryform_object.analysisform_set.all().values('id', 'created_at', 'comments', 'entryform_id', 'exam_id', 'exam__name', 'patologo_id', 'patologo__first_name', 'patologo__last_name'))
        entryform["cassettes"] = list(
            entryform_object.cassette_set.all().values())
        entryform["customer"] = entryform_object.customer.name if entryform_object.customer else ""
        entryform["larvalstage"] = entryform_object.larvalstage.name if entryform_object.larvalstage else ""
        entryform["fixative"] = entryform_object.fixative.name if entryform_object.fixative else ""
        entryform["watersource"] = entryform_object.watersource.name if entryform_object.watersource else ""
        entryform["specie"] = entryform_object.specie.name if entryform_object.specie else ""
        organs_set = list(Organ.objects.all().values())
        exams_set = list(Exam.objects.all().values())
        

        data = {'slices': slices, 'entryform': entryform, 'samples': samples_as_dict, 'organs': organs_set, 'exams_set': exams_set}

        return JsonResponse(data)

class WORKFLOW(View):
    http_method_names = ['get', 'post', 'delete']
    
    def sortReport(self, report):
        return report.organ_id

    @method_decorator(login_required)
    def get(self, request, form_id, step_tag=None):
        form = Form.objects.get(pk=form_id)
        if not step_tag:
            step_tag = form.state.step.tag
        object_form_id = form.content_object.id

        actor = Actor.objects.filter(profile_id=request.user.userprofile.profile_id).first()
        if (form.content_type.name == 'entry form'):
            # Fix patch state id non-correlative from step_3 > id : 5
            if step_tag == "step_3":
                state_id = 5
            else:
                state_id = step_tag.split('_')[1]
            permisos =  actor.permission.filter(from_state_id=state_id)
            edit = 1 if permisos.filter(type_permission='w').first() else 0
            route = 'app/workflow_main.html'

            close_allowed = 1
            closed = 0
            if form.form_closed or form.cancelled:
                close_allowed = 0
                closed = 1
            else:
                childrens = Form.objects.filter(parent_id=form)
                for ch in childrens:
                    if not ch.form_closed and not ch.cancelled:
                        close_allowed = 0
                        break

            data = {
                'form': form,
                'form_id': form_id,
                'entryform_id': object_form_id,
                'set_step_tag': step_tag,
                'edit': edit,
                'closed': closed,
                'close_allowed': close_allowed
            }

            print (data)
        elif (form.content_type.name == 'analysis form'):
            reopen = False
            analisis = AnalysisForm.objects.get(id=int(object_form_id))
            if step_tag == 'step_6':
                if analisis.exam.service_id == 1:
                    step_tag = 'step_5'
                elif analisis.exam.service_id == 2:
                    step_tag = 'step_2'
                    
                reopen = True
               
                
            permisos =  actor.permission.filter(from_state_id=int(step_tag.split('_')[1]) + 6)
            if permisos:
                edit = 1 if permisos.filter(type_permission='w').first() else 0
            else:
                return redirect(app_view.show_ingresos)

            if reopen:
                if not edit and not form.form_reopened:
                    return redirect(app_view.show_ingresos)
                form.form_closed = False
                form.form_reopened = True
                form.save()
                
            route = 'app/workflow_analysis.html'
            
            reports = Report.objects.filter(analysis_id=int(object_form_id))
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
                value.sort(key=self.sortReport)
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
            
            report_finalExtra = ReportFinal.objects.filter(analysis_id=int(object_form_id)).last()

            data = {
                'form': form,
                'analisis': analisis,
                'form_id': form_id,
                'analysis_id': object_form_id,
                'set_step_tag': step_tag,
                'exam_name': form.content_object.exam.name,
                'histologico': form.content_object.exam.service_id,
                'form_parent_id': form.parent.id,
                'entryform_id': analisis.entryform_id,
                'report': reports,
                'reports2': data,
                'reopen': reopen,
                'report_finalExtra': report_finalExtra,
                'edit': edit
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
            
            actor_user = None
            next_state = None
            for actor in next_step.actors.all():
                if actor.profile == up.profile:
                    actor_user = actor
                    if previous_step:
                        next_state = Permission.objects.get(to_state=form.state, type_permission='w').from_state
                    else:
                        # fix para saltar bloque cassete slice flujo prinicpal

                        if form.state_id == 3 and int(id_next_step) == 5:
                            next_state = State.objects.get(pk=5)
                        else:
                            next_state = actor.permission.get(
                                from_state=form.state, type_permission='w').to_state
                    break

            if not previous_step:
                process_answer = call_process_method(form.content_type.model,
                                                     request)
                next_step_permission = next_state.id != 1 and not len(actor_user.permission.filter(to_state=next_state, type_permission='w'))
            else:
                next_step_permission = next_state.id != 1 and not len(actor_user.permission.filter(from_state=next_state, type_permission='w'))
                form.form_reopened = False
            # for actor in next_state.step.actors.all():
            #     if actor.profile == up.profile:
            #         next_step_permission = True
            if process_answer and next_state:
                current_state = form.state
                form.state = next_state
                form.save()
                if next_step_permission:
                    return redirect(app_view.show_ingresos)
                next_step_permission = not next_step_permission
                process_response = True
                # sendEmailNotification(form, current_state, next_state)
            else:
                print("FALLO EL PROCESAMIENTO")
                return redirect(app_view.show_ingresos)

            return JsonResponse({
                'process_response': process_response,
                'next_step_permission': next_step_permission
            })
        else:
            process_answer = call_process_method(form.content_type.model,
                                                     request)
            

            form.form_closed = False
            
            form.form_reopened = False
            form.save()

            return JsonResponse({'redirect_flow': True})

    def delete(self, request, form_id):
        form =  Form.objects.get(pk=form_id)
        form.cancelled = True
        form.cancelled_at = datetime.now()
        form.save()
        forms = Form.objects.filter(parent_id=form_id, form_closed=False, cancelled=False)
        for f in forms:
            f.cancelled = True
            f.cancelled_at = datetime.now()
            f.save()
        # object_form_id = form.content_object.id
        return JsonResponse({'ok': True})

class REPORT(View):

    def get(self, request, slice_id=None, analysis_id=None):
        if slice_id:
            report_qs = Report.objects.filter(slice=slice_id)
            reports = []
            for report in report_qs:
                organ = report.organ.name if report.organ else ""
                organ_location = report.organ_location.name if report.organ_location else ""
                pathology = report.pathology.name if report.pathology else ""
                diagnostic = report.diagnostic.name if report.diagnostic else ""
                diagnostic_distribution = report.diagnostic_distribution.name if report.diagnostic_distribution else ""
                diagnostic_intensity = report.diagnostic_intensity.name if report.diagnostic_intensity else ""
                image_list = []
                for img in report.images.all():
                    image_list.append({
                        'name': img.file.name.split("/")[-1],
                        'url': img.file.url,
                        'id': img.id
                    })

                reports.append({
                    "report_id": report.id,
                    "organ": organ,
                    "organ_location": organ_location,
                    "pathology": pathology,
                    "diagnostic": diagnostic,
                    "diagnostic_distribution": diagnostic_distribution,
                    "diagnostic_intensity": diagnostic_intensity,
                    "images": image_list
                })

            data = {'reports': reports}

        if analysis_id:
            report_qs = Report.objects.filter(analysis_id=analysis_id)
            reports = []
            for report in report_qs:
                image_list = []
                for img in report.images.all():
                    image_list.append({
                        'name': img.file.name.split("/")[-1],
                        'url': img.file.url,
                        'id': img.id
                    })

                reports.append({
                    "report_id": report.id,
                    "organ": model_to_dict(report.organ),
                    "organ_location": model_to_dict(report.organ_location, exclude=["organs"]),
                    "pathology": model_to_dict(report.pathology, exclude=["organs"]),
                    "diagnostic": model_to_dict(report.diagnostic, exclude=["organs"]),
                    "diagnostic_distribution": model_to_dict(report.diagnostic_distribution, exclude=["organs"]),
                    "diagnostic_intensity": model_to_dict(report.diagnostic_intensity, exclude=["organs"]),
                    "images": image_list,
                    "identification": model_to_dict(report.identification, exclude=["organs"]),
                    "analysis": model_to_dict(report.analysis, exclude=["exam"]),
                    "exam": model_to_dict(report.analysis.exam)
                })
            
            analysis_form = AnalysisForm.objects.get(pk=analysis_id)
            entryform = EntryForm.objects.values().get(pk=analysis_form.entryform.pk)
            entryform_object = EntryForm.objects.get(pk=analysis_form.entryform.pk)
            subflow = entryform_object.get_subflow
            entryform["subflow"] = subflow
            identifications = list(
                Identification.objects.filter(
                    entryform=entryform['id']).values())
            
            samples = Sample.objects.filter(
                    entryform=entryform['id']).order_by('index')
            
            samples_as_dict = []
            for s in samples:
                s_dict = model_to_dict(s, exclude=['organs', 'exams', 'cassettes', 'identification'])
                # organs_set = s.organs.all().values()
                # exams_set = s.exams.all().values()
                # cassettes_set = Cassette.objects.filter(sample=s).values()
                # s_dict['organs_set'] = list(organs_set)
                # s_dict['exams_set'] = list(exams_set)
                # s_dict['cassettes_set'] = list(cassettes_set)
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
                            'exam_type': sE.exam.service_id,
                            'sample_id': sE.sample_id,
                            'organ_id': [{
                            'name':sE.organ.name,
                            'id':sE.organ.id}]
                        }
                    if sE.exam.service_id in [1,2,3]:
                        if sE.organ in s.identification.organs_before_validations.all():
                            try:
                                organs.index(model_to_dict(sE.organ))
                            except:
                                organs.append(model_to_dict(sE.organ))
                        else:
                            for org in s.identification.organs_before_validations.all():
                                if org.organ_type == 2:
                                    try:
                                        organs.index(model_to_dict(org))
                                    except:
                                        organs.append(model_to_dict(org))
                s_dict['organs_set'] = organs
                s_dict['exams_set'] = sampleExa
                cassettes_set = []
                cassettes = Cassette.objects.filter(sample=s)
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
                s_dict['identification'] = model_to_dict(s.identification)
                samples_as_dict.append(s_dict)

            entryform["identifications"] = list(
                entryform_object.identification_set.all().values())
            # entryform["answer_questions"] = list(
            #     entryform_object.answerreceptioncondition_set.all().values())
            entryform["analyses"] = list(
                entryform_object.analysisform_set.all().values())
            entryform["cassettes"] = list(
                entryform_object.cassette_set.all().values())
            entryform["customer"] = entryform_object.customer.name if entryform_object.customer else ""
            entryform["larvalstage"] = entryform_object.larvalstage.name if entryform_object.larvalstage else ""
            entryform["fixative"] = entryform_object.fixative.name if entryform_object.fixative else ""
            entryform["watersource"] = entryform_object.watersource.name if entryform_object.watersource else ""
            entryform["specie"] = entryform_object.specie.name if entryform_object.specie else ""

            data = {'reports': reports, "entryform": entryform}
        return JsonResponse(data)

    def post(self, request):
        var_post = request.POST.copy()

        analysis_id = var_post.get('analysis_id')
        slice_id = var_post.get('slice_id')
        sample_id = var_post.get('sample_id')
        organ_id = var_post.get('organ')
        organ_location_id = var_post.get('organ_location')
        pathology_id = var_post.get('pathology')
        diagnostic_id = var_post.get('diagnostic')
        diagnostic_distribution_id = var_post.get('diagnostic_distribution')
        diagnostic_intensity_id = var_post.get('diagnostic_intensity')

        sample = Sample.objects.get(pk=sample_id)
        report = Report.objects.create(
            analysis_id=analysis_id,
            slice_id=slice_id,
            sample=sample,
            organ_id=organ_id,
            organ_location_id=organ_location_id,
            pathology_id=pathology_id,
            diagnostic_id=diagnostic_id,
            diagnostic_distribution_id=diagnostic_distribution_id,
            diagnostic_intensity_id=diagnostic_intensity_id,
            identification=sample.identification
        )
        report.save()

        return JsonResponse({'ok': True})

    def delete(self, request, report_id):
        if report_id:
            report = Report.objects.get(pk=report_id)
            report.delete()

        return JsonResponse({'ok': True})

class IMAGES(View):
    
    def post(self, request, report_id):
        try:
            if report_id:
                report = Report.objects.get(pk=report_id)
                var_post = request.POST.copy()
                desc = var_post.get('comments')
                img_file = request.FILES['file']
                img = Img.objects.create(
                    file = img_file,
                    desc = desc,
                )
                report.images.add(img)
                return JsonResponse({'ok': True, 'img_url': img.file.url, 'img_name': img.file.name.split('/')[-1]})
            else:
                return JsonResponse({'ok': False})
        except:
             return JsonResponse({'ok': False})

class RESPONSIBLE(View):
    http_method_names = ['get', 'post', 'delete']
    
    def get(self, request):
        responsibles = Responsible.objects.filter(active=True)
        data = []
        for r in responsibles:
            data.append(model_to_dict(r))

        return JsonResponse({'ok': True, 'responsibles': data})

    def post(self, request):
        try:
            var_post = request.POST.copy()
            responsible = Responsible()
            id = var_post.get('id', None)
            if id:
                responsible.id = id
            responsible.name = var_post.get('name', None)
            responsible.email = var_post.get('email', None)
            responsible.phone = var_post.get('phone', None)
            responsible.job = var_post.get('job', None)
            responsible.active = var_post.get('active', True)
            responsible.save()
            return JsonResponse({'ok': True})
        except Exception as e:
             return JsonResponse({'ok': False})
    
    def delete(self, request, id):
        responsible = Responsible.objects.get(pk=id)
        responsible.active = False
        responsible.save()

        return JsonResponse({'ok': True})

class SERVICE_REPORTS(View):
    http_method_names = ['get', 'post', 'delete']
    
    def get(self, request, analysis_id):
        af = AnalysisForm.objects.get(pk=analysis_id)

        data = []
        for report in af.external_reports.all().order_by('-created_at'):
            data.append({'id': report.id, 'path': report.file.url, 'name': report.file.name.split("/")[-1]})

        return JsonResponse({'ok': True, 'reports': data})

    def post(self, request, analysis_id):
        try:
            if analysis_id:
                af = AnalysisForm.objects.get(pk=analysis_id)
                file_report = request.FILES['file']
                external_report = ExternalReport.objects.create(
                    file = file_report,
                    loaded_by = request.user
                )
                af.external_reports.add(external_report)
                return JsonResponse({'ok': True, 'file': {'id': external_report.id, 'path': external_report.file.url, 'name': external_report.file.name.split("/")[-1]} })
            else:
                return JsonResponse({'ok': False})
        except:
             return JsonResponse({'ok': False})

    
    def delete(self, request, analysis_id, id):
        try:
            report = ExternalReport.objects.get(pk=id)
            af = AnalysisForm.objects.get(pk=analysis_id)
            af.external_reports.remove(report)
            return JsonResponse({'ok': True})
        except:
            return JsonResponse({'ok': False})

class SERVICE_COMMENTS(View):
    http_method_names = ['get', 'post', 'delete']
    
    def get(self, request, analysis_id):
        af = AnalysisForm.objects.get(pk=analysis_id)

        data = []
        for cmm in af.service_comments.all().order_by('-created_at'):
            response = {
                'id': cmm.id,
                'text': cmm.text,
                'created_at': cmm.created_at.strftime('%d/%m/%Y %H:%M:%S'),
                'done_by': cmm.done_by.get_full_name()
            }
            data.append(response)

        return JsonResponse({'ok': True, 'comments': data})

    def post(self, request, analysis_id):
        try:
            if analysis_id:
                af = AnalysisForm.objects.get(pk=analysis_id)
                var_post = request.POST.copy()
                comment = var_post.get('comment', None)
                if comment:
                    service_comment = ServiceComment.objects.create(
                        text = comment,
                        done_by = request.user
                    )
                    af.service_comments.add(service_comment)
                    response = {
                        'id': service_comment.id,
                        'text': service_comment.text,
                        'created_at': service_comment.created_at.strftime('%d/%m/%Y %H:%M:%S'),
                        'done_by': service_comment.done_by.get_full_name()
                    }
                    return JsonResponse({'ok': True, 'comment': response})
                else:
                    return JsonResponse({'ok': True})
            else:
                return JsonResponse({'ok': False})
        except:
             return JsonResponse({'ok': False})

    
    def delete(self, request, analysis_id, id):
        try:
            sc = ServiceComment.objects.get(pk=id)
            af = AnalysisForm.objects.get(pk=analysis_id)
            af.service_comments.remove(sc)
            return JsonResponse({'ok': True})
        except:
            return JsonResponse({'ok': False})
   
class EMAILTEMPLATE(View):
    def get(self, request, id=None):
        if id:
            template = EmailTemplate.objects.get(pk=id)
            data = model_to_dict(template)
            return JsonResponse({'ok': True, 'template': data})
        else:
            var_get = request.GET.copy()
            entryform = EntryForm.objects.get(pk=var_get['form'])
            responsible = Responsible.objects.filter(name=entryform.responsible).first()
            email = ''
            if responsible:
                email = responsible.email
            templates = EmailTemplate.objects.all()
            data = []
            for r in templates:
                data.append(model_to_dict(r))

            return JsonResponse({'ok': True, 'templates': data, 'email': email})

    def post(self, request):
        try:
            var_post = request.POST.copy()
            from app import views as appv
            lang = var_post.get('lang', 'es')
            formId = var_post.get('formId')
            doc = appv.get_resume_file(request.user, formId, lang)
            center = doc.entryform.center if doc.entryform.center else ""
            subject = "Recepción de muestras/"+doc.entryform.no_caso+"/"+center
            from_email = settings.EMAIL_HOST_USER
            to = var_post.get('to').split(',')
            message = var_post.get('body')
            plantilla = var_post.get('plantilla')

            msg = EmailMultiAlternatives(subject, message, from_email, to)
            files = EmailTemplateAttachment.objects.filter(template=plantilla)
            for f in files:
                msg.attach_file(f.template_file.path)

            if settings.DEBUG:
                file_path = settings.BASE_DIR + settings.MEDIA_URL + "pdfs/"
            else:
                file_path = settings.MEDIA_ROOT + "/pdfs/"
            
            with open(file_path + "" + str(doc.file), 'rb') as pdf:
                msg.attach(doc.filename, pdf.read(), 'application/pdf')

            msg.send()

            DocumentResumeActionLog.objects.create(
                document=doc,
                mail_action=True,
                done_by=request.user
            )
            return JsonResponse({'ok': True})
        except Exception as e:
            print (e)
            return JsonResponse({'ok': False})

class CASE_FILES(View):
    http_method_names = ['get', 'post', 'delete']
    
    def get(self, request, entryform_id):
        ef = EntryForm.objects.get(pk=entryform_id)

        data = []
        for file in ef.attached_files.all().order_by('-created_at'):
            data.append({'id': file.id, 'path': file.file.url, 'name': file.file.name.split("/")[-1]})

        return JsonResponse({'ok': True, 'files': data})

    def post(self, request, entryform_id):
        try:
            if entryform_id:
                ef = EntryForm.objects.get(pk=entryform_id)
                file = request.FILES['file']
                case_file = CaseFile.objects.create(
                    file = file,
                    loaded_by = request.user
                )
                ef.attached_files.add(case_file)
                return JsonResponse({'ok': True, 'file': {'id': case_file.id, 'path': case_file.file.url, 'name': case_file.file.name.split("/")[-1]} })
            else:
                return JsonResponse({'ok': False})
        except:
             return JsonResponse({'ok': False})

    
    def delete(self, request, entryform_id, id):
        try:
            file = CaseFile.objects.get(pk=id)
            ef = EntryForm.objects.get(pk=entryform_id)
            ef.attached_files.remove(file)
            return JsonResponse({'ok': True})
        except:
            return JsonResponse({'ok': False})

def organs_by_slice(request, slice_id=None, sample_id=None):
    if slice_id and sample_id:
        slice_obj = Slice.objects.get(
            pk=slice_id)

        sample = Sample.objects.get(pk=sample_id)
        sampleExa = {}

        for sE in sample.sampleexams_set.all():
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

        organs = []
        for key, value in sampleExa.items():
            if key == slice_obj.analysis.exam.id:
                for organ in value['organ_id']:
                    # print (organ)
                    # ESTE IF NO DEBERIA APLICAR CON EL FIX DE ORGANOS EN CONJUNTO, DEBERIAN YA ESTAR TODOS LOS ORGANOS
                    
                    # if organ['name'].upper() == "ALEVÍN" or organ['name'].upper() == "LARVA":
                    #     all_organs = Organ.objects.all()
                    #     for organ in all_organs:
                    #         organs.append({
                    #             "id":
                    #             organ.id,
                    #             "name":
                    #             organ.name.upper(),
                    #             "organ_locations":
                    #             list(organ.organlocation_set.all().values()),
                    #             "pathologys":
                    #             list(organ.pathology_set.all().values()),
                    #             "diagnostics":
                    #             list(organ.diagnostic_set.all().values()),
                    #             "diagnostic_distributions":
                    #             list(organ.diagnosticdistribution_set.all().values()),
                    #             "diagnostic_intensity":
                    #             list(organ.diagnosticintensity_set.all().values())
                    #         })
                    # else:
                    organ = Organ.objects.get(pk=organ['id'])
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
        analysis.comments = comments
        analysis.save()
        return JsonResponse({'ok': True})
    except:
        return JsonResponse({'ok': False})

def save_block_timing(request):
    try:
        var_post = request.POST.copy()

        block_cassette_pk = [
            v for k, v in var_post.items() if k.startswith("block_cassette_pk")
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

        zip_block = zip(block_cassette_pk, block_start_block, block_end_block, block_start_slice, block_end_slice)

        for values in zip_block:
            _slices = Slice.objects.filter(cassette=Cassette.objects.get(pk=values[0]))
            for _slice in _slices:
                if values[1] != '':
                    _slice.start_block = datetime.strptime(values[1], '%d/%m/%Y %H:%M:%S') or None
                if values[2] != '':
                    _slice.end_block = datetime.strptime(values[2], '%d/%m/%Y %H:%M:%S') or None
                if values[3] != '':
                    _slice.start_slice = datetime.strptime(values[3], '%d/%m/%Y %H:%M:%S') or None
                if values[4] != '':
                    _slice.end_slice = datetime.strptime(values[4], '%d/%m/%Y %H:%M:%S') or None
                _slice.save()
        return JsonResponse({'ok': True})
    except:
        return JsonResponse({'ok': False})

def save_stain_timing(request):
    try:
        var_post = request.POST.copy()

        stain_slice_id = [
            v for k, v in var_post.items() if k.startswith("stain_slice_id")
        ]
        stain_start_stain = [
            v for k, v in var_post.items() if k.startswith("stain_start_stain")
        ]
        stain_end_stain = [
            v for k, v in var_post.items() if k.startswith("stain_end_stain")
        ]

        zip_stain = zip(stain_slice_id, stain_start_stain, stain_end_stain)

        for values in zip_stain:
            slice_new = Slice.objects.get(pk=values[0])
            if values[1] != '':
                slice_new.start_stain = datetime.strptime(values[1], '%d/%m/%Y %H:%M:%S') or None
            if values[2] != '':
                slice_new.end_stain = datetime.strptime(values[2], '%d/%m/%Y %H:%M:%S') or None
            slice_new.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        print (e)
        return JsonResponse({'ok': False})

def save_scan_timing(request):
    try:
        var_post = request.POST.copy()

        scan_slice_id = [
            v for k, v in var_post.items() if k.startswith("scan_slice_id")
        ]
        scan_start_scan = [
            v for k, v in var_post.items() if k.startswith("scan_start_scan")
        ]
        scan_end_scan = [
            v for k, v in var_post.items() if k.startswith("scan_end_scan")
        ]
        scan_store = [
            v for k, v in var_post.items() if k.startswith("scan_store")
        ]

        zip_scan = zip(scan_slice_id, scan_start_scan, scan_end_scan, scan_store)

        for values in zip_scan:
            slice_new = Slice.objects.get(pk=values[0])
            if values[1] != '':
                slice_new.start_scan = datetime.strptime(values[1], '%d/%m/%Y %H:%M:%S') or None
            if values[2] != '':
                slice_new.end_scan = datetime.strptime(values[2], '%d/%m/%Y %H:%M:%S') or None
            if values[3] != '':
                slice_new.slice_store = values[3]

            slice_new.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        print (e)
        return JsonResponse({'ok': False})

# Any process function must to have a switcher for choice which method will be call
def process_entryform(request):
    step_tag = request.POST.get('step_tag')

    # try:
    switcher = {
        'step_1': step_1_entryform,
        'step_2': step_2_entryform,
        'step_3': step_3_entryform,
        'step_4': step_4_entryform,
        'step_3_new': step_new_analysis,
        'step_4_new': step_new_analysis2
    }

    method = switcher.get(step_tag)

    if not method:
        raise NotImplementedError(
            "Method %s_entryform not implemented" % step_tag)
    
    return method(request)

def process_analysisform(request):
    step_tag = request.POST.get('step_tag')

    # try:
    switcher = {
        'step_1': step_1_analysisform,
        'step_2': step_2_analysisform,
        'step_3': step_3_analysisform,
        'step_4': step_4_analysisform,
        'step_5': step_5_analysisform,
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
   
    entryform.analysisform_set.all().delete()
    Sample.objects.filter(entryform=entryform).delete()

    change = False
    if str(entryform.specie_id) != var_post.get('specie') and (entryform.specie_id == None and var_post.get('specie') != ''):
        change = True
    entryform.specie_id = var_post.get('specie')
    
    if str(entryform.watersource_id) != var_post.get('watersource') and (entryform.watersource_id == None and var_post.get('watersource') != ''):
        change = True
    entryform.watersource_id = var_post.get('watersource')
    
    if str(entryform.fixative_id) != var_post.get('fixative') and (entryform.fixative_id == None and var_post.get('fixative') != ''):
        change = True
    entryform.fixative_id = var_post.get('fixative')
    
    if str(entryform.larvalstage_id) != var_post.get('larvalstage') and (entryform.larvalstage_id == None and var_post.get('larvalstage') != ''):
        change = True
    entryform.larvalstage_id = var_post.get('larvalstage')
    
    # if str(entryform.observation) != var_post.get('observation') and (entryform.observation == None and var_post.get('observation') != ''):
    #     change = True
    # entryform.observation = var_post.get('observation')
    
    if str(entryform.customer_id) != var_post.get('customer') and (entryform.customer_id == None and var_post.get('customer') != ''):
        change = True
    entryform.customer_id = var_post.get('customer')

    if str(entryform.entryform_type_id) != var_post.get('entryform_type') and (entryform.entryform_type_id == None and var_post.get('entryform_type') != ''):
        change = True
    entryform.entryform_type_id = var_post.get('entryform_type')
    
    if str(entryform.no_order) != var_post.get('no_order') and (entryform.no_order == None and var_post.get('no_order') != ''):
        change = True
    entryform.no_order = var_post.get('no_order')

    # TODO: COMPROBAR LOS CAMBIOS DE HORARIO SERVER - BD
    try:
        if entryform.created_at != datetime.strptime(var_post.get('created_at'), '%d/%m/%Y %H:%M') and (entryform.created_at != datetime.strptime(var_post.get('created_at'), '%d/%m/%Y %H:%M') != ''):
            # change = True
            pass
        entryform.created_at = datetime.strptime(var_post.get('created_at'), '%d/%m/%Y %H:%M')
    except Exception as e: 
        pass
    try:
        if entryform.sampled_at != datetime.strptime(var_post.get('sampled_at'), '%d/%m/%Y %H:%M') and (entryform.sampled_at != datetime.strptime(var_post.get('sampled_at'), '%d/%m/%Y %H:%M') != ''):
             # change = True
            pass
        entryform.sampled_at = datetime.strptime(var_post.get('sampled_at'), '%d/%m/%Y %H:%M')
    except:
        pass

    if str(entryform.center) != var_post.get('center') and (entryform.center == None and var_post.get('center') != ''):
        change = True
    entryform.center = var_post.get('center')
    
    if str(entryform.responsible) != var_post.get('responsible') and (entryform.responsible == None and var_post.get('responsible') != ''):
        change = True
    entryform.responsible = var_post.get('responsible')
    
    if str(entryform.company) != var_post.get('company') and (entryform.company == None and var_post.get('company') != ''):
        change = True
    entryform.company = var_post.get('company')
    
    if str(entryform.no_request) != var_post.get('no_request') and (entryform.no_request == None and var_post.get('no_request') != ''):
        change = True
    entryform.no_request = var_post.get('no_request')

    if str(entryform.anamnesis) != var_post.get('anamnesis') and (entryform.anamnesis == None and var_post.get('anamnesis') != ''):
        change = True
    entryform.anamnesis = var_post.get('anamnesis')
    
    entryform.save()

    optimals = [
        v for k, v in dict(var_post).items() if k.startswith("identification[is_optimal]")
    ]

    organs = [
        list(v) for k, v in dict(var_post).items() if k.startswith("identification[organs]")
    ]
    identification_cage = var_post.getlist("identification[cage]")
    identification_group = var_post.getlist("identification[group]")
    identification_no_container = var_post.getlist("identification[no_container]")
    identification_no_fish = var_post.getlist("identification[no_fish]")
    identification_id = var_post.getlist("identification[id]")
    identification_weight = var_post.getlist("identification[weight]")
    identification_extra_features_detail = var_post.getlist("identification[extra_features_detail]")
    identification_is_optimal = optimals
    identification_observations = var_post.getlist("identification[observations]")
    identification_organs = organs

    zip_identification = zip(identification_cage, 
                        identification_group,
                        identification_no_container,
                        identification_no_fish, 
                        identification_id, 
                        identification_weight,
                        identification_extra_features_detail, 
                        identification_is_optimal, 
                        identification_observations,
                        identification_organs)
    zip_identification1 = zip(identification_cage, 
                        identification_group,
                        identification_no_container,
                        identification_no_fish, 
                        identification_id, 
                        identification_weight,
                        identification_extra_features_detail, 
                        identification_is_optimal, 
                        identification_observations,
                        identification_organs)

    entryform_identification = entryform.identification_set.all()
    
    change = change or checkIdentification(entryform_identification, zip_identification1)
    if change:
        changeCaseVersion(False, entryform.id, request.user.id)
    if strtobool(var_post.get('select_if_divide_flow')):
        if var_post.get('flow_divide_option') == "1":
            i = 0
            for values in zip_identification:
                # First identification is first subflow and it had some data saved before.
                # Next iterations need to create an entire EntryForm based in the first one.
                if i == 0:
                    entryform_identification.delete()
                    identificacion = Identification.objects.create(
                        entryform_id=entryform.id,
                        cage=values[0],
                        group=values[1],
                        no_container=values[2],
                        no_fish=values[3],
                        temp_id=values[4],
                        weight=values[5],
                        extra_features_detail=values[6],
                        is_optimum = True if "si" in values[7] else False,
                        observation = values[8]
                    )
                    organs_type2_count = Organ.objects.filter(id__in=values[9], organ_type=2).count()
                    if organs_type2_count > 0:
                        for org in Organ.objects.all():
                            identificacion.organs.add(org)
                    else:
                        for org in values[9]:
                            identificacion.organs.add(org)
                    
                    for org in values[9]:
                        identificacion.organs_before_validations.add(org)

                    sample_index = 1
                    for i in range(int(values[3])):
                        sample = Sample.objects.create(
                            entryform_id=entryform.id,
                            index=sample_index,
                            identification=identificacion
                        )
                        sample_index += 1
                else:
                    flow_aux = Flow.objects.get(pk=1)
                    entryform_aux = EntryForm.objects.create(created_by=request.user)
                    form_aux = Form.objects.create(
                        content_object=entryform_aux, flow=flow_aux, state=flow_aux.step_set.all()[1:2].first().state, parent_id=entryform.forms.first().id)
                    entryform_aux.specie_id = var_post.get('specie')
                    entryform_aux.watersource_id = var_post.get('watersource')
                    entryform_aux.fixative_id = var_post.get('fixative')
                    entryform_aux.larvalstage_id = var_post.get('larvalstage')
                    entryform_aux.observation = var_post.get('observation')
                    entryform_aux.customer_id = var_post.get('customer')
                    entryform_aux.no_order = var_post.get('no_order')
                    entryform_aux.created_at = datetime.strptime(var_post.get('created_at'), '%d/%m/%Y %H:%M')
                    entryform_aux.sampled_at = datetime.strptime(var_post.get('sampled_at'), '%d/%m/%Y %H:%M')
                    entryform_aux.center = var_post.get('center')
                    entryform_aux.no_caso = entryform.no_caso
                   
                    entryform_aux.save()

                    entryform_aux.identification_set.all().delete()
                    identificacion = Identification.objects.create(
                        entryform_id=entryform_aux.id,
                        cage=values[0],
                        group=values[1],
                        no_container=values[2],
                        no_fish=values[3],
                        temp_id=values[4],
                        weight=values[5],
                        extra_features_detail=values[6],
                        is_optimum = True if "si" in values[7] else False,
                        observation = values[8]
                    )

                    organs_type2_count = Organ.objects.filter(id__in=values[9], organ_type=2).count()
                    if organs_type2_count > 0:
                        for org in Organ.objects.all():
                            identificacion.organs.add(org)
                    else:
                        for org in values[9]:
                            identificacion.organs.add(org)
                    
                    for org in values[9]:
                        identificacion.organs_before_validations.add(org)

                    sample_index = 1
                    for i in range(int(values[3])):
                        sample = Sample.objects.create(
                            entryform_id=entryform_aux.id,
                            index=sample_index,
                            identification=identificacion
                        )
                        sample_index += 1
                i += 1 
        elif var_post.get('flow_divide_option') == "2":
            subflow_groups = [
                var_post.getlist(k) for k, v in var_post.items()
                if k.startswith("subflow_select[group]")
            ]
            zip_identification_list = list(zip_identification)
            for i in range(len(subflow_groups)):
                if i == 0:
                    total_no_fish = 0
                    entryform_identification.delete()
                    for values in zip_identification_list:
                        new_no_fish = 0
                        for item in subflow_groups[i]:
                            if item.split("_")[0] == values[4]:
                                new_no_fish += 1
                        if new_no_fish:
                            identificacion = Identification.objects.create(
                                entryform_id=entryform.id,
                                cage=values[0],
                                group=values[1],
                                no_container=values[2],
                                no_fish=new_no_fish,
                                temp_id=values[4],
                                weight=values[5],
                                extra_features_detail=values[6],
                                is_optimum = True if "si" in values[7] else False,
                                observation = values[8]
                            )
                            
                            organs_type2_count = Organ.objects.filter(id__in=values[9], organ_type=2).count()
                            if organs_type2_count > 0:
                                for org in Organ.objects.all():
                                    identificacion.organs.add(org)
                            else:
                                for org in values[9]:
                                    identificacion.organs.add(org)
                            
                            for org in values[9]:
                                identificacion.organs_before_validations.add(org)

                            sample_index = 1
                            for k in range(int(new_no_fish)):
                                sample = Sample.objects.create(
                                    entryform_id=entryform.id,
                                    index=sample_index,
                                    identification=identificacion
                                )
                                sample_index += 1
                        
                else:
                    flow_aux = Flow.objects.get(pk=1)
                    entryform_aux = EntryForm.objects.create(created_by=request.user)
                    form_aux = Form.objects.create(
                        content_object=entryform_aux, flow=flow_aux, state=flow_aux.step_set.all()[1:2].first().state, parent_id=entryform.forms.first().id)
                    entryform_aux.specie_id = var_post.get('specie')
                    entryform_aux.watersource_id = var_post.get('watersource')
                    entryform_aux.fixative_id = var_post.get('fixative')
                    entryform_aux.larvalstage_id = var_post.get('larvalstage')
                    entryform_aux.observation = var_post.get('observation')
                    entryform_aux.customer_id = var_post.get('customer')
                    entryform_aux.no_order = var_post.get('no_order')
                    entryform_aux.created_at = datetime.strptime(var_post.get('created_at'), '%d/%m/%Y %H:%M')
                    entryform_aux.sampled_at = datetime.strptime(var_post.get('sampled_at'), '%d/%m/%Y %H:%M')
                    entryform_aux.center = var_post.get('center')
                    entryform_aux.no_caso = entryform.no_caso

                    entryform_aux.save()

                    for values in zip_identification_list:
                        new_no_fish = 0
                        for item in subflow_groups[i]:
                            if item.split("_")[0] == values[4]:
                                new_no_fish += 1
                        if new_no_fish:
                            identificacion = Identification.objects.create(
                                entryform_id=entryform_aux.id,
                                cage=values[0],
                                group=values[1],
                                no_container=values[2],
                                no_fish=new_no_fish,
                                temp_id=values[4],
                                weight=values[5],
                                extra_features_detail=values[6],
                                is_optimum = True if "si" in values[7] else False,
                                observation = values[8]
                            )
                                    
                            for org in values[9]:
                                identificacion.organs.add(org)

                            sample_index = 1
                            for k in range(int(new_no_fish)):
                                sample = Sample.objects.create(
                                    entryform_id=entryform_aux.id,
                                    index=sample_index,
                                    identification=identificacion
                                )
                                sample_index += 1

    else:
        entryform_identification.delete()
        entryform.sample_set.all().delete()
        sample_index = 1

        for values in zip_identification:
            # print (values)
            identificacion = Identification.objects.create(
                entryform_id=entryform.id,
                cage=values[0],
                group=values[1],
                no_container=values[2],
                no_fish=values[3],
                temp_id=values[4],
                weight=values[5],
                extra_features_detail=values[6],
                is_optimum = True if "si" in values[7] else False,
                observation = values[8]
            )

            organs_type2_count = Organ.objects.filter(id__in=values[9], organ_type=2).count()
            if organs_type2_count > 0:
                for org in Organ.objects.all():
                    identificacion.organs.add(org)
            else:
                for org in values[9]:
                    identificacion.organs.add(org)
            
            for org in values[9]:
                identificacion.organs_before_validations.add(org)

            for i in range(int(values[3])):
                sample = Sample.objects.create(
                    entryform_id=entryform.id,
                    index=sample_index,
                    identification=identificacion
                )
                sample_index += 1
       
    return True

def checkIdentification(olds, news):
    for v in news:
        ident = olds.filter(temp_id=v[4]).first()
        if not ident:
            return True
        if ident.cage != v[0] or \
            ident.group != v[1] or \
            str(ident.no_container) != v[2] or \
            str(ident.no_fish)!= v[3] or \
            ident.temp_id != v[4] or \
            (ident.weight != v[5] and (v[5] != '0' and ident.weight == 0.0)) or \
            ident.extra_features_detail != v[6] or \
            ident.is_optimum != True if "si" in v[7] else False or \
            ident.observation != v[8]:
            return True
        orgs = []
        for org in ident.organs.all():
            orgs.append(str(org.id))
        if len(orgs) != len(v[9]):
            return True
        for o in v[9]:
            if not o in orgs:
                return True
    return False

def step_2_entryform(request):
    var_post = request.POST.copy()

    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))
    Cassette.objects.filter(entryform=entryform).delete()
    exams_to_do = var_post.getlist("analysis")
    analyses_qs = entryform.analysisform_set.all()
    change = False
    # for analysis in analyses_qs:
    #     analysis.forms.get().delete()

    # analyses_qs.delete()


    for exam in exams_to_do:
        ex = Exam.objects.get(pk=exam)

        if ex.service_id in [1,3,4]:
            flow = Flow.objects.get(pk=2)
        elif ex.service_id == 5:
            continue;
        else:
            flow = Flow.objects.get(pk=3)

        
        if AnalysisForm.objects.filter(entryform_id=entryform.id, exam=ex).count() == 0:
            analysis_form = AnalysisForm.objects.create(
                entryform_id=entryform.id,
                exam=ex,
            )

            Form.objects.create(
                content_object=analysis_form,
                flow=flow,
                state=flow.step_set.all()[0].state,
                parent_id=entryform.forms.first().id)

    sample_id = [
        v for k, v in var_post.items() if k.startswith("sample[id]")
    ]

    for values in sample_id:
        sample = Sample.objects.get(pk=int(values))
        # sample.cassette_set.all().delete()
        
        sample_exams = [
            v[0] for k, v in dict(var_post).items() if k.startswith("sample[exams]["+values)
        ]
        sample_organs = []
        bulk_data = []
        
        for se in SampleExams.objects.filter(sample=sample):
            if se.exam_id not in sample_exams:
                se.delete()

        for exam in sample_exams:
            sample_organs = [
                v for k, v in dict(var_post).items() if k.startswith("sample[organs]["+values+"]["+exam)
            ]
            
            for se in SampleExams.objects.filter(sample=sample, exam_id=exam):
                if se.organ_id not in sample_organs[0]:
                    se.delete()      

            for organ in sample_organs[0]:
                if SampleExams.objects.filter(sample=sample, exam_id=exam, organ_id=organ).count() == 0:
                    bulk_data.append(SampleExams(
                        sample_id = sample.pk,
                        exam_id = exam,
                        organ_id= organ
                    ))
        change = change or checkSampleExams(sample.sampleexams_set.all(), bulk_data)
        SampleExams.objects.bulk_create(bulk_data)
        sample.save()
    if change:
        changeCaseVersion(True,entryform.id, request.user.id)
    return True

def checkSampleExams(olds, news):
    if len(olds) != len(news):
        return True
    for s in news:
        if not olds.filter(sample_id=s.sample_id, exam_id=s.exam_id, organ_id=s.organ_id).first():
            return True
    return False

def step_3_entryform(request):
    var_post = request.POST.copy()

    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))

    processor_loaded_at = None
    try:
        processor_loaded_at = datetime.strptime(var_post.get('processor_loaded_at'), '%d/%m/%Y %H:%M')
    except: 
        pass

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

    zip_cassettes = zip(cassette_sample_id, cassette_name, cassette_organs)

    entryform.cassette_set.all().delete()
    entryform.slice_set.all().delete()
    count = 1
    for values in zip_cassettes:
        sample = Sample.objects.get(pk=values[0])
        prev_cassettes = Cassette.objects.filter(entryform_id=entryform.id, cassette_name=values[1].strip())

        if prev_cassettes.count() > 0:
            cassette = prev_cassettes.first()
            cassette.samples.add(sample)
            for org in values[2]:
                if not cassette.organs.filter(pk=org).exists():
                    cassette.organs.add(org)
        else:
            cassette = Cassette.objects.create(
                entryform_id=entryform.id,
                processor_loaded_at=processor_loaded_at,
                cassette_name=values[1],
                index=count,
                # sample=sample
            )
            cassette.samples.add(sample)
            cassette.organs.set(values[2])
            count += 1
        cassette.save()


    for cassette in Cassette.objects.filter(entryform_id=entryform.id):
        exams_final = []
        for sample in cassette.samples.all():
            exams = [ sampleexam.exam for sampleexam in sample.sampleexams_set.all() if sampleexam.exam.service_id in [1,2,3]]
            exams_final = exams_final + exams
       
        exams_uniques = []
        _exams = []

        for item in exams_final:
            if item.pk not in exams_uniques:
                exams_uniques.append(item.pk)
                _exams.append(item)
        
        slice_index = 0
        
        for index, val in enumerate(_exams):
            slice_index = index + 1
            slice_name = cassette.cassette_name + "-S" + str(slice_index)
            
            analysis_form = AnalysisForm.objects.filter(
                entryform_id=entryform.id,
                exam_id=val.id,
            ).first()

            slice_new = Slice.objects.create(
                entryform_id = entryform.id,
                slice_name = slice_name,
                index=slice_index,
                cassette=cassette,
                analysis=analysis_form
            )
            slice_new.save()
        
    return True

def step_4_entryform(request):
    var_post = request.POST.copy()

    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))

    block_cassette_pk = [
        v for k, v in var_post.items() if k.startswith("block_cassette_pk")
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

    zip_block = zip(block_cassette_pk, block_start_block, block_end_block, block_start_slice, block_end_slice)

    for values in zip_block:
        _slices = Slice.objects.filter(cassette=Cassette.objects.get(pk=values[0]))
        for _slice in _slices:
            _slice.start_block = datetime.strptime(values[1], '%d/%m/%Y %H:%M:%S') or None
            _slice.end_block = datetime.strptime(values[2], '%d/%m/%Y %H:%M:%S') or None
            _slice.start_slice = datetime.strptime(values[3], '%d/%m/%Y %H:%M:%S') or None
            _slice.end_slice = datetime.strptime(values[4], '%d/%m/%Y %H:%M:%S') or None
            _slice.save()

    return True

def step_5_entryform(request):
    print("step_4")
    return True

def changeCaseVersion(allow_new, form_id, user_id):
    versions = CaseVersion.objects.filter(entryform_id= form_id)
    if len(versions) or allow_new:
        CaseVersion.objects.create(
            entryform_id = form_id,
            version = len(versions) + 1,
            generated_by_id = user_id
        )
    

def step_new_analysis(request):
    var_post = request.POST.copy()
    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))
    
    exams_to_do = var_post.getlist("analysis")
    analyses_qs = entryform.analysisform_set.all()

    for analysis in analyses_qs:
        analysis.forms.get().delete()

    analyses_qs.delete()

    for exam in exams_to_do:
        ex = Exam.objects.get(pk=exam)
        if AnalysisForm.objects.filter(entryform_id=entryform.id, exam_id=exam).count() == 0:
            if ex.service_id in [1,3,4]:
                flow = Flow.objects.get(pk=2)
            elif ex.service_id == 5:
                continue;
            else:
                flow = Flow.objects.get(pk=3)

            analysis_form = AnalysisForm.objects.create(
                entryform_id=entryform.id,
                exam=ex,
            )

            Form.objects.create(
                content_object=analysis_form,
                flow=flow,
                state=flow.step_set.all()[0].state,
                parent_id=entryform.forms.first().id)

    sample_id = [
        v for k, v in var_post.items() if k.startswith("sample[id]")
    ]

    for values in sample_id:
        sample = Sample.objects.get(pk=int(values))
        sample_exams = [
            v[0] for k, v in dict(var_post).items() if k.startswith("sample[exams]["+values)
        ]
        sample_organs = []
        for exam in sample_exams:
            sample_organs = [
                v for k, v in dict(var_post).items() if k.startswith("sample[organs]["+values+"]["+exam)
            ]
            for organ in sample_organs[0]:
                if SampleExams.objects.filter(sample= sample, exam_id=exam, organ_id=organ).count() == 0:
                    SampleExams.objects.create(
                        sample= sample,
                        exam_id= exam,
                        organ_id= organ
                    )
                    for cassette in Cassette.objects.filter(sample=sample):
                        if not len(cassette.organs.filter(id=organ)):
                            cassette.organs.add(organ)
                            cassette.save()
                            
        for cassette in Cassette.objects.filter(sample=sample):
            cassette.slice_set.all().delete()
            exams = [ sampleexam.exam for sampleexam in sample.sampleexams_set.all() if sampleexam.exam.service_id in [1,2,3]]
            _exams = []
            exams_uniques = []

            for item in exams:
                if item.pk not in exams_uniques:
                    exams_uniques.append(item.pk)
                    _exams.append(item)
            
            slice_index = 0
            
            for index, val in enumerate(_exams):
                slice_index = index + 1
                slice_name = cassette.cassette_name + "-S" + str(slice_index)
                
                analysis_form = AnalysisForm.objects.filter(
                    entryform_id=entryform.id,
                    exam_id=val.id,
                ).first()

                slice_new = Slice.objects.create(
                    entryform_id = entryform.id,
                    slice_name = slice_name,
                    index=slice_index,
                    cassette=cassette,
                    analysis=analysis_form
                )
                slice_new.save()

    return False

def step_new_analysis2(request):
    var_post = request.POST.copy()
    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))
    
    exams_to_do = var_post.getlist("analysis")
    analyses_qs = entryform.analysisform_set.all()

    new_analysisform = {}
    for exam in exams_to_do:
        ex = Exam.objects.get(pk=exam)
        if AnalysisForm.objects.filter(entryform_id=entryform.id, exam_id=exam).count() == 0:
            if ex.service_id in [1,3,4]:
                flow = Flow.objects.get(pk=2)
            elif ex.service_id == 5:
                continue;
            else:
                flow = Flow.objects.get(pk=3)

            analysis_form = AnalysisForm.objects.create(
                entryform_id=entryform.id,
                exam=ex,
            )
            new_analysisform[exam] = analysis_form.pk

            Form.objects.create(
                content_object=analysis_form,
                flow=flow,
                state=flow.step_set.all()[0].state,
                parent_id=entryform.forms.first().id)

    sample_id = [
        v for k, v in var_post.items() if k.startswith("sample[id]")
    ]

    for values in sample_id:
        sample = Sample.objects.get(pk=int(values))
        sample_exams = [
            v[0] for k, v in dict(var_post).items() if k.startswith("sample[exams]["+values)
        ]
        sample_organs = []
        for exam in sample_exams:
            sample_organs = [
                v for k, v in dict(var_post).items() if k.startswith("sample[organs]["+values+"]["+exam)
            ]
            for organ in sample_organs[0]:
                if SampleExams.objects.filter(sample= sample, exam_id=exam, organ_id=organ).count() == 0:
                    SampleExams.objects.create(
                        sample= sample,
                        exam_id= exam,
                        organ_id= organ
                    )
                    for cassette in Cassette.objects.filter(samples__in=[sample]):
                        if not len(cassette.organs.filter(id=organ)):
                            cassette.organs.add(organ)
                            cassette.save()

            if new_analysisform.get(exam, None):
                for cassette in Cassette.objects.filter(sample=sample):
                    last_slice_from_cassette = Slice.objects.filter(cassette=cassette).last()
                    last_slice_from_cassette.pk = None
                    old_index = last_slice_from_cassette.index
                    new_index = old_index + 1
                    last_slice_from_cassette.index = new_index
                    last_slice_from_cassette.analysis_id = new_analysisform.get(exam, None)
                    last_slice_from_cassette.slice_name = last_slice_from_cassette.slice_name.replace("S"+str(old_index), "S"+str(new_index) )
                    last_slice_from_cassette.save()

    return False

def step_1_analysisform(request):
    var_post = request.POST.copy()

    stain_slice_id = [
        v for k, v in var_post.items() if k.startswith("stain_slice_id")
    ]
    stain_start_stain = [
        v for k, v in var_post.items() if k.startswith("stain_start_stain")
    ]
    stain_end_stain = [
        v for k, v in var_post.items() if k.startswith("stain_end_stain")
    ]

    zip_stain = zip(stain_slice_id, stain_start_stain, stain_end_stain)

    for values in zip_stain:
        slice_new = Slice.objects.get(pk=values[0])
        slice_new.start_stain = datetime.strptime(values[1], '%d/%m/%Y %H:%M:%S') or None
        slice_new.end_stain = datetime.strptime(values[2], '%d/%m/%Y %H:%M:%S') or None
        slice_new.start_scan = None
        slice_new.end_scan = None
        slice_new.slice_store = None

        slice_new.save()


def step_2_analysisform(request):
    var_post = request.POST.copy()

    scan_slice_id = [
        v for k, v in var_post.items() if k.startswith("scan_slice_id")
    ]
    scan_start_scan = [
        v for k, v in var_post.items() if k.startswith("scan_start_scan")
    ]
    scan_end_scan = [
        v for k, v in var_post.items() if k.startswith("scan_end_scan")
    ]
    scan_store = [
        v for k, v in var_post.items() if k.startswith("scan_store")
    ]

    zip_scan = zip(scan_slice_id, scan_start_scan, scan_end_scan, scan_store)

    for values in zip_scan:
        slice_new = Slice.objects.get(pk=values[0])
        slice_new.start_scan = datetime.strptime(values[1], '%d/%m/%Y %H:%M:%S') or None
        slice_new.end_scan = datetime.strptime(values[2], '%d/%m/%Y %H:%M:%S') or None
        slice_new.slice_store = values[3]
        slice_new.box_id = None
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
        slice_new.report_set.all().delete()
        slice_new.save()


def step_4_analysisform(request):
    print("Step 4 Analysis Form")

def step_5_analysisform(request):
    var_post = request.POST.copy()

    analysis_id = var_post.get('analysis_id')
    no_reporte = var_post.get('no_reporte')
    box_findings = var_post.get('box-findings').replace("\\r\\n", "")
    box_diagnostic = var_post.get('box-diagnostics').replace("\\r\\n", "")
    box_comments = var_post.get('box-comments').replace("\\r\\n", "")
    box_tables = var_post.get('box-tables').replace("\\r\\n", "")
    # print (var_post)
    ReportFinal.objects.filter(analysis_id=analysis_id).delete()
    ReportFinal.objects.create(
        analysis_id=analysis_id,
        no_reporte=no_reporte,
        box_findings=box_findings,
        box_diagnostics=box_diagnostic,
        box_comments=box_comments,
        box_tables=box_tables
    )

# Generic function for call any process method for any model_form
def call_process_method(model_name, request):
    method_name = "process_" + str(model_name)
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(method_name)
    if not method:
        raise NotImplementedError("Method %s not implemented" % method_name)
    return method(request)

def save_identification(request, id):
    var_post = request.POST.copy()
    change = False
    ident = Identification.objects.get(pk=id)
    if ident.cage != var_post['jaula']:
        change = True
    ident.cage = var_post['jaula']

    if ident.group != var_post['grupo']:
        change = True
    ident.group = var_post['grupo']

    if str(ident.no_container) != var_post['contenedores']:
        change = True
    ident.no_container = var_post['contenedores']

    if ident.weight != var_post['peso'] and (var_post['peso'] != '0' and ident.weight == 0.0) :
        change = True
    ident.weight = var_post['peso']

    if ident.extra_features_detail != var_post['extras']:
        change = True
    ident.extra_features_detail = var_post['extras']

    if ident.observation != var_post['observation']:
        change = True
    ident.observation = var_post['observation']

    if ident.is_optimum != True if '1' == var_post['optimo'] else False:
        change = True
    ident.is_optimum = var_post['optimo']

    if ident.no_fish != var_post['no_fish']:
        change = True
        identification_ids = Identification.objects.filter(entryform=ident.entryform).values_list('id', flat=True)
        current_total_samples = Sample.objects.filter(identification__in=identification_ids).order_by('-index')
        current_ident_samples = Sample.objects.filter(identification=ident).order_by('-index')
        new_samples = int(var_post['no_fish']) - current_ident_samples.count()
        max_index = current_total_samples.first().index if current_total_samples.count() > 0 else 0
        new_counter_index = 0
        for i in range(len(current_total_samples), len(current_total_samples) + new_samples):
            sample = Sample.objects.create(
                entryform=ident.entryform,
                index=max_index + new_counter_index + 1,
                identification=ident
            )
            new_counter_index += 1

    ident.no_fish = var_post['no_fish']

    organs = var_post.getlist('organs')
    orgs = []
    for org in ident.organs_before_validations.all():
        orgs.append(str(org.id))
    if len(orgs) != len(organs):
        change = True
    for o in organs:
        if not o in orgs:
            change = True

    ident.organs.set([])
    ident.organs_before_validations.set([])

    organs_type2_count = Organ.objects.filter(id__in=organs, organ_type=2).count()
    if organs_type2_count > 0:
        for org in Organ.objects.all():
            ident.organs.add(org)
    else:
        for org in organs:
            ident.organs.add(int(org))
    
    for org in organs:
        ident.organs_before_validations.add(int(org))
    
    ident.save()

    if change:
        changeCaseVersion(True, ident.entryform.id, request.user.id)
    return JsonResponse({})

def new_empty_identification(request, entryform_id):
    ident = Identification.objects.create(entryform_id=entryform_id, temp_id=''.join(random.choices(string.ascii_uppercase + string.digits, k=11)))
    return JsonResponse({'id': ident.id}) 

def save_generalData(request, id):
    var_post = request.POST.copy()
    entry = EntryForm.objects.get(pk=id)

    change = False
    if entry.specie_id != int(var_post['specie']):
        change = True
    entry.specie_id = int(var_post['specie'])
    if entry.watersource_id != int(var_post['watersource']):
        change = True
    entry.watersource_id = int(var_post['watersource'])
    if entry.larvalstage_id != int(var_post['larvalstage']):
        change = True
    entry.larvalstage_id = int(var_post['larvalstage'])
    if entry.fixative_id != int(var_post['fixative']):
        change = True
    entry.fixative_id = int(var_post['fixative'])
    if entry.customer_id != int(var_post['client']):
        change = True
    entry.customer_id = int(var_post['client'])

    if entry.entryform_type_id != int(var_post['entryform_type']):
        change = True
    entry.entryform_type_id = int(var_post['entryform_type'])

    if entry.company != var_post['company']:
        change = True
    entry.company = var_post['company']
    if entry.center != var_post['center']:
        change = True
    entry.center = var_post['center']
    if entry.responsible != var_post['responsable']:
        change = True
    entry.responsible = var_post['responsable']
    if entry.no_order != var_post['no_order']:
        change = True
    entry.no_order = var_post['no_order']
    if entry.no_request != var_post['no_solic']:
        change = True
    entry.no_request = var_post['no_solic']
    if entry.anamnesis != var_post['anamnesis']:
        change = True
    entry.anamnesis = var_post['anamnesis']
    try:
        entry.created_at = datetime.strptime(var_post.get('recive'), '%d/%m/%Y %H:%M')
    except: 
        pass
    try:
        entry.sampled_at = datetime.strptime(var_post.get('muestreo'), '%d/%m/%Y %H:%M')
    except:
        pass
    if change:
        changeCaseVersion(True, id, request.user.id)
    entry.save()
    return JsonResponse({})

def sendEmailNotification(request):
# form, current_state, next_state):
    var_post = request.GET.copy()

    form = Form.objects.get(pk=var_post.get('form_id'))
    next_state = form.state
    previous_step = strtobool(var_post.get('previous_step'))
    if not previous_step:
        current_state = Permission.objects.get(to_state=form.state, type_permission='w').from_state
    else:
        current_state = Permission.objects.get(from_state=form.state, type_permission='w').to_state

    content_type = form.content_type.model
    caso = ''
    exam = ''
    template = 'app/notification.html'
    if content_type == 'analysisform':
        caso = form.parent.content_object.no_caso
        exam = form.content_object.exam.name
        template = 'app/notification1.html'
    else:
        caso = form.content_object.no_caso
        
    users=[]
    if next_state.id < 10:
        users = User.objects.filter(userprofile__profile_id__in=[1,3]).values_list('first_name', 'last_name', 'email')
    else:
        users=list(User.objects.filter(userprofile__profile_id__in=[1]).values_list('first_name', 'last_name', 'email'))
        if form.content_object.patologo:
            users.append((form.content_object.patologo.first_name, form.content_object.patologo.last_name, form.content_object.patologo.email))
    print(users)
    for f, l, e in users:
        subject = "Notificación: Acción Requerida Caso " + caso
        to = [e]
        # to = ['wcartaya@dataqu.cl']
        from_email = settings.EMAIL_HOST_USER

        ctx = {
            'name': f+' '+l,
            'nro_caso': caso,
            'etapa_last': current_state.name,
            'etapa_current': next_state.name,
            'url': settings.SITE_URL+'/workflow/'+str(form.id)+'/'+next_state.step.tag,
            'exam':exam
        }
        message = get_template(template).render(context=ctx)
        msg = EmailMultiAlternatives(subject,message,from_email,to)
        msg.content_subtype="html"
        # msg.send()
    return JsonResponse({})

def completeForm(request, form_id):
    form = Form.objects.get(pk=form_id)
    form.form_closed = True
    form.save()
    return JsonResponse({'ok':True})

def save_step1(request, form_id):
    valid = step_1_entryform(request)
    return JsonResponse({'ok': valid})

def save_patologo(request, analysis_id, patologo_id= None):
    analysis = AnalysisForm.objects.get(pk=analysis_id)
    analysis.patologo_id = patologo_id
    analysis.save()
    return JsonResponse({})

def dashboard_analysis(request):
    exam = request.GET.get('exam')
    year = request.GET.get('year')
    mes = request.GET.getlist('mes')
    query = """
                SELECT YEAR(a.created_at) AS `year`, MONTH(a.created_at) AS `month`, COUNT(a.id) AS count
                FROM backend_sample s
                INNER JOIN backend_analysisform a ON s.entryform_id = a.entryform_id
                INNER JOIN backend_entryform e ON a.entryform_id = e.id
                INNER JOIN workflows_form f ON a.entryform_id = f.object_id
                WHERE f.flow_id in (2,3) AND f.cancelled = 0
                AND YEAR(a.created_at) = {0}
                AND MONTH(a.created_at) IN {1}
            """.format(year, tuple(mes))
    if exam != '0':
       query += """
                    AND a.exam_id = %s
                """.format(exam)
    query +="""
                GROUP BY `year`, `month`
                ORDER BY `month`
            """
    cursor1=connection.cursor()
    data1 = cursor1.execute(query)
    data = cursor1.fetchall()

    return JsonResponse({'data': data})
       
def dashboard_lefts(request):
    exam = request.GET.get('exam')
    year = request.GET.get('year')
    mes = request.GET.getlist('mes')
    query = """
                SELECT YEAR(e.created_at) AS `year`, MONTH(e.created_at) AS `month`, CONCAT(u.first_name,' ',u.last_name) AS fullName, COUNT(e.id) AS count
                FROM backend_analysisform e 
                LEFT JOIN auth_user u ON e.patologo_id = u.id
                INNER JOIN workflows_form f ON f.object_id = e.id
                WHERE f.form_closed = 0 AND f.flow_id in (2,3) AND f.cancelled = 0
                AND YEAR(e.created_at) = {0}
                AND MONTH(e.created_at) IN {1}
            """.format(year, tuple(mes))
    if exam != '0':
       query += """
                    AND e.exam_id = {0}
                """.format(exam)
    query +="""
                GROUP BY `year`, `month`, fullName
                ORDER BY `month`
            """
    cursor1=connection.cursor()
    data1 = cursor1.execute(query)
    data = cursor1.fetchall()

    return JsonResponse({'data': data})   

def dashboard_reports(request):
    exam = request.GET.get('exam')
    year = request.GET.get('year')
    mes = request.GET.getlist('mes')
    
    query = """
                SELECT YEAR(f.closed_at) AS `year`, MONTH(f.closed_at) AS `month`, COUNT(e.id) AS count
                FROM backend_analysisform e
                INNER JOIN workflows_form f ON f.object_id = e.id
                WHERE f.form_closed = 1 AND f.flow_id in (2,3) AND f.cancelled = 0
                AND YEAR(f.closed_at) = {0}
                AND MONTH(f.closed_at) IN {1}
            """.format(year, tuple(mes))
    if exam != '0':
       query += """
                    AND e.exam_id = {0}
                """.format(exam)
    query +="""
                GROUP BY `year`, `month`
                ORDER BY `month`
            """
    cursor1=connection.cursor()
    data1 = cursor1.execute(query)
    data = cursor1.fetchall()

    return JsonResponse({'data': data})

def close_service(request, form_id):
    form = Form.objects.get(pk=form_id)
    form.form_closed = True
    form.closed_at = datetime.now()
    form.save()
    return JsonResponse({'ok':True})

def cancel_service(request, form_id):
    form = Form.objects.get(pk=form_id)
    form.cancelled = True
    form.cancelled_at = datetime.now()
    form.save()
    return JsonResponse({'ok':True})

def reopen_form(request, form_id):
    form = Form.objects.get(pk=form_id)
    form.cancelled = False
    form.cancelled_at = None
    form.form_reopened = True
    form.form_closed = False
    form.closed_at = None
    form.save()
    return JsonResponse({'ok':True})

def delete_sample(request, id):
    sample = Sample.objects.get(pk=id)
    ident = sample.identification
    ident.no_fish = ident.no_fish - 1
    ident.save()
    sample.delete()
    changeCaseVersion(True, ident.entryform.id, request.user.id)

    return JsonResponse({'ok':True})
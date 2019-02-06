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
from django.forms.models import model_to_dict

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
                    entryform=entryform['id']).order_by('index')
            
            samples_as_dict = []
            for s in samples:
                s_dict = model_to_dict(s, exclude=['organs', 'sampleexams', 'exams', 'identification'])
                organs = []
                sampleexams = s.sampleexams_set.all()
                sampleExa = {}
                for sE in sampleexams:
                    try:
                        sampleExa[sE.exam_id]['organ_id'].append(sE.organ_id)
                    except:
                        sampleExa[sE.exam_id]={
                            'exam_id': sE.exam_id,
                            'exam_name': sE.exam.name,
                            'sample_id': sE.sample_id,
                            'organ_id': [sE.organ_id]
                        }
                    organs.append(model_to_dict(sE.organ))
                cassettes = Cassette.objects.filter(sample=s).values()
                s_dict['organs_set'] = organs
                # s_dict['exams_set'] = list(exams)
                s_dict['sample_exams_set'] = sampleExa
                s_dict['cassettes_set'] = list(cassettes)
                s_dict['identification'] = model_to_dict(s.identification, exclude=["organs",])
                samples_as_dict.append(s_dict)

            # entryform["identifications"] = list(
            #     entryform_object.identification_set.all().values())
            entryform["identifications"] = []
            for ident in entryform_object.identification_set.all():
                ident_json = model_to_dict(ident, exclude=["organs"])
                ident_json['organs_set'] = list(ident.organs.all().values())
                entryform["identifications"].append(ident_json)              

            entryform["analyses"] = list(
                entryform_object.analysisform_set.all().values())
            entryform["cassettes"] = list(
                entryform_object.cassette_set.all().values())
            entryform["customer"] = model_to_dict(entryform_object.customer) if entryform_object.customer else None
            entryform["larvalstage"] = model_to_dict(entryform_object.larvalstage) if entryform_object.larvalstage else None
            entryform["fixative"] = model_to_dict(entryform_object.fixative) if entryform_object.fixative else None
            entryform["watersource"] = model_to_dict(entryform_object.watersource) if entryform_object.watersource else None
            entryform["specie"] = model_to_dict(entryform_object.specie) if entryform_object.specie else None

            exams_set = list(Exam.objects.all().values())
            organs_set = list(Organ.objects.all().values())

            data = {
                'entryform': entryform,
                'identifications': identifications,
                'samples': samples_as_dict,
                'exams': exams_set,
                'organs': organs_set
            }
        else:
            species = list(Specie.objects.all().values())
            larvalStages = list(LarvalStage.objects.all().values())
            fixtatives = list(Fixative.objects.all().values())
            waterSources = list(WaterSource.objects.all().values())
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

        # no_slice = len(analyses)

        cassettes_qs = Cassette.objects.filter(
            entryform=entry_form).prefetch_related(Prefetch('organs'))
        cassettes = []

        for cassette in cassettes_qs:
            organs = [organ.name for organ in cassette.organs.all()]
            slices = []

            for slice in Slice.objects.filter(cassette=cassette):
                slices.append(model_to_dict(slice))

            sample = model_to_dict(cassette.sample, exclude=["exams", "organs"])
            # print(sample)
            # s_dict['identification'] = model_to_dict(s.identification, exclude=["organs",])
            sample['identification'] = model_to_dict(Identification.objects.get(pk=sample['identification']), exclude=["organs"])
            # sample_exams = [model_to_dict(exam) for exam in Sample.objects.get(pk=sample['id']).exams.all() ]
            sample_exams = [ model_to_dict(sampleexam.exam) for sampleexam in Sample.objects.get(pk=sample['id']).sampleexams_set.all() ]
            sample['exams_set'] = sample_exams

            # sample['exams_set'] = list(sample.exams.all().values())
            
            # print (sample)

            cassette_as_dict = model_to_dict(cassette, exclude=['organs'])
            cassette_as_dict['slices_set'] = slices
            cassette_as_dict['organs_set'] = organs
            cassette_as_dict['sample'] = sample

            cassettes.append(cassette_as_dict)
            # cassette_as_dict['sample'] = 
        # print(cassettes)
        
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
            s_dict = model_to_dict(s, exclude=['organs', 'exams', 'identification'])
            organs_set = s.organs.all().values()
            exams_set = s.exams.all().values()
            cassettes_set = Cassette.objects.filter(sample=s).values()
            s_dict['organs_set'] = list(organs_set)
            s_dict['exams_set'] = list(exams_set)
            s_dict['cassettes_set'] = list(cassettes_set)
            s_dict['identification'] = model_to_dict(s.identification, exclude=["organs"])
            samples_as_dict.append(s_dict)

        entryform["identifications"] = []
        for ident in entryform_object.identification_set.all():
            ident_json = model_to_dict(ident, exclude=["organs"])
            ident_json['organs_set'] = list(ident.organs.all().values())
            entryform["identifications"].append(ident_json)           
        # entryform["answer_questions"] = list(
        #     entryform_object.answerreceptioncondition_set.all().values())
        entryform["analyses"] = list(
            entryform_object.analysisform_set.all().values())
        entryform["cassettes"] = list(
            entryform_object.cassette_set.all().values())
        entryform["customer"] = model_to_dict(entryform_object.customer) if entryform_object.customer else None
        entryform["larvalstage"] = model_to_dict(entryform_object.larvalstage) if entryform_object.larvalstage else None
        entryform["fixative"] = model_to_dict(entryform_object.fixative) if entryform_object.fixative else None
        entryform["watersource"] = model_to_dict(entryform_object.watersource) if entryform_object.watersource else None
        entryform["specie"] = model_to_dict(entryform_object.specie) if entryform_object.specie else None
        
        data = {'cassettes': cassettes, 'exams': exams, 'analyses': analyses, 'entryform':entryform, 'samples': samples_as_dict}

        return JsonResponse(data)


class ANALYSIS(View):
    def get(self, request, entry_form=None):
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
            s_dict = model_to_dict(s, exclude=['organs', 'exams', 'identification'])
            organs_set = s.organs.all().values()
            exams_set = s.exams.all().values()
            cassettes_set = Cassette.objects.filter(sample=s).values()
            s_dict['organs_set'] = list(organs_set)
            s_dict['exams_set'] = list(exams_set)
            s_dict['cassettes_set'] = list(cassettes_set)
            s_dict['identification'] = model_to_dict(s.identification, exclude=["organs"])
            samples_as_dict.append(s_dict)

        entryform["identifications"] = []
        for ident in entryform_object.identification_set.all():
            ident_json = model_to_dict(ident, exclude=["organs"])
            ident_json['organs_set'] = list(ident.organs.all().values())
            entryform["identifications"].append(ident_json)           

        entryform["analyses"] = list(
            entryform_object.analysisform_set.all().values())
        entryform["cassettes"] = list(
            entryform_object.cassette_set.all().values())
        entryform["customer"] = model_to_dict(entryform_object.customer) if entryform_object.customer else None
        entryform["larvalstage"] = model_to_dict(entryform_object.larvalstage) if entryform_object.larvalstage else None
        entryform["fixative"] = model_to_dict(entryform_object.fixative) if entryform_object.fixative else None
        entryform["watersource"] = model_to_dict(entryform_object.watersource) if entryform_object.watersource else None
        entryform["specie"] = model_to_dict(entryform_object.specie) if entryform_object.specie else None

        data = {'analyses': analyses, 'entryform':entryform, 'samples': samples_as_dict}
        
        return JsonResponse(data)


class SLICE(View):
    def get(self, request, analysis_form=None):
        slices_qs = Slice.objects.filter(analysis=analysis_form)
        slices = []

        for slice_new in slices_qs:
            slice_as_dict = model_to_dict(slice_new, exclude=['cassette'])
            slice_as_dict['cassette'] = model_to_dict(slice_new.cassette, exclude=['organs'])
            slice_as_dict['organs'] = list(slice_new.cassette.organs.all().values())
            sample = slice_new.cassette.sample
            slice_as_dict['sample'] = model_to_dict(sample, exclude=['exams', 'organs', 'cassettes'])
            slice_as_dict['sample']['identification'] = model_to_dict(sample.identification, exclude=["organs"])
            slice_as_dict['paths_count'] = Report.objects.filter(slice_id=slice_new.pk).count()
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
            s_dict = model_to_dict(s, exclude=['organs', 'exams', 'cassettes', 'identification'])
            organs_set = s.organs.all().values()
            exams_set = s.exams.all().values()
            cassettes_set = Cassette.objects.filter(sample=s).values()
            s_dict['organs_set'] = list(organs_set)
            s_dict['exams_set'] = list(exams_set)
            s_dict['cassettes_set'] = list(cassettes_set)
            s_dict['identification'] = model_to_dict(s.identification, exclude=["organs"])
            samples_as_dict.append(s_dict)

        entryform["identifications"] = []
        for ident in entryform_object.identification_set.all():
            ident_json = model_to_dict(ident, exclude=["organs"])
            ident_json['organs_set'] = list(ident.organs.all().values())
            entryform["identifications"].append(ident_json)   

        entryform["analyses"] = list(
            entryform_object.analysisform_set.all().values())
        entryform["cassettes"] = list(
            entryform_object.cassette_set.all().values())
        entryform["customer"] = entryform_object.customer.name
        entryform["larvalstage"] = entryform_object.larvalstage.name
        entryform["fixative"] = entryform_object.fixative.name
        entryform["watersource"] = entryform_object.watersource.name
        entryform["specie"] = entryform_object.specie.name

        data = {'slices': slices, 'entryform': entryform, 'samples': samples_as_dict}
        # print (data)

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
            reports = Report.objects.filter(analysis_id=int(object_form_id))
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

            data = {
                'form': form,
                'form_id': form_id,
                'analysis_id': object_form_id,
                'set_step_tag': step_tag,
                'exam_name': form.content_object.exam.name,
                'form_parent_id': form.parent.id,
                'report': reports,
                'reports2': data
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
            process_answer = call_process_method(form.content_type.model,
                                                     request)
            form.form_closed = True
            form.save()

            return JsonResponse({'redirect_flow': True})

    def delete(self, request, form_id):
        Form.objects.get(pk=form_id).delete()
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
                    "identification": model_to_dict(report.identification),
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
                organs_set = s.organs.all().values()
                exams_set = s.exams.all().values()
                cassettes_set = Cassette.objects.filter(sample=s).values()
                s_dict['organs_set'] = list(organs_set)
                s_dict['exams_set'] = list(exams_set)
                s_dict['cassettes_set'] = list(cassettes_set)
                s_dict['identification'] = model_to_dict(s.identification)
                samples_as_dict.append(s_dict)

            entryform["identifications"] = list(
                entryform_object.identification_set.all().values())
            entryform["answer_questions"] = list(
                entryform_object.answerreceptioncondition_set.all().values())
            entryform["analyses"] = list(
                entryform_object.analysisform_set.all().values())
            entryform["cassettes"] = list(
                entryform_object.cassette_set.all().values())
            entryform["customer"] = entryform_object.customer.name
            entryform["larvalstage"] = entryform_object.larvalstage.name
            entryform["fixative"] = entryform_object.fixative.name
            entryform["watersource"] = entryform_object.watersource.name
            entryform["specie"] = entryform_object.specie.name
            # print(reports)

            data = {'reports': reports, "entryform": entryform}
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

        slice = Slice.objects.get(pk=slice_id)
        report = Report.objects.create(
            analysis_id=analysis_id,
            slice_id=slice_id,
            organ_id=organ_id,
            organ_location_id=organ_location_id,
            pathology_id=pathology_id,
            diagnostic_id=diagnostic_id,
            diagnostic_distribution_id=diagnostic_distribution_id,
            diagnostic_intensity_id=diagnostic_intensity_id,
            identification=slice.cassette.sample.identification
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

def organs_by_slice(request, slice_id=None):
    if slice_id:
        organs_qs = Slice.objects.get(
            pk=slice_id).cassette.organs.all()

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
    # print (var_post)

    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))

    entryform.specie_id = var_post.get('specie')
    entryform.watersource_id = var_post.get('watersource')
    entryform.fixative_id = var_post.get('fixative')
    entryform.larvalstage_id = var_post.get('larvalstage')
    entryform.observation = var_post.get('observation')
    entryform.customer_id = var_post.get('customer')
    entryform.no_order = var_post.get('no_order')
    try:
        entryform.created_at = datetime.strptime(var_post.get('created_at'), '%d/%m/%Y %H:%M')
    except: 
        pass
    try:
        entryform.sampled_at = datetime.strptime(var_post.get('sampled_at'), '%d/%m/%Y %H:%M')
    except:
        pass
    entryform.center = var_post.get('center')
    entryform.responsible = var_post.get('responsible')
    entryform.company = var_post.get('company')
    entryform.no_request = var_post.get('no_request')
    entryform.save()

#    questions_id = [
#         v for k, v in var_post.items() if k.startswith("question['id']")
#     ]
#     answers = [
#         v for k, v in var_post.items() if k.startswith("question['answer']")
#     ] 
#     zip_question = zip(questions_id, answers)

#     entryform.answerreceptioncondition_set.all().delete()
#     for values in zip_question:
#         answerquestion = AnswerReceptionCondition.objects.create(
#             entryform_id=entryform.id,
#             question_id=values[0],
#             answer=values[1],
#         )

    # sample_index = [
    #     list(v) for k, v in dict(var_post).items() if k.startswith("sample[index]")
    # ]
    # sample_identification = [
    #     list(v) for k, v in dict(var_post).items() if k.startswith("sample[identification]")
    # ]
    # sample_analysis = [
    #     list(v) for k, v in dict(var_post).items() if k.startswith("sample[analysis]")
    # ]

    # sample_organs = [
    #     list(v) for k, v in dict(var_post).items() if k.startswith("sample[organs]")
    # ]

    # # print (sample_organs)

    # zip_samples = zip(sample_index, sample_identification, sample_analysis, sample_organs)

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

                    # analysis_id = [
                    #     v for k, v in var_post.items() if k.startswith("analysis[id]")
                    # ]
                    # analysis_no_fish = [
                    #     v for k, v in var_post.items() if k.startswith("analysis[no_fish]")
                    # ]
                    # analysis_organ = [
                    #     var_post.getlist(k) for k, v in var_post.items()
                    #     if k.startswith("analysis[organ]")
                    # ]

                    # zip_analysis = zip(analysis_id, analysis_no_fish, analysis_organ)
                    
                    # analyses_qs = entryform.analysisform_set.all()

                    # for analysis in analyses_qs:
                    #     analysis.forms.get().delete()

                    # analyses_qs.delete()

                    # flow = Flow.objects.get(pk=2)

                    # for values in zip_analysis:
                    #     analysis = AnalysisForm.objects.create(
                    #         entryform_id=entryform.id,
                    #         exam_id=values[0],
                    #         no_fish=zip_identification[i][3],
                    #     )

                    #     analysis.organs.set(values[2])

                    #     Form.objects.create(
                    #         content_object=analysis,
                    #         flow=flow,
                    #         state=flow.step_set.all()[0].state,
                    #         parent_id=entryform.forms.first().id)

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
                    
                    # print (zip_analysis)

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
        # print ( var_post.getlist("identification[cage]"))
        # print (var_post.getlist("identification[is_optimal]"))
        optimals = [
            v for k, v in dict(var_post).items() if k.startswith("identification[is_optimal]")
        ]

        organs = [
            list(v) for k, v in dict(var_post).items() if k.startswith("identification[organs]")
        ]
        # print (organs)

        identification_cage = var_post.getlist("identification[cage]")
        identification_group = var_post.getlist("identification[group]")
        identification_no_container = var_post.getlist(
            "identification[no_container]")
        identification_no_fish = var_post.getlist("identification[no_fish]")
        identification_id = var_post.getlist("identification[id]")
        identification_weight = var_post.getlist("identification[weight]")
        identification_extra_features_detail = var_post.getlist("identification[extra_features_detail]")
        identification_is_optimal = optimals
        identification_observations = var_post.getlist("identification[observations]")
        identification_organs = organs

        zip_identification = zip(identification_cage, identification_group,
                                identification_no_container,
                                identification_no_fish, 
                                identification_id, 
                                identification_weight,
                                identification_extra_features_detail, 
                                identification_is_optimal, 
                                identification_observations,
                                identification_organs)

        entryform.identification_set.all().delete()
        entryform.sample_set.all().delete()
        sample_index = 1
        # print (zip_identification)
        for values in zip_identification:
            print (values)
            identificacion = Identification.objects.create(
                entryform_id=entryform.id,
                cage=values[0],
                group=values[1],
                no_container=values[2],
                no_fish=values[3],
                temp_id=values[4],
                weight=values[5],
                extra_features_detail=values[6],
                is_optimum = True if values[7] == "si" else False,
                observation = values[8]
            )
            
            for org in values[9]:
                identificacion.organs.add(org)

            for i in range(int(values[3])):
                sample = Sample.objects.create(
                    entryform_id=entryform.id,
                    index=sample_index,
                    identification=identificacion
                )
                sample_index += 1
        # print (caaca)
        # entryform.sample_set.all().delete()
        # for values in zip_samples:
        #     # print (values)
        #     sample = Sample.objects.create(
        #         entryform_id=entryform.id,
        #         index=int(values[0][0]),
        #         identification=Identification.objects.filter(entryform__id=entryform.id, temp_id=values[1][0]).first(),
        #     )
        #     for organ in values[3]:
        #         sample.organs.add(organ)

        #     for exam in values[2]:
        #         sample.exams.add(exam)
            
        #     sample.save()

        # exams_to_do = var_post.getlist("analysis")

        # analyses_qs = entryform.analysisform_set.all()

        # for analysis in analyses_qs:
        #     analysis.forms.get().delete()

        # analyses_qs.delete()

        # flow = Flow.objects.get(pk=2)

        # # print(exams_to_do)
        # for exam in exams_to_do:
        #     analysis_form = AnalysisForm.objects.create(
        #         entryform_id=entryform.id,
        #         exam_id=exam,
        #     )

        #     Form.objects.create(
        #         content_object=analysis_form,
        #         flow=flow,
        #         state=flow.step_set.all()[0].state,
        #         parent_id=entryform.forms.first().id)

def step_2_entryform(request):
    var_post = request.POST.copy()

    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))
    
    exams_to_do = var_post.getlist("analysis")
    analyses_qs = entryform.analysisform_set.all()

    for analysis in analyses_qs:
        analysis.forms.get().delete()

    analyses_qs.delete()

    flow = Flow.objects.get(pk=2)

    # print(exams_to_do)
    for exam in exams_to_do:
        analysis_form = AnalysisForm.objects.create(
            entryform_id=entryform.id,
            exam_id=exam,
        )

        Form.objects.create(
            content_object=analysis_form,
            flow=flow,
            state=flow.step_set.all()[0].state,
            parent_id=entryform.forms.first().id)

    sample_id = [
        v for k, v in var_post.items() if k.startswith("sample[id]")
    ]
    # sample_exams = [
    #     list(v) for k, v in dict(var_post).items() if k.startswith("sample[exams]")
    # ]
    # sample_organs = [
    #     list(v) for k, v in dict(var_post).items() if k.startswith("sample[organs]")
    # ]

    # zip_samples = zip(sample_id, sample_exams, sample_organs)

    for values in sample_id:
        sample = Sample.objects.get(pk=int(values))
        sample.sampleexams_set.all().delete()
        sample.save()
        sample_exams = [
            v[0] for k, v in dict(var_post).items() if k.startswith("sample[exams]["+values)
        ]
        sample_organs = []
        for exam in sample_exams:
            sample_organs = [
                v for k, v in dict(var_post).items() if k.startswith("sample[organs]["+values+"]["+exam)
            ]
            for organ in sample_organs[0]:
                SampleExams.objects.create(
                    sample= sample,
                    exam_id= exam,
                    organ_id= organ
                )
    return
        # for exam in values[1]:
        #     sample.exams.add(exam)

        # sample.organs.clear()
        # for organ in values[2]:
        #     sample.organs.add(organ)
        

def step_3_entryform(request):
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

    cassette_organs = [
        var_post.getlist(k) for k, v in var_post.items()
        if k.startswith("cassette[organ]")
    ]

    zip_cassettes = zip(cassette_sample_id, cassette_name, cassette_organs)

    entryform.cassette_set.all().delete()
    count = 1
    for values in zip_cassettes:
        sample = Sample.objects.get(pk=values[0])
        cassette = Cassette.objects.create(
            entryform_id=entryform.id,
            processor_loaded_at=processor_loaded_at,
            cassette_name=values[1],
            index=count,
            sample=sample
        )
        cassette.organs.set(values[2])
        cassette.save()
        count += 1

def step_4_entryform(request):
    var_post = request.POST.copy()

    entryform = EntryForm.objects.get(pk=var_post.get('entryform_id'))

    block_sample_id = [
        v for k, v in var_post.items() if k.startswith("cassette_sample_id")
    ]

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

    zip_block = zip(block_sample_id, block_cassette_pk, block_start_block, block_end_block, block_start_slice, block_end_slice)

    entryform.slice_set.all().delete()

    for values in zip_block:
        
        exams = [ sampleexam.exam for sampleexam in Sample.objects.get(pk=values[0]).sampleexams_set.all() ]
        slice_index = 0
        cassette = Cassette.objects.get(pk=values[1])
        
        for index, val in enumerate(exams):
            slice_index = index + 1
            slice_name = cassette.cassette_name + "-S" + str(slice_index)
            
            analysis_form = AnalysisForm.objects.filter(
                entryform_id=entryform.id,
                exam_id=val.id,
            ).first()

            slice_new = Slice.objects.create(
                entryform_id=entryform.id,
                slice_name=slice_name,
                start_block=values[2],
                end_block=values[3],
                start_slice=values[4],
                end_slice=values[5],
                index=slice_index,
                cassette=cassette,
                analysis=analysis_form

            )
            slice_new.save()

def step_5_entryform(request):
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

def step_5_analysisform(request):
    var_post = request.POST.copy()

    analysis_id = var_post.get('analysis_id')
    box_findings = var_post.get('box-findings').replace("\\r\\n", "")
    box_diagnostic = var_post.get('box-diagnostics').replace("\\r\\n", "")
    box_comments = var_post.get('box-comments').replace("\\r\\n", "")
    box_tables = var_post.get('box-tables').replace("\\r\\n", "")
    # print (var_post)
    ReportFinal.objects.create(
        analysis_id=analysis_id,
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

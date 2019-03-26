from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from backend import views

urlpatterns = [
    path('customer', csrf_exempt(views.CUSTOMER.as_view()), name='customer'),
    path('exam', csrf_exempt(views.EXAM.as_view()), name='exam'),
    path(
        'entryform', csrf_exempt(views.ENTRYFORM.as_view()), name='entryform'),
    path(
        'entryform/<int:id>',
        csrf_exempt(views.ENTRYFORM.as_view()),
        name='entryform_id'),
    path(
        'cassettes-entry-form/<int:entry_form>',
        csrf_exempt(views.CASSETTE.as_view()),
        name='cassette_entryform_id'),
    path(
        'workflow/<int:form_id>/<slug:step_tag>',
        csrf_exempt(views.WORKFLOW.as_view()),
        name='workflow_open_step'),
    path('workflow', csrf_exempt(views.WORKFLOW.as_view()), name='workflow'),
    path('workflow/<int:form_id>', csrf_exempt(views.WORKFLOW.as_view()), name='workflow_w_id'),
    path(
        'analysis-entry-form/<int:entry_form>',
        csrf_exempt(views.ANALYSIS.as_view()),
        name='analysis_entryform_id'),
    path(
        'slice-analysis/<int:analysis_form>',
        csrf_exempt(views.SLICE.as_view()),
        name='slice_analysis_id'),
    path('customer', csrf_exempt(views.CUSTOMER.as_view()), name='customer'),
    path(
        'report-slice/<int:slice_id>',
        csrf_exempt(views.REPORT.as_view()),
        name='report_by_slice'),
    path(
        'report-analysis/<int:analysis_id>',
        csrf_exempt(views.REPORT.as_view()),
        name='report_by_analysis'),
    path(
        'report/<int:report_id>',
        csrf_exempt(views.REPORT.as_view()),
        name='report_by_id'),
    path('report', csrf_exempt(views.REPORT.as_view()), name='report'),
    path(
        'organs-slice/<int:slice_id>',
        csrf_exempt(views.organs_by_slice),
        name="organs_by_slice"),
    path(
        'analysis/<int:analysisform_id>',
        csrf_exempt(views.set_analysis_comments),
        name="set_analysis_comments"),
    path(
        'images/<int:report_id>',
        csrf_exempt(views.IMAGES.as_view()),
        name='images',
    ),
    path(
        'block-timing',
        csrf_exempt(views.save_block_timing),
        name="save_block_timing"
    ),
    path(
        'stain-timing',
        csrf_exempt(views.save_stain_timing),
        name="save_stain_timing"
    ),
    path(
        'scan-timing',
        csrf_exempt(views.save_scan_timing),
        name="save_scan_timing"
    ),
    # path(
    #     'images/<int:image_id>',
    #     csrf_exempt(views.IMAGES.as_view()),
    #     'images_w_id'
    # ),

]

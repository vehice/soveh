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
        'organs-slice/<int:slice_id>/<int:sample_id>',
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
    path(
        'identification/<int:id>',
        csrf_exempt(views.save_identification),
        name="identification"
    ),
    path(
        'generalData/<int:id>',
        csrf_exempt(views.save_generalData),
        name="generalData"
    ),
    path(
        'sendNotification',
        csrf_exempt(views.sendEmailNotification),
        name="sendNotification"
    ),
    path('workform/<int:form_id>/complete', csrf_exempt(views.completeForm), name='complete_form'),

    path('workform/<int:form_id>/save_step1', csrf_exempt(views.save_step1), name='save_step1'),
    path('service_assigment/', csrf_exempt(views.service_assignment), name='service_assignment'),
    path('dashboard_analysis', csrf_exempt(views.dashboard_analysis), name='dashboard_analysis'),
    path('dashboard_reports', csrf_exempt(views.dashboard_reports), name='dashboard_reports'),
    path('dashboard_lefts', csrf_exempt(views.dashboard_lefts), name='dashboard_lefts'),
    path('responsible', csrf_exempt(views.RESPONSIBLE.as_view()), name='responsible'),
    path('responsible/<int:id>', csrf_exempt(views.RESPONSIBLE.as_view()), name='responsible_detail'),
    path('emailTemplate', csrf_exempt(views.EMAILTEMPLATE.as_view()), name='emailTemplate'),
    path('emailTemplate/<int:id>', csrf_exempt(views.EMAILTEMPLATE.as_view()), name='emailTemplate_detail'),
    path(
        'service_reports/<int:analysis_id>',
        csrf_exempt(views.SERVICE_REPORTS.as_view()),
        name='service_reports',
    ),
    path(
        'service_reports/<int:analysis_id>/<int:id>',
        csrf_exempt(views.SERVICE_REPORTS.as_view()),
        name='service_reports_id',
    ),
    path(
        'service_comments/<int:analysis_id>',
        csrf_exempt(views.SERVICE_COMMENTS.as_view()),
        name='service_comments',
    ),
    path(
        'service_comments/<int:analysis_id>/<int:id>',
        csrf_exempt(views.SERVICE_COMMENTS.as_view()),
        name='service_comments_id',
    ),
    path(
        'case_files/<int:entryform_id>',
        csrf_exempt(views.CASE_FILES.as_view()),
        name='case_files',
    ),
    path(
        'case_files/<int:entryform_id>/<int:id>',
        csrf_exempt(views.CASE_FILES.as_view()),
        name='case_files_id',
    ),
    path('close_service/<int:form_id>', csrf_exempt(views.close_service), name='close_service'),
    path('cancel_service/<int:form_id>', csrf_exempt(views.cancel_service), name='cancel_service'),
    path('reopen_form/<int:form_id>', csrf_exempt(views.reopen_form), name='reopen_form'),
    path(
        'delete-sample/<int:id>',
        csrf_exempt(views.delete_sample),
        name="delete-sample"
    ),
    path(
        'new-identification/<int:entryform_id>',
        csrf_exempt(views.new_empty_identification),
        name="new_identification"
    ),
    path(
        'remove-identification/<int:id>',
        csrf_exempt(views.remove_identification),
        name="remove_identification"
    ),
]

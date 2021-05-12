from django.test import TestCase, Client

from review.models import Analysis
from django.urls import reverse
import json


class AnalysisTestCase(TestCase):
    def setUp(self):
        Analysis.objects.create(pre_report_started=True, exam_id=66)
        Analysis.objects.create(
            pre_report_started=True, pre_report_ended=True, exam_id=66
        )

    def test_manager_stage(self):
        waiting = Analysis.objects.stage(0)

        self.assertGreaterEqual(
            len(waiting), 1, "Response should contain as expected or more results."
        )

    def test_view_index(self):
        client = Client()
        response = client.get(reverse("review:index"))

        self.assertTemplateUsed(
            response, "index.html", "Response must use expected template."
        )

    def test_view_list(self):
        client = Client()
        response = client.get(reverse("review:stage", kwargs={"index": 0}))

        self.assertIn(
            "pk", json.loads(response.json())[0], "Response must contain expected data."
        )

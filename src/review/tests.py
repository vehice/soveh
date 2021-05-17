from django.test import TestCase, Client

from django.contrib.auth.models import User
from review.models import Analysis, File, Stage
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
        analysis = Analysis.objects.filter(stages__state=0)

        self.assertGreaterEqual(
            waiting.count(),
            analysis.count(),
            "Response should contain as expected or more results.",
        )

    def test_view_index(self):
        client = Client()
        client.login(username="jmonagas", password="vehice1234")
        response = client.get(reverse("review:index"))

        self.assertTemplateUsed(
            response, "index.html", "Response must use expected template."
        )

    def test_view_list_stage(self):
        client = Client()
        client.login(username="jmonagas", password="vehice1234")
        response = client.get(reverse("review:list", kwargs={"index": 0}))
        analysis = Analysis.objects.stage(0)

        self.assertGreaterEqual(
            len(json.dumps(response.json())),
            analysis.count(),
            "Response must contain expected data.",
        )

    def test_view_list_waiting(self):
        client = Client()
        client.login(username="jmonagas", password="vehice1234")
        response = client.get(reverse("review:list", kwargs={"index": 9}))
        analysis = Analysis.objects.waiting()

        self.assertGreaterEqual(
            len(json.dumps(response.json())),
            analysis.count(),
            "Response must contain expected data.",
        )

    def test_update_stage(self):
        client = Client()
        client.login(username="jmonagas", password="vehice1234")

        user = User.objects.get(pk=1)

        stage = Stage.objects.create(
            analysis=Analysis.objects.last(), state=0, created_by=user
        )
        response = client.post(
            reverse("review:stage", kwargs={"pk": stage.analysis.id}),
            json.dumps({"state": 1}),
            content_type="application/json",
        )

        stage = json.loads(response.json())[0]

        self.assertTrue(stage, "Response must contain create or updated Stage.")

        self.assertDictContainsSubset(
            {"model": "review.stage"},
            stage,
            "Response must contain created or updated Stage.",
        )

    def test_get_files(self):
        client = Client()
        client.login(username="jmonagas", password="vehice1234")

        analysis = Analysis.objects.all().last()
        files = analysis.external_reports.all()
        review_files = File.objects.filter(analysis=analysis)

        response = client.get(reverse("review:files", kwargs={"pk": analysis.pk}))

        prereports = json.loads(response.json()["prereports"])
        reviews = json.loads(response.json()["reviews"])

        self.assertGreaterEqual(
            len(prereports),
            files.count(),
            "Response must contain expected result.",
        )

        self.assertGreaterEqual(
            len(reviews),
            review_files.count(),
            "Response must contain expected result.",
        )

    def test_file_download(self):
        client = Client()
        client.login(username="jmonagas", password="vehice1234")

        review_file = File.objects.all().last()

        response = client.get(
            reverse("review:download_file", kwargs={"pk": review_file.id})
        )

        self.assertTrue(response.streaming_content)

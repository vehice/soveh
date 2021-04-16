import json
import datetime

from django.contrib import auth
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker

from lab.models import Case, Cassette
from backend.models import Organ


class CaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

    def test_detail_returns_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:case_detail", kwargs={"pk": 983}))

        self.assertTemplateUsed(
            response, "cases/detail.html", "Response must use expected template."
        )

    def test_detail_returns_case(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:case_detail", kwargs={"pk": 983}))

        self.assertTrue(
            response.context["case"].id == 983, "Response must return expected Case."
        )



class CassetteIndexTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

    def test_expected_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:cassette_index"))

        self.assertTemplateUsed(
            response, "cassettes/index.html", "Response must use expected template."
        )

        self.assertIn("cases", response.context, "Response context must contain Cases.")
    def test_expected_data(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:cassette_index"))
        cassette = Cassette.objects.all()

        self.assertEqual(
            len(cassette),
            len(response.context["object_list"]),
            "Response must contain as many Cassettes as expected.",
        )


class VariantTest(TestCase):
    """Includes test that don't fit into any particular class"""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

    def test_organ_list_no_id(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:organ_index"))

        self.assertEquals(Organ.objects.all().count(), len(response.json()))

    def test_home_template(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:home"))

        self.assertTemplateUsed(
            response, "home.html", "Response must use expected template."
        )

    def test_home_context(self):
        self.client.login(username="jmonagas", password="vehice1234")
        response = self.client.get(reverse("lab:home"))

        self.assertIn(
            "cassette", response.context, "Response context must contain expected data."
        )


class CassetteDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.fake = Faker()

    def test_detail_returns_json(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.get(reverse("lab:cassette_detail", kwargs={"pk": 1}))

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )

    def test_detail_updates_cassette(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:cassette_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "build_at": self.fake.date_time().isoformat(),
                    "correlative": self.fake.pyint(),
                    "organs": [49, 50],
                }
            ),
            content_type="application/json",
        )

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )

    def test_detail_updates_no_build_at(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:cassette_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "correlative": self.fake.pyint(),
                    "organs": [49, 50],
                }
            ),
            content_type="application/json",
        )

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )

    def test_detail_updates_no_correlative(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:cassette_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "build_at": self.fake.date_time().isoformat(),
                    "organs": [49, 50],
                }
            ),
            content_type="application/json",
        )

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )

    def test_detail_no_organs(self):
        self.client.login(username="jmonagas", password="vehice1234")

        response = self.client.post(
            reverse("lab:cassette_detail", kwargs={"pk": 1}),
            json.dumps(
                {
                    "build_at": self.fake.date_time().isoformat(),
                    "correlative": self.fake.pyint(),
                }
            ),
            content_type="application/json",
        )

        self.assertIn("cassette", response.json(), "Response must contain Cassette.")
        self.assertIn(
            "organs", response.json(), "Response must contain Cassette's organs."
        )

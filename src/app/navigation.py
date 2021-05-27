# -*- coding: utf-8 -*-
"""
.. module:: viewer.navigation
   :synopsis: Generate a navigation tree (left bar) for the user.

Each item in the navigation tree is a python dictionary with the
following fields::

    path: url to link to
    icon: icon to display
    section_name: text to display
    child_items: list of items to display nested to this item
    open: whether it should be expanded or not
"""

from django.urls import reverse
from django.utils.translation import ugettext
from accounts.models import UserProfile


def generate_navigation_tree(user, request):
    "Returns a custom navigation tree for the given user."
    if not user.is_authenticated():
        return anon_tree()
    tree = default_tree(user)
    expand(tree, request.path)
    return tree


def anon_tree():
    "Tree for anon users."
    return [{"path": reverse("root"), "icon": "home", "section_name": "Inicio"}]


def default_tree(user):
    usuario = UserProfile.objects.get(user=user)
    language = usuario.language
    menu = [
        {
            "path": "/",
            "icon": "ft-home",
            "section_name": "Inicio" if language == 1 else "Home",
        },
        {
            "path": "/ingresos",
            "icon": "ft-clipboard",
            "section_name": "Ingreso de Casos" if language == 1 else "Cases",
        },
        {
            "path": "/estudios",
            "icon": "ft-book",
            "section_name": "Estudios" if language == 1 else "Studies",
        },
        {
            "path": "/derivacion/0",
            "icon": "ft-users",
            "section_name": "Derivación" if language == 1 else "Derivation",
        },
    ]
    reports = []

    if user.userprofile.profile_id in (1, 2, 4, 5):
        reports.append(
            {
                "path": reverse("report:service"),
                "section_name": "Servicios" if language == 1 else "Services",
            }
        )
        reports.append(
            {
                "path": reverse("report:efficiency"),
                "section_name": "Rendimiento" if language == 1 else "Efficiency",
            },
        )
    if user.userprofile.profile_id in (1, 2):
        reports.append(
            {
                "path": reverse("report:control"),
                "section_name": "Jefe Tecnico" if language == 1 else "Tech Lead",
            }
        )

    if user.userprofile.profile_id in (1, 2) or user.userprofile.is_reviewer:
        menu.append(
            {
                "icon": "ft-check-square",
                "section_name": "Revisión" if language == 1 else "Review",
                "path": reverse("review:index"),
            },
        )

    menu.append(
        {
            "icon": "ft-pie-chart",
            "section_name": "Reportes" if language == 1 else "Reports",
            "child_items": reports,
        },
    )
    if user.userprofile.profile_id in (1, 3):
        menu.append(
            {
                "icon": "ft-grid",
                "section_name": "Laboratorio" if language == 1 else "Laboratory",
                "child_items": [
                    {
                        "path": reverse("lab:home"),
                        "section_name": "Inicio" if language == 1 else "Home",
                    },
                    {
                        "path": reverse("lab:cassette_build"),
                        "section_name": "Armar Cassettes"
                        if language == 1
                        else "Build Cassettes",
                    },
                    {
                        "path": reverse("lab:cassette_index"),
                        "section_name": "Indice Cassettes"
                        if language == 1
                        else "Index Cassettes",
                    },
                    {
                        "path": reverse("lab:slide_build"),
                        "section_name": "Armar Slides"
                        if language == 1
                        else "Build Slides",
                    },
                    {
                        "path": reverse("lab:slide_index"),
                        "section_name": "Indice Slides"
                        if language == 1
                        else "Index Slides",
                    },
                ],
            }
        )

    if user.userprofile.profile_id == 1:
        menu.append(
            {
                "path": "/admin",
                "icon": "ft-settings",
                "section_name": "Administración" if language == 1 else "Administration",
            }
        )

    return menu


def expand(tree, path):
    "Sets parent nodes as 'open' whenever a child node matches the path."
    for item in tree:
        if any(
            subitem.get("path", None) == path for subitem in item.get("child_items", [])
        ):
            item["open"] = True

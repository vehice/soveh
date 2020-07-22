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

def generate_navigation_tree(user, request):
    "Returns a custom navigation tree for the given user."
    if not user.is_authenticated():
        return anon_tree()
    tree = default_tree(user)
    expand(tree, request.path)
    return tree


def anon_tree():
    "Tree for anon users."
    return [
        {'path': reverse('root'),
         'icon': 'home',
         'section_name': "Inicio"}]


def default_tree(user):
    menu = [
        {
            'path': '/',
            'icon': 'ft-home',
            'section_name': "Inicio",
        },
        {
            'path': '/ingresos',
            'icon': 'ft-clipboard',
            'section_name': "Ingreso de Casos",
        },

    ]
    if user.userprofile.profile_id in (1,2,3):
        menu.append({
            'path': '/derivacion',
            'icon': 'ft-users',
            'section_name': "Derivación"
        })
    if user.userprofile.profile_id == 1:
        menu.append({
            'path': '/admin',
            'icon': 'ft-settings',
            'section_name': "Administración"
        })

    return menu

def expand(tree, path):
    "Sets parent nodes as 'open' whenever a child node matches the path."
    for item in tree:
        if any(subitem.get('path', None) == path
               for subitem in item.get('child_items', [])):
            item['open'] = True

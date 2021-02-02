from django.template import Library
from app.navigation import default_tree
from django.conf import settings
from utils import functions as fn
register = Library()

@register.filter(name='join_diagnostic')
def join_diagnostic(value):
    text = ''
    for i in value:
        text+= str(i.sample.index)+', '
    return text[:-2]

@register.filter(name='navigations')
def navigations(user):
    return default_tree(user)

@register.simple_tag
def settings_var(name):
    return getattr(settings, name, "")

# @register.translate
# def translate(value):
#     lang = fn.translation('en')
#     return getattr(settings, name, "")
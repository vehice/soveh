from django.template import Library
from app.navigation import default_tree
register = Library()

@register.filter(name='join_diagnostic')
def join_diagnostic(value):
    text = ''
    for i in value:
        text+= str(i.slice.cassette.sample.index)+', '
    return text[:-2]

@register.filter(name='navigations')
def navigations(user):
    return default_tree(user)
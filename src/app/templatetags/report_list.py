from django.template import Library
register = Library()

@register.filter(name='join_diagnostic')
def join_diagnostic(value):
    text = ''
    for i in value:
        text+= str(i.slice.cassette.sample.index)+', '
    return text[:-2]
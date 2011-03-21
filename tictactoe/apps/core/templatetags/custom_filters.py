from django import template

register = template.Library()

@register.filter(name='splitboard')

def splitboard(input):
    return [input.pieces[0:3], input.pieces[3:6], input.pieces[6:9]]

splitboard.is_safe = True

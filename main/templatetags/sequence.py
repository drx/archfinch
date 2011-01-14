from django import template


register = template.Library()


@register.filter
def sequence(value):
    '''
    Converts a list of items into its written representation,
     for example it would turn [1, 2, 3] to "1, 2 and 3".
    '''
    value = map(str, value)

    if len(value) == 0:
        return ''

    elif len(value) == 1:
        return value[0]

    else:
        return ', '.join(value[:-1]) + ' and ' + value[-1]

from django import template
from django.utils.timesince import timesince


register = template.Library()


@register.filter
def timesince_days(value):
    """
    Takes a datetime object and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
    then "0 minutes" is returned.

    Units used are years, months, weeks, days.
    Seconds and microseconds are ignored.  Up to two adjacent units will be
    displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
    possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.

    Times earlier than "24 hours" are displayed as "today".
    """
    from django.utils.timesince import timesince

    if not value:
        return u''
    try:
        t = timesince(value)
    except (ValueError, TypeError):
        return u''

    left, sep, right = t.partition(', ')
    
    if sep:
        if right.find('hour') != -1:
            return left + ' ago'

    else:
        if left.find('hour') != -1:
            return 'today'

    if t.find('minute') != -1:
        return 'today'

    return t + ' ago'
timesince_days.is_safe = False

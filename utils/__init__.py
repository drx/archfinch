import django.shortcuts

def render_to_response(template, dictionary=None, context_instance=None, mimetype=None):
    """
    A modification of render_to_response providing some default template variables.
    """

    if dictionary is None:
        dictionary = {}

    dictionary.setdefault('base', 'base.html')
    return django.shortcuts.render_to_response(template, dictionary=dictionary, context_instance=context_instance, mimetype=mimetype)

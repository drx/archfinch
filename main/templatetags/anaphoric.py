from django.template import Library
from django.template.base import Node
from django.utils.http import int_to_base36


register = Library()
class AIfNotEmptyNode(Node):
    child_nodelists = ('nodelist_test', 'nodelist_then')

    def __init__(self, nodelist_test, nodelist_then):
        self.nodelist_test, self.nodelist_then = nodelist_test, nodelist_then

    def __repr__(self):
        return "<AIfNotEmpty node>"

    def __iter__(self):
        for node in self.nodelist_test:
            yield node
        for node in self.nodelist_then:
            yield node

    def render(self, context):
        test = self.nodelist_test.render(context)
        context['it'] = test
        if test.strip():
            return self.nodelist_then.render(context)
        else:
            return ""


def aifnotempty(parser, token):
    """
    The ``{% aifnotempty %}`` tag evaluates the contents of its first subblock (``test``),
    and if it is not empty, returns the contents of its second subblock (``then``) rendered
    with an additional context variable ``it`` that is set to the rendered test subblock.

    ::

        {% aifnotempty %}
            ... lots of different things that might happen to all be empty ...
        {% then %}
            <div class="box">
            {{ it }}
            </div>
        {% endaifnotempty %}

    Here, the ``then`` block (the div) is only rendered if the test is nonempty. If it is nonempty,
    it is passed as the ``it`` variable.

    This is useful because it is otherwise difficult to check if the contents of a div are empty
    (alternatives require use of external JavaScript libraries such as jQuery, or CSS3, which is not
    standard yet.

    """
    nodelist_test = parser.parse(('then',))
    token = parser.next_token()
    nodelist_then = parser.parse(('endaifnotempty',))
    parser.delete_first_token()
    token = parser.next_token()
    return AIfNotEmptyNode(nodelist_test, nodelist_then)
aifnotempty = register.tag("aifnotempty", aifnotempty)


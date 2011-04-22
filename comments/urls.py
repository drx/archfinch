from django.conf.urls.defaults import *


urlpatterns = patterns('archfinch.comments.views',
    url(r'^add(?P<json>\.json)?$', 'add_comment', name='comment-add'),
)

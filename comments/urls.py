from django.conf.urls.defaults import *


urlpatterns = patterns('archfinch.comments.views',
    url(r'^add$', 'add_comment', name='comment-add'),
)

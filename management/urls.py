from django.conf.urls import patterns

urlpatterns = patterns(
    'management.views',
    (r'^$', 'index'),
    (r'^(?P<hit_id>\d+)/$', 'show_hit'),
)

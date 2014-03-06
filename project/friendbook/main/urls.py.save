from django.conf.urls import patterns, url
from main import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^tags/$', views.tags, name='tags'),
    url(r'^tags/(?P<tag_name>\w+)/$', views.tag, name='tag'),
    url(r'^add_link/$', views.add_link, name='add_link'),
)

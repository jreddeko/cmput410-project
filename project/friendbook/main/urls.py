from django.conf.urls import patterns, include, url
from main import views
from django.contrib import admin
admin.autodiscover()

#postwall url is just to test display only URI
urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^server_admin/$', views.server_admin, name='server_admin'),
    url(r'^newpost/$', views.newpost, name='newpost'),
    url(r'^authors$', views.users, name='users'),
    url(r'^author/$', views.users, name='users'),
    url(r'^wall/$', views.wall, name='wall'),
    url(r'^author/(?P<username>\w+)/$', views.user, name='user'),
    #url(r'^author/(?P<username>\w+)/posts$', views.posts, name='posts'),
    url(r'^author/(?P<user_id>\w+)/posts/$', views.posts, name='posts'),
    url(r'^author/(?P<user_id>\w+)/posts/(?P<post_id>\w+)/$', views.post, name='post'),
    url(r'^author/(?P<username>\w+)/friends$', views.friends, name='friends'),
    url(r'^author/(?P<username>\w+)/friends/$', views.friends, name='friends'),
    url(r'^author/(?P<username>\w+)/friends/(?P<friend_id>\w+)/$', views.friend, name='friend'),
    url(r'^author/(?P<username>\w+)/images$', views.images, name='images'),
    url(r'^author/(?P<username>\w+)/images/$', views.images, name='images'),
    url(r'^author/(?P<username>\w+)/images/(?P<image_id>\w+)/$', views.image, name='image'),
    url(r'^admin/', include(admin.site.urls))
)

from django.conf.urls import patterns, url
from main import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^server_admin/$', views.server_admin, name='server_admin'),
    url(r'^user$', views.users, name='users'),
    url(r'^user/$', views.users, name='users'),
    url(r'^user/(?P<username>\w+)/$', views.user, name='user'),
    url(r'^user/(?P<username>\w+)/post$', views.posts, name='posts'),
    url(r'^user/(?P<username>\w+)/post/$', views.posts, name='posts'),
    url(r'^user/(?P<username>\w+)/post/(?P<post_id>\w+)/$', views.post, name='post'),
    url(r'^user/(?P<username>\w+)/friends$', views.friends, name='friends'),
    url(r'^user/(?P<username>\w+)/friends/$', views.friends, name='friends'),
    url(r'^user/(?P<username>\w+)/friends/(?P<friend_id>\w+)/$', views.friend, name='friend'),
    url(r'^user/(?P<username>\w+)/image$', views.images, name='images'),
    url(r'^user/(?P<username>\w+)/image/$', views.images, name='images'),
    url(r'^user/(?P<username>\w+)/image/(?P<image_id>\w+)/$', views.image, name='image'),
)

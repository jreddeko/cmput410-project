from django.conf.urls import patterns, include, url
from main import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
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
    url(r'^admin/', include(admin.site.urls))
)

from django.conf.urls import patterns, include, url
from main import views
from django.contrib import admin
admin.autodiscover()


'''
The first 8 URIs are for viewing the website while the after 9th URI and on are
for the RESTful API.  For more information on this RESTful service, please read
the methods associated with them in views.py.
'''
urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^server_admin/$', views.server_admin, name='server_admin'),
    url(r'^newpost/$', views.newpost, name='newpost'),
    url(r'^friendship/$', views.friendship, name='friendship'),
    url(r'^friendship_accept/$', views.friendship_accept, name='friendship_accept'),
    url(r'^search_users/$', views.search_users, name='search_users'),
    url(r'^authors$', views.users, name='users'),
    url(r'^author/$', views.users, name='users'),
    url(r'^wall/$', views.wall, name='wall'),
    url(r'^author/(?P<username>\w+)/$', views.user, name='user'),
    url(r'^author/(?P<username>\w+)/posts$', views.posts, name='posts'),
    url(r'^author/(?P<username>\w+)/posts/$', views.posts, name='posts'),
    url(r'^author/(?P<username>\w+)/posts/(?P<post_id>\w+)$', views.post, name='post'),
    url(r'^author/(?P<username>\w+)/posts/(?P<post_id>\w+)/$', views.post, name='post'),
    url(r'^author/(?P<username>\w+)/friends$', views.friends, name='friends'),
    url(r'^author/(?P<username>\w+)/friends/$', views.friends, name='friends'),
    url(r'^author/(?P<username>\w+)/friends/(?P<friend_id>\w+)/$', views.friend, name='friend'),
    url(r'^author/(?P<username>\w+)/images$', views.images, name='images'),
    url(r'^author/(?P<username>\w+)/images/$', views.images, name='images'),
    url(r'^author/(?P<username>\w+)/images/(?P<image_id>\w+)/$', views.image, name='image'),
    url(r'^admin/', include(admin.site.urls))
)

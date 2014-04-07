from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from main import views
from django.contrib import admin
admin.autodiscover()


'''
The first 11 URIs are for viewing the website while the after 9th URI and on are
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
    url(r'^unfriend/$', views.unfriend, name='unfriend'),
    url(r'^search_users/$', views.search_users, name='search_users'),
    url(r'^authors$', views.users, name='users'),
    url(r'^author/$', views.users, name='users'),
    url(r'^wall/$', views.wall, name='wall'),
    url(r'^account/$', views.account, name='account'),
    url(r'^author/posts/$', views.posts, name='posts'),
    url(r'^author/(?P<userID>[\w\-]+)$', views.user, name='user'),
    url(r'^author/(?P<guid>[\w\-]+)/activate/$', views.activate_user, name='activate_user'),
    url(r'^author/(?P<guid>[\w\-]+)/modify/$', views.modify_user, name='modify_user'),
    url(r'^author/(?P<guid>[\w\-]+)/delete/$', views.delete_user, name='delete_user'),
    url(r'^posts/$', views.pubposts, name='pubposts'),
    url(r'^author/(?P<username>\w+)/posts/$', views.authorposts, name='authorposts'),
    url(r'^author/(?P<username>\w+)/posts/(?P<post_id>\w+)/$', views.post, name='post'),
    url(r'^author/(?P<username>\w+)/posts/(?P<post_id>\w+)/comments/$', views.comments, name='post'),
    url(r'^author/(?P<username>\w+)/friends/$', views.friends, name='friends'),
    url(r'^author/(?P<username>\w+)/friends/(?P<friend_id>\w+)/$', views.friend, name='friend'),
    url(r'^author/(?P<username>\w+)/images/$', views.images, name='images'),
    url(r'^images/$', views.images, name='images'),
    url(r'^admin/', views.server_admin, name='server_admin')


)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from main.models import Users, Posts
import json
import time
import datetime

def index(request):
  context = RequestContext(request)
  return render_to_response('main/index.html', context)

def server_admin(request):
  if request.method == 'GET':
    context = RequestContext(request)
    context['users'] = list(Users.objects.all())
    return render_to_response('main/server_admin.html', context)

def users(request):
  if request.method == 'GET':
    response_data = serializers.serialize('json', Users.objects.all())
    return HttpResponse(response_data)
  else:
    return HttpResponseNotAllowed

@csrf_exempt
def posts(request,username):
  context = RequestContext(request)
  return render_to_response('main/postwall.html', context)
  #if request.method == 'GET':
  #  artifact = Users.objects.get(username=username)
  #  response_data = serializers.serialize('json', Posts.objects.filter(owner_id=Users.objects.get(username=username)))
  #  return HttpResponse(response_data)
  #elif request.method == 'PUT':
  #  #add post
  #  #eg curl -X PUT -H "Content-Type: application/json" -d '{"title":"sometitle", "permission":"local", "content_type":"content_type", "content":"bunch of stuff", "visibility" :"poor"}' http://localhost:8000/friendbook/user/testperson/post 
  #  b = json.loads(request.body)
  #  post = Posts.objects.create(title = b['title'], owner_id=Users.objects.get(username=username), permission= b['permission'], content_type= b['content_type'], content=b['content'],  visibility = b['visibility'])
  #  post.source = request.build_absolute_uri() + "/" + str(post.id)
  #  post.save()
  #  response_data = serializers.serialize('json', [post])
  #  return HttpResponse(response_data)
  #else:
  #  return HttpResponseNotAllowed

@csrf_exempt
def post (request, username,post_id):
  if request.method == 'GET':
    reponse_data = serializers.serialize('json', Posts.objects.filter(owner_id=Users.objects.get(username=username)),use_natural_foreign_keys=True)
    return HttpResponse(reponse_data)
  elif request.method == 'POST':
    #modify post
    doSOmething()
  elif request.method == 'DELETE':
    #delete post
    #eg curl -X DELETE http://localhost:8000/friendbook/user/jasonreddekopp/post/1/
    Posts.objects.get(id=post_id).delete()
    return HttpResponse("Post Deleted\n")
  else: 
    return HttpResponseNotAllowed

def images (request, username):
  if request.method == 'GET':
    return HttpResponse("all images from " + username)
  else: 
    return HttpResponseNotAllowed

def image (request,username,image_id):
  if request.method == 'GET':
    return HttpResponse("image: " + image_id + ", from " + username)
  elif request.method == 'POST':
    #modify image
    doSomething()
  elif request.method == 'PUT':
    #add image
    doSomething()
  elif request.method == 'DELETE':
    #delete image
    doSomething()
  else: 
    return HttpResponseNotAllowed
  
def friends (request,username):
  return HttpResponse("all friends of " + username)


def friend (request, username, friend_id):
  if request.method == 'GET':
    return HttpResponse("friend : " + friend_id + ", from " + username)
  elif request.method == 'POST':
    #modify friend
    doSomething()
  elif request.method == 'PUT':
    #add friend
    doSomething()
  elif request.method == 'DELETE':
    #delete friend
    doSomething()
  else: 
    return HttpResponseNotAllowed
  
@csrf_exempt
def user(request, username):
  context=RequestContext(request)
  if request.method == 'GET':
    user = Users.objects.get(username=username)
    reponse_data = serializers.serialize('json', [user])
    return HttpResponse(reponse_data) 
  elif request.method == 'POST':
    user = Users.objects.get(username=request.POST['username'])
    if   (request.POST['method']=="delete"):
      Users.objects.get(username=request.POST['username']).delete()
      context['users'] = list(Users.objects.all())
      return render_to_response('main/server_admin.html', context)
    elif (request.POST['method']=="change"):
      context['userprofile']= [user]
      context['users'] = list(Users.objects.all())
      return render_to_response('main/auth_user.html', context)
    elif (request.POST['method']=="add"):
      user.active = True
      user.save()
      context['users'] = list(Users.objects.all())
      return render_to_response('main/server_admin.html', context)
    elif (request.POST['method']=="edit"):
      if 'name' in request.POST:
        doSomething()
      elif 'password' in request.POST:
        user.password = request.POST['password']
      elif 'role' in request.POST:
        user.role = request.POST['role']
      elif 'register_date' in request.POST:
        user.register_date = request.POST['register_date']
      elif 'github_account' in request.POST:
        user.github_account = request.POST['github_account']
      user.save()
      context['users'] = list(Users.objects.all())
      return render_to_response('main/server_admin.html', context)
    else:
      return HttpResponse("Error")

  elif request.method == 'PUT':
    #add user 
    #eg curl -X PUT -H "Content-Type: application/json" -d '{"password":"asdf", "role":"author"}' http://localhost:8000/friendbook/user/jasonreddekopp/
    if(Users.objects.filter(username=username).count() > 0 ):
      return HttpResponse("User exists\n")
    b = json.loads(request.body)
    Users.objects.create(username = username, password = b['password'], role = b['role'], active = False, github_account = "")
    return HttpResponse("User Created\n")
  elif request.method == 'DELETE':
    #delete user
    #eg curl -X DELETE http://localhost:8000/friendbook/user/jasonreddekopp/
    Users.objects.get(username=username).delete()
    return HttpResponse("User Deleted\n")
  else: 
    return HttpResponseNotAllowed

def doSomething():
  return null



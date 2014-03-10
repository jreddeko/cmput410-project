from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.db import IntegrityError
from main.models import Users, Posts
import json
import time
from datetime import datetime
import urllib2

@require_http_methods(["GET", "POST"])
def index(request):
  context = RequestContext(request)
  
  if (request.method == "POST"):
    username = request.POST["username"]
    password = request.POST["password"]
    role = "Author"
    registerDate = datetime.now().date()
    active = 0
    github = request.POST["github"]

    if ((username == "") or (password == "")):
      return render_to_response('main/index.html', {"signupError": "Error: one or more missing fields"}, context)

    try:
      newUser = Users(username=username, password=password, role=role, register_date=registerDate, active=active, github_account=github)
      newUser.save()
    except IntegrityError as e:
      return render_to_response('main/index.html', {"signupError": "Error: username already exists"}, context)

    return render_to_response('main/index.html', {"signupSuccess": "Successfully created an account! Before you can login, the website admin has to verify who you are"}, context)
  else:
    return render_to_response('main/index.html', context)

@require_http_methods(["POST"])
def login(request):
  context = RequestContext(request)
  
  username = request.POST["username"]
  password = request.POST["password"]

  if (len(Users.objects.filter(username = username, password = password)) == 1):
    request.session["loggedIn"] = True
    request.session["username"] = username

    return redirect("wall")
  else:
    return render_to_response("main/index.html", {"loginError": "Error: wrong username/password"}, context)

@require_http_methods(["GET"])
def logout(request):
  context = RequestContext(request)

  request.session["loggedIn"] = False
  request.session["username"] = ""

  return redirect("index")
  
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

def getGitHubEvents(userName):
    response = urllib2.urlopen("https://api.github.com/users/"+userName+"/events").read()
    eventList = json.loads(response)

@csrf_exempt
def wall(request):
    context = RequestContext(request)
    if request.method == "POST":
        title = request.POST["post_title"]
        author_id = Users.objects.get(username=request.session["username"])

        permission = request.POST["post_permissions"]
        source = request.POST["post_source"]
        origin = request.POST["post_origin"]
        category = request.POST["post_category"]
        description = request.POST["post_description"]
        content_type = "text/html"
        content = request.POST["post_content"]
        pub_date = datetime.now().date()

        post = Posts(title = title, source=source, origin=origin, category=category, description=description, content_type=content_type, content=content, owner_id=author_id, permission=permission, pub_date=pub_date, visibility = permission)
        post.save()
        return redirect("wall")
    else:
        #pull posts from db --> replace with restful service when it's done
        
        
        return render_to_response('main/postwall.html', context)

def newpost(request):
    print "got new post"
    context = RequestContext(request)
    return render_to_response('main/create_post.html', context)

@csrf_exempt
def posts(request, username):
  context = RequestContext(request)
  print request.method
  #return render_to_response('main/postwall.html', context)
  if request.method == 'GET':
    print "restful get requested"
    getGitHubEvents(request.session["username"])
    
    
    
    # TODO: change this!! hard coded username for now for testing
    userInfo = Users.objects.get(username=request.session["username"])
    #TODO grab username from session later
    return render(request, 'main/postwall.html', context)
    #return HttpResponse(response_data)
  elif request.method == 'POST':
    print "restful POST requested"
  else:
    return HttpResponseNotAllowed

@csrf_exempt
def post (request, username,post_id):
  print request.method
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



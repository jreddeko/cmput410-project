from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse,StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.db import IntegrityError
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from main.models import Users, Posts, Comment , Friends, PostsForm, CommentForm

import json
import time
from datetime import datetime
import urllib2

@require_http_methods(["GET", "POST"])
def index(request):
    context = RequestContext(request)

    if (request.method == "GET"):
        return render_to_response('main/index.html', context)
    else:
        if ("login" in request.POST):
            username = request.POST["username"]
            password = request.POST["password"]
            
            if (len(Users.objects.filter(username = username, password = password)) == 1):
                if ((Users.objects.get(username = username, password = password)).active == 1):
                  request.session["loggedIn"] = True
                  request.session["username"] = username
                
                  return redirect("wall")
                else:
                  return render_to_response("main/index.html", {"loginError": "Error: you haven't been verified by the website admin yet"}, context)
            else:
                return render_to_response("main/index.html", {"loginError": "Error: wrong username/password"}, context)
        else:
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

def getGitHubEvents(githubAccount):
    if githubAccount:
        response = urllib2.urlopen("https://api.github.com/users/"+githubAccount+"/events").read()
        jsonResponse = json.loads(response)
        for item in jsonResponse:
            item["pubDate"] = item["created_at"]
            del item["created_at"]
        return jsonResponse
    else:
        return list()

'''
This method is triggered by URI http://127.0.0.1:8000/wall/
to display the post wall.  The GET method just gets all posts that the
user has access to and sends it back to the postwall.html for display.

The POST method can be for two purposes: for creating new post or for
editting an existing post.  In both cases the data is taken from the POST
body and inserted into the main_posts database table.
'''
@csrf_exempt
@require_http_methods(["GET", "POST"])
def wall(request):
    context = RequestContext(request)
    userInfo = Users.objects.get(username=request.session["username"])
    if request.method == "POST":
        f = PostsForm(request.POST)
        if f.is_valid():
            new_post = f.save(commit=False)
            new_post.author = userInfo
            new_post.save()
        return redirect("wall")
    #GET request
    else:
        githubActivity = getGitHubEvents(userInfo.github_account)
        authorposts = Posts.objects.filter(author=userInfo)
        currentHost = request.get_host()
        #queryData = post2Json(currentHost, userInfo, authorposts, '').get("posts")
        #mergedList = githubActivity + queryData
        #mergedList.sort(key = lambda item:item["pubDate"], reverse = True)asdfsadfsfd
        posts = Posts.objects.filter(author=userInfo)
        comments = Comment.objects.filter(postguid__in=posts.values_list("guid"))
        #return HttpResponse(str(comments[0].postguid.guid))
        return render_to_response('main/postwall.html', 
            {"user_id": userInfo.id, "username": request.session['username'], "posts": posts, 'comments':comments, 'comment_form':CommentForm()}, context)

# for above method to grab all posts from friends. (Need to watch out for having duplicate posts!
#def getFriendsPosts(friendObj):
#   friendposts = {}
#   for result in friendObj:
#       allPosts = Posts.objects.filter(author=result)
#posts = allPosts.exclude(visibility = "public").order_by("-pub_date")
#friendposts[] = posts

def newpost(request):
    context = RequestContext(request)
    userInfo = Users.objects.get(username=request.session["username"])
    f = PostsForm()
    return render_to_response('main/create_post.html', {'form':f},context)

'''Displays all users within the system and as users as friends'''
def search_users(request):
    context = RequestContext(request)
    me = request.session["username"]
    users = list(Users.objects.all())
    friends = list(Friends.objects.all())

    friend_check = [x.username2.username for x in friends if x.username1.username == me] + [x.username1.username for x in friends if x.username2.username == me]
    print friend_check
    return render_to_response('main/search_user.html',{'users': users, 'me': me, 'friends': friends,'check': friend_check }, context)


def friendship(request):
    context = RequestContext(request)

    username1 = request.session["username"]
    user1 = Users.objects.get(username=username1)
    username2 = request.POST["friendname"]
    user2 = Users.objects.get(username=username2)
    accept = 0
    friends = Friends.objects.create(username1 = user1, username2=user2, accept=accept)
    return redirect("search_users")

def unfriend(request):
    context = RequestContext(request)

    username1 = request.session["username"]
    user1 = Users.objects.get(username=username1)
    username2 = request.POST["friendname"]
    user2 = Users.objects.get(username=username2)
    
    friends = Friends.objects.get(username1 = user1, username2=user2)
    friends.delete()
    return redirect("search_users")


def friendship_accept(request):
    context = RequestContext(request)
    if request.POST.get('request') == "Accept Request":
        username2 = request.session["username"]
        user2 = Users.objects.get(username=username2)
        username1 = request.POST["friendrequest"]
        user1 = Users.objects.get(username=username1)
        accept = 1
        friend_request = Friends.objects.get(username1 = user1, username2=user2)
        friend_request.accept = accept
        friend_request.save()

    elif request.POST.get('request') == "Decline Request":
        username2 = request.session["username"]
        user2 = Users.objects.get(username=username2)
        username1 = request.POST["friendrequest"]
        user1 = Users.objects.get(username=username1)
        
        friend_request = Friends.objects.get(username1 = user1, username2=user2)
        friend_request.delete()

    return redirect("search_users")
'''
    RESTful API for One author's posts
    
    This function is called when /author<username>/posts is called with GET, POST,
    PUT or DELETE HTTP requests and it shows information about author's
    posts.
    
    For GET requests, it returns all posts that the user has access to.
    For POST requests, if an id is specified and if the post exists, then it
    will update the post to newly given information in POST request body if 
    the specified user is the author.  If the post does not exist in the
    database, then it will create a new post with specified author as an author.
    For PUT request, it will modify the posts in the PUT request body that exists in
    the database already. For each post that does not exist in the database, the API
    will output an HTML string to warn the user.
    For DELETE request, it will delete all posts that the specified user has
    authored. Only the author and the server admin have the permission to do this.
'''
def comments(request,username,post_id):
    if request.method == "POST":
        if 'comment_submit_form' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                user = Users.objects.get(username=username)
                post = Posts.objects.get(guid=post_id)
                comment = Comment.objects.create(postguid = post, author = user, comment = form['comment'].value())
                return redirect("wall")

    return None
@csrf_exempt
def posts(request, username):
    context = RequestContext(request)
    currentHost = request.get_host()
    if request.method == 'GET':
        #need to add permission stuff when friends are implemented
        try:
            userInfo = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            return HttpResponse("<p>Username specified does not existin the database</p>\r\n", content_type="text/html")
        try:
            posts = Posts.objects.filter(author=userInfo).order_by("-pub_date")
        except ObjectDoesNotExist:
            return HttpResponse("<p>This user does not have any posts.</p>\r\n", content_type="text/html")
        
        jsonResult = post2Json(currentHost, userInfo, posts, "posts")
        # must have content_type parameter to not include HTTPResponse
        # values included in the JSON result to be passed to the AJAX call
        #return jsonResult
        return HttpResponse(json.loads(jsonResult), content_type="application/json")
    
    elif request.method == 'POST':
        print "restful POST requested"
        try:
            userInfo = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            return HttpResponse("<p>Username specified does not existin the databasee</p>\r\n", content_type="text/html")
        postList = json.loads(request.body).get("posts")

        errorMessage = []
        for post in postList:
            postId = post["guid"]
            try:
                old_post = Posts.objects.get(id=postId)
                title = post["title"]
                origin = post["origin"]
                source = post["source"]
                description = post["description"]
                contentType = post["content_type"]
                content = post["content"]
                categories = ",".join(post["categories"])
                pubDate = datetime.now().date()
                permission = post["visibility"]
                visibility = post["visibility"]
                
                old_post.title = title
                old_post.permission = permission
                old_post.source = source
                old_post.origin = origin
                old_post.category = categories
                old_post.description = description
                old_post.content_type = "text/html"
                old_post.content = content
                old_post.author = userInfo
                old_post.pub_date = datetime.now().date()
                old_post.visibility = permission
                old_post.save()
            except ObjectDoesNotExist:
                title = post["title"]
                origin = post["origin"]
                source = post["source"]
                description = post["description"]
                contentType = post["content_type"]
                content = post["content"]
                categories = ",".join(post["categories"])
                pubDate = datetime.now().date()
                permission = post["visibility"]
                visibility = post["visibility"]
                
                post = Posts(title = title, source=source, origin=origin, category=categories, description=description, content_type=contentType, content=content, author=userInfo, permission=permission, pub_date=pubDate, visibility = permission)
                post.save()

        return HttpResponse("<p>The posts have been created/modified successfully.</p>", content_type="text/html")
    elif request.method == 'PUT':
        try:
            userInfo = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            return HttpResponse("<p>Username specified does not existin the databasee</p>\r\n", content_type="text/html")
        postList = json.loads(request.body).get("posts")
        errorMessage = []
        for post in postList:
            postId = post["guid"]
            try:
                old_post = Posts.objects.get(id=postId)
                title = post["title"]
                origin = post["origin"]
                source = post["source"]
                description = post["description"]
                contentType = post["content_type"]
                content = post["content"]
                categories = ",".join(post["categories"])
                pubDate = datetime.now().date()
                permission = post["visibility"]
                visibility = post["visibility"]
                
                old_post.title = title
                old_post.permission = permission
                old_post.source = source
                old_post.origin = origin
                old_post.category = categories
                old_post.description = description
                old_post.content_type = "text/html"
                old_post.content = content
                old_post.author = userInfo
                old_post.pub_date = datetime.now().date()
                old_post.visibility = permission
                
                old_post.save()
            except ObjectDoesNotExist:
                errorMessage.append("<p>The specified post with ID "+str(post["guid"])+" does not exsit to be modified.</p>\r\n")

        errors = ",".join(errorMessage)
        return HttpResponse(errors, content_type="text/html")

        #create post in db
    elif request.method == 'DELETE':
        #only system admin and the author can do this!
        #check if the user is admin/author of post
        try:
            userInfo = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            return HttpResponse("<p>Username specified does not existin the databasee</p>\r\n", content_type="text/html")

        postInfo = Posts.objects.filter(author=userInfo)
        
        #server admins and the author has the permissions to delete the post
        for post in postInfo:
            if userInfo.role == "admin" or post.author.id == userInfo.id:
                    post.delete()
            else:
                return HttpResponse("<p>You do not have permission to delete these posts.</p>", content_type="text/html")
        return HttpResponse("<p>Posts have been deleted.</p>", content_type="text/html")
    else:
        return HttpResponseNotAllowed

'''
This method is called by posts to format the JSON as to appropriate format to be inserted into the database.
The jsonObject param is the JSON object that is shown in example_article.json in project webisite:
https://github.com/abramhindle/CMPUT404-project-socialdistribution/blob/master/example-article.json

It takes the JSON object and create and create a properly formatted JSON object.

@param querySet         django QuerySet object that is returned from database query to
posts table
@return JSON object to be sent as a response to an AJAX call
'''
#def json2Post(host, userData, jsonObject):

'''
This method is called by posts to format the query result as desired JSON format
as ones shown in example_article.json in project webisite:
https://github.com/abramhindle/CMPUT404-project-socialdistribution/blob/master/example-article.json

It takes the database query result and pases the QuerySet and create a properly formatted JSON object.

@param querySet         django QuerySet object that is returned from database query to 
                        posts table
@return JSON object to be sent as a response to an AJAX call
    
'''
def post2Json(host, userData, queryset, param):
    # TODO Date format is currently wrong! May have to change
    # the format when it's being inserted into DB
    post_lists = dict()
    querylist = []
    for queryResult in queryset:
        user = {}
        user["id"] = userData.id
        # TODO change this when we are communicating with other servers
        # they may have to specify their url?
        user["host"] = host
        user["displayname"] = userData.username
        user["url"] = host+"/author/"+str(userData.id)
        
        post = {}
        post["title"] = queryResult.title
        post["source"] = queryResult.source
        post["origin"] = queryResult.origin
        post["description"] = queryResult.description
        post["content_type"] = queryResult.content_type
        post["content"] = queryResult.content
        post["author"] = user
        categories = queryResult.category.split(",")
        post["categories"] = categories
        comments = {}
        post["comments"] = comments
        post["pubDate"] = queryResult.pub_date
        #should be SHA1 or UUID encrypted?
        post["guid"] = queryResult.id
        #post["visibility"] = queryResult.visibility
        querylist.append(post)
    post_lists["posts"] = querylist
    
    # curl requires differnt output
    return 
    if param != "posts":
        return json.loads(json.dumps(post_lists, default=date_handler))
    else:
        return json.dumps(json.dumps(post_lists, default=date_handler))

'''
date_handler function changes the date format to the one
that can be serialized by the json python library

@param obj      datetime object to be handled
@return         date format that can be serialized by the json library

'''
# code taken from:
# http://blog.codevariety.com/2012/01/06/python-serializing-dates-datetime-datetime-into-json/
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

'''
This method get the current host URL to be inserted into the database.
The URL is in form of http://IP address or domain name:port
'''
# code from http://fragmentsofcode.wordpress.com/2009/02/24/django-fully-qualified-url/
def current_site_url():
    """Returns fully qualified URL (no trailing slash) for the current site."""
    from django.contrib.sites.models import Site
    current_site = Site.objects.get_current()
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    port     = getattr(settings, 'MY_SITE_PORT', '')
    url = '%s://%s' % (protocol, current_site.domain)
    if port:
        url += ':%s' % port
    return url

'''
    RESTful API for getting information on one post specified in post_id
    of the URI
    
    This function is called when /author/<username>/posts/<post_id> is called with GET, POST,
    PUT or DELETE HTTP requests and it shows information about the specified post.
    
    For GET requests, it returns relevant information about the specified post.(the
    user must have access to this post!)
    For POST requests, if an id is specified and if the post exists, then it
    will update the post to newly given information in POST request body if
    the specified user is the author.  If the post does not exist in the
    database, then it will create a new post with specified author as an author.
    For PUT request, it will modify a post in the PUT request body.
    For DELETE request, it will delete all post if the user specified is an author of
    the post.
    
    @param request      information on HTTP Request
    @param username      (currently DB ID but should be SHA1 ID) of user in URI
    @param post_id      (currently DB ID but should be SHA1 ID) of post in URI
    
    @return             For GET, JSON representation of specified post information
                        FOR POST, message for either updated/added
                        FOR PUT, message indicating insertion of new post
                        For Delete, message indicating deletion of post
'''
@csrf_exempt
def post(request, username, post_id):
    if request.method == 'GET':
        #need to add permission stuff when friends are implemented
        userInfo = Users.objects.get(username=username)
        #used filter instead of get to use post2Json method
        post = Posts.objects.filter(id=post_id)
        currentHost = request.get_host()
        jsonResult = post2Json(currentHost, userInfo, post, '')
        # must have content_type parameter to not include HTTPResponse
        # values included in the JSON result to be passed to the AJAX call
        return HttpResponse(jsonResult, content_type="application/json")
    elif request.method == 'POST':
        # AJAX call by jQuery needs method to be POST to work so param
        # is passed to identify the intended HTTP method
        print type(request.POST)
        if "method" in request.POST:
            if request.POST["method"] == "delete":
                #check if the user is admin/author of post
                userInfo = Users.objects.get(username=username)
                postInfo = Posts.objects.get(id=post_id)
                
                #server admins and the author has the permissions to delete the post
                if userInfo.role == "admin" or postInfo.author.id == userInfo.id:
                    postInfo.delete()
                    print "author has permission"
                    return HttpResponse("<p>Post has been deleted.</p>", content_type="text/html")
                else:
                    print "no permission"
                    return HttpResponse("<p>You do not have permission to delete this post.</p>", content_type="text/html")
        # for curl POST methods!
        else:
            try:
                userInfo = Users.objects.get(username=username)
            except ObjectDoesNotExist:
                return HttpResponse("<p>Username specified does not existin the databasee</p>\r\n", content_type="text/html")
            try:
                #if the post exists, then modify it, if  not then create a new one.
                old_post = Posts.objects.get(id=post_id)
            except ObjectDoesNotExist:
                postList = json.loads(request.body).get("posts")
                for post in postList:
                    title = post["title"]
                    origin = post["origin"]
                    source = post["source"]
                    description = post["description"]
                    contentType = post["content_type"]
                    content = post["content"]
                    categories = ",".join(post["categories"])
                    pubDate = datetime.now().date()
                    permission = post["visibility"]
                    visibility = post["visibility"]
                    
                    post = Posts(title = title, source=source, origin=origin, category=categories, description=description, content_type=contentType, content=content, author=userInfo, permission=permission, pub_date=pubDate, visibility = permission)
                    post.save()
                return HttpResponse("<p>A new post has been created!</p>\r\n", content_type="text/html")
            # a post already exists with this ID so modify the old post
            postList = json.loads(request.body).get("posts")
            for post in postList:
                title = post["title"]
                origin = post["origin"]
                source = post["source"]
                description = post["description"]
                contentType = post["content_type"]
                content = post["content"]
                categories = ",".join(post["categories"])
                pubDate = datetime.now().date()
                permission = post["visibility"]
                visibility = post["visibility"]

                old_post.title = title
                old_post.permission = permission
                old_post.source = source
                old_post.origin = origin
                old_post.category = categories
                old_post.description = description
                old_post.content_type = "text/html"
                old_post.content = content
                old_post.author = userInfo
                old_post.pub_date = datetime.now().date()
                old_post.visibility = permission

                old_post.save()
            return HttpResponse("<p>The Specified post has been updated!</p>\r\n", content_type="text/html")
    elif request.method == 'PUT':
        try:
            userInfo = Users.objects.get(username=username)
            old_post = Posts.objects.get(id=post_id)
        except ObjectDoesNotExist:
            return HttpResponse("<p>Username/Post ID specified does not existin the databasee</p>\r\n", content_type="text/html")

        postList = json.loads(request.body).get("posts")
        for post in postList:
            title = post["title"]
            origin = post["origin"]
            source = post["source"]
            description = post["description"]
            contentType = post["content_type"]
            content = post["content"]
            categories = ",".join(post["categories"])
            pubDate = datetime.now().date()
            permission = post["visibility"]
            visibility = post["visibility"]

            old_post.title = title
            old_post.permission = permission
            old_post.source = source
            old_post.origin = origin
            old_post.category = categories
            old_post.description = description
            old_post.content_type = "text/html"
            old_post.content = content
            old_post.author = userInfo
            old_post.pub_date = datetime.now().date()
            old_post.visibility = permission

            old_post.save()
        return HttpResponse("<p>The Specified post has been updated!</p>\r\n", content_type="text/html")


    elif request.method == 'DELETE':
        #check if the user is admin/author of post
        userInfo = Users.objects.get(username=username)
        postInfo = Posts.objects.get(id=post_id)
        
        #server admins and the author has the permissions to delete the post
        if userInfo.role == "admin" or postInfo.author.id == userInfo.id:
            postInfo.delete()
            return HttpResponse("<p>Post has been deleted.</p>\r\n", content_type="text/html")
        #user specified is not author/server admin, so give them a warning
        else:
            return HttpResponse("<p>You do not have permission to delete this post.</p>\r\n", content_type="text/html")
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



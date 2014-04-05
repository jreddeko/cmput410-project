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
import uuid

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
    currentHost = request.get_host()
    me = request.session["username"]
    userInfo = Users.objects.get(username=me)
    if request.method == "POST":
        f = PostsForm(request.POST)
        if f.is_valid():
            new_post = f.save(commit=False)
            new_post.author = userInfo
            new_post.source = currentHost
            new_post.origin = currentHost
            #need the db guid field to be string
            #new_post.guid = uuid.uuid4().int
            new_post.save()
        else:
            print "invalid form"
    #GET request
    githubActivity = getGitHubEvents(userInfo.github_account)
    authorposts = Posts.objects.filter(author=userInfo)
    publicPosts = Posts.objects.filter(permission="PUBLIC").exclude(author=userInfo)
    
    friends = list(Friends.objects.all())
    friend_check = [x.username2 for x in friends if (x.username1 == me and x.accept== 1)] + [x.username1 for x in friends if (x.username2== me and x.accept== 1)]

    authorData = post2Json(currentHost, authorposts).get("posts")
    publicPosts = post2Json(currentHost, publicPosts).get("posts")
    serverOnlyPosts = getServerOnlyPosts(me, currentHost, friend_check)
    friendsPosts = getAllFriendPosts(me, currentHost, friend_check)
    
    print authorData
    print publicPosts
    print serverOnlyPosts
    print friendsPosts
    
    mergedList = githubActivity + authorData + publicPosts + serverOnlyPosts + friendsPosts
    mergedList.sort(key = lambda item:item["pubDate"], reverse = True)

    return render_to_response('main/postwall.html', 
        {"user_id": userInfo.id, "username": request.session['username'], "posts": mergedList, 'comment_form':CommentForm(),'friends': friend_check}, context)

def getAllFriendPosts(user, host, friendlist):
    postList = []
    for friend in friendlist:
        friendInfo = Users.objects.get(username=friend)
        friendServer = Friends.objects.filter(Q(username1=friend, username2=user)|Q(username2=friend, username1=user)).values("server")
        friendPosts = Posts.objects.filter(permission="FRIENDS", author=friendInfo)
        
        if friendServer[0].get("server"):
            friendPosts = post2Json(friendServer[0].get("server"), friendPosts).get("posts")
            postList += friendPosts
        else:
            friendPosts = post2Json(str(host), friendPosts).get("posts")
            postList += friendPosts
    return postList

def getServerOnlyPosts(user, host, friendlist):
    postList = []
    for friend in friendlist:
        friendInfo = Users.objects.get(username=friend)
        friendServer = Friends.objects.filter(Q(username1=friend, username2=user)|Q(username2=friend, username1=user)).values("server")
        friendPosts = Posts.objects.filter(permission="SERVERONLY", author=friendInfo)
        
        if friendServer[0].get("server") == "":
            friendPosts = post2Json(str(host), friendPosts).get("posts")
            postList += friendPosts
    return postList

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

    friend_check = [x.username2 for x in friends if x.username1 == me] + [x.username1 for x in friends if x.username2== me]
    request_check = [x.username2 for x in friends if (x.username1 == me and x.accept== 0)] + [x.username1 for x in friends if (x.username2== me and x.accept== 0)]
    return render_to_response('main/search_user.html',{'users': users, 'me': me, 'friends': friends,'check': friend_check,'request_pend': request_check }, context)


def friendship(request):
    context = RequestContext(request)

    user1 = request.session["username"]
    user2 = request.GET["friendname"]

    friends = Friends.objects.create(username1 = user1, username2=user2, accept=0)
    return redirect("search_users")

def unfriend(request):
    context = RequestContext(request)

    user1 = request.session["username"]
    user2 = request.GET["friendname"]

    try:
            friends = Friends.objects.get(username1 = user1, username2=user2)
    except:
            friends = Friends.objects.get(username1 = user2, username2=user1)

    friends.delete()
    return redirect("search_users")


def friendship_accept(request):
    context = RequestContext(request)
    if request.GET.get('request') == "Accept Request":
        user2 = request.session["username"]
        user1 = request.GET["friendrequest"]
        friend_request = Friends.objects.get(username1=user1, username2=user2)
        friend_request.accept = 1
        friend_request.save()

    elif request.GET.get('request') == "Decline Request":
        user2 = request.session["username"]
        user1 = request.GET["friendrequest"]
        friend_request = Friends.objects.get(username1=user1, username2=user2)
        friend_request.delete()

    return redirect("search_users")

def comments(request,username,post_id):
    if request.method == "POST":
        if 'comment_submit_form' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                user = Users.objects.get(username=username)
                post = Posts.objects.get(guid=post_id)
                comment = Comment.objects.create(postguid = post, author = user, comment = form['comment'].value())
                return redirect("wall")
    elif request.method == "GET":
        currentHost = request.get_host()
        post = Posts.objects.get(guid=post_id)
        comment = Comment.objects.filter(postguid=post)
        jsonResult = comment2Json(currentHost, comment)
        return HttpResponse(json.loads(json.dumps(json.dumps(jsonResult))), content_type="application/json")

'''
    RESTful API for Currently Authenticated user's posts
    
    This function is called when /author/posts/ is called with GET HTTP requests
    and it shows information about author's posts.
    
    For GET requests, it returns all posts that the user has access to.
    '''
@csrf_exempt
def posts(request):
    username = request.session["username"]
    context = RequestContext(request)
    currentHost = request.get_host()
    if request.method == 'GET':
        userInfo = Users.objects.get(username=username)
        authorposts = Posts.objects.filter(author=userInfo)
        publicPosts = Posts.objects.filter(permission="PUBLIC").exclude(author=userInfo)
        currentHost = request.get_host()
        friends = list(Friends.objects.all())
        friend_check = [x.username2 for x in friends if (x.username1 == username and x.accept== 1)] + [x.username1 for x in friends if (x.username2== username and x.accept== 1)]
        
        authorData = post2Json(currentHost, authorposts).get("posts")
        publicPosts = post2Json(currentHost, publicPosts).get("posts")
        serverOnlyPosts = getServerOnlyPosts(username, currentHost, friend_check)
        friendsPosts = getAllFriendPosts(username, currentHost, friend_check)
        postList = dict()
        postList["posts"] = []
        mergedList = authorData + publicPosts + serverOnlyPosts + friendsPosts
        mergedList.sort(key = lambda item:item["pubDate"], reverse = True)
        for listitem in mergedList:
            postList["posts"].append(listitem)
    
        return HttpResponse(json.loads(json.dumps(json.dumps(postList))), content_type="application/json")

'''
    RESTFul for http://localhost:8000/posts
    
    GET all public posts within the server.
'''
def pubposts(request):
    if request.method == "GET":
        currentHost = request.get_host()
        publicPosts = Posts.objects.filter(permission="PUBLIC", source=currentHost)
        publicPosts = post2Json(currentHost, publicPosts)
        return HttpResponse(json.loads(json.dumps(json.dumps(publicPosts))), content_type="application/json")

'''
    RESTFul for http://localhost:8000/author/<author_username>/posts
    
    GET all public posts within the server.
'''
def authorposts(request, username):
    if request.method == "GET":
        currentHost = request.get_host()
        userInfo = Users.objects.get(username=username)
        publicPosts = Posts.objects.filter(permission="PUBLIC", author=userInfo)
        friendPosts = Posts.objects.filter(permission="FRIENDS", author=userInfo)
        serveronlyPosts = Posts.objects.filter(permission="SERVERONLY", author=userInfo)
        
        publicPosts = post2Json(currentHost, publicPosts).get("posts")
        friendPosts = post2Json(currentHost, friendPosts).get("posts")
        serveronlyPosts = post2Json(currentHost, serveronlyPosts).get("posts")
        
        postList = dict()
        postList["posts"] = []
        mergedList = publicPosts + serveronlyPosts + friendPosts
        mergedList.sort(key = lambda item:item["pubDate"], reverse = True)
        for listitem in mergedList:
            postList["posts"].append(listitem)
        
        return HttpResponse(json.loads(json.dumps(json.dumps(postList))), content_type="application/json")


'''
This method is called by posts to format the posts query result as desired JSON format
as ones shown in example_article.json in project website:
https://github.com/abramhindle/CMPUT404-project-socialdistribution/blob/master/example-article.json

It takes the database query result and pases the QuerySet and create a properly formatted JSON object.

@param host             current host address
@param querySet         django QuerySet object that is returned from database query to  posts table
@return JSON object to be sent as a response to an AJAX call
    
'''
def post2Json(host, queryset):
    post_lists = dict()
    querylist = []
    for queryResult in queryset:
        authorInfo = Users.objects.get(id=queryResult.author.id)
        user = {}
        user["id"] = authorInfo.id
        # TODO change this when we are communicating with other servers
        # they may have to specify their url?
        user["host"] = host
        user["displayname"] = authorInfo.username
        user["url"] = host+"/author/"+str(authorInfo.id)
        
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
        #need to make a function to get all comments of this post
        comments = []
        
        getCommentJson = urllib2.urlopen("http://"+host+"/author/"+queryResult.author.username+"/posts/"+str(queryResult.guid)+"/comments/").read()
        
        commentjson = json.loads(getCommentJson)
        for comment in commentjson:
            comments.append(comment)
        
        post["comments"] = comments
        post["pubDate"] = queryResult.pubdate
        #should be SHA1 or UUID encrypted?
        post["guid"] = queryResult.guid
        post["visibility"] = queryResult.permission
        querylist.append(post)
    post_lists["posts"] = querylist
    
    return json.loads(json.dumps(post_lists, default=date_handler))

'''
    This method is called by comments to format the comments query result as desired JSON format
    as ones shown in example_article.json in project website:
    https://github.com/abramhindle/CMPUT404-project-socialdistribution/blob/master/example-article.json
    
    It takes the database query result and pases the QuerySet and create a properly formatted JSON object.
    
    @param host             current host address
    @param querySet         django QuerySet object that is returned from database query to comments table
    
    @return JSON object to be sent as a response to an AJAX call
'''
def comment2Json(host, queryset):
    comment_lists = dict()
    querylist = []
    for queryResult in queryset:
        authorInfo = Users.objects.get(id=queryResult.author.id)
        user = {}
        user["id"] = authorInfo.id
        # TODO change this when we are communicating with other servers
        # they may have to specify their url?
        user["host"] = host
        user["displayname"] = authorInfo.username

        comment = {}
        comment["author"] = user
        comment["comment"] = queryResult.comment
        comment["pubDate"] = queryResult.pubDate
        comment["guid"] = queryResult.guid

        querylist.append(comment)

    return json.loads(json.dumps(querylist, default=date_handler))


'''
date_handler function changes the date format to the one
that can be serialized by the json python library

@param obj      datetime object to be handled
@return         date format that can be serialized by the json library

'''
# code taken and modified from:
# http://blog.codevariety.com/2012/01/06/python-serializing-dates-datetime-datetime-into-json/
def date_handler(obj):
    return obj.strftime('%b %d, %Y at %H:%M' ) if hasattr(obj, 'isoformat') else obj

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
        jsonResult = post2Json(currentHost, post)
        # must have content_type parameter to not include HTTPResponse
        # values included in the JSON result to be passed to the AJAX call
        return HttpResponse(jsonResult, content_type="application/json")
    elif request.method == 'POST':
        # AJAX call by jQuery needs method to be POST to work so param
        # is passed to identify the intended HTTP method
        if "method" in request.POST:
            if request.POST["method"] == "delete":
                #check if the user is admin/author of post
                userInfo = Users.objects.get(username=username)
                postInfo = Posts.objects.get(guid=post_id)
                
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



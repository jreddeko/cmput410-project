from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse,StreamingHttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.db import IntegrityError
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from main.models import Users, Posts, Comment , Friends, ServerPermission, PostsForm, CommentForm, Image, ImageForm, UserForm, ServerPermissionForm
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied

import json
import time
from datetime import datetime
import urllib
import urllib2
import uuid
import urlparse

@require_http_methods(["GET", "POST"])
def index(request):
    context = RequestContext(request)
    if (request.method == "GET"):
        logout(request)
        return render_to_response('main/index.html', context)
    else:
        if ("login" in request.POST):
            username = request.POST["username"]
            password = request.POST["password"]
            
            if (len(Users.objects.filter(username = username, password = password)) == 1):
                if ((Users.objects.get(username = username, password = password)).active == 1):
                  request.session["loggedIn"] = True
                  request.session["username"] = username
                  request.session["guid"] = Users.objects.get(username = username).guid
                
                  return redirect("wall")
                else:
                  return render_to_response("main/index.html", {"loginError": "Error: you haven't been verified by the website admin yet"}, context)
            else:
                return render_to_response("main/index.html", {"loginError": "Error: wrong username/password"}, context)
        else:
            guid = uuid.uuid4()
            username = request.POST["username"]
            password = request.POST["password"]
            role = "Author"
            registerDate = datetime.now().date()
            active = 0
            github = request.POST["github"]
            
            try:
                newUser = Users(guid = guid, username=username, password=password, role=role, register_date=registerDate, active=active, github_account=github)
                newUser.save()
            except IntegrityError as e:
                return render_to_response('main/index.html', {"signupError": "Error: username already exists"}, context)
            
            return render_to_response('main/index.html', {"signupSuccess": "Successfully created an account! Before you can login, the website admin has to verify who you are"}, context)

@require_http_methods(["GET", "POST"])
def account(request):
  context = RequestContext(request)
  guid = request.session["guid"]
  message = ""
  error = ""

  if (request.method == "POST"):
    if (len(Users.objects.exclude(guid = guid).filter(username = request.POST["username"])) == 0):
      Users.objects.filter(guid = guid).update(username = request.POST["username"], password = request.POST["password"], github_account = request.POST["github"])
      message = "Account successfully updated"
    else:
      error = "Username already exists"

  user = Users.objects.get(guid = guid)
  return render_to_response("main/account.html", {"username": user.username, "password": user.password, "github": user.github_account, "message": message, "error": error}, context)

@require_http_methods(["GET"])
def logout(request):
  context = RequestContext(request)

  request.session["loggedIn"] = False
  request.session["username"] = ""
  request.session["guid"] = ""

  return redirect("index")
  

@staff_member_required
def server_admin(request):
    context = RequestContext(request)

    article_posts = get_server_permission('can_share_posts')
    article_images = get_server_permission('can_share_images')

    if request.method == 'POST':

        share_posts = request.POST.get('public_posts')
        share_images = request.POST.get('public_images')

        article_posts.value = True if share_posts else False   
        article_posts.save() 
        article_images.value = True if share_images else False
        article_images.save() 

    context['users'] = list(Users.objects.all())
    context['share_posts'] = article_posts.value
    context['share_images'] = article_images.value
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
            stripedDate = item["pubDate"].replace('Z', '')
            stripedDate = stripedDate.replace('T', ' ')
            postDate = datetime.strptime(stripedDate, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y at %H:%M')
            item["pubDate"] = postDate
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
        f = PostsForm(request.POST,request.FILES)
        if f.is_valid():
            new_post = f.save(commit=False)
            new_post.author = userInfo
            new_post.source = currentHost
            new_post.origin = currentHost
            #need the db guid field to be string
            new_post.guid = uuid.uuid4()
            new_post.save()
        else:
            print "invalid form"
    #GET request
    githubActivity = getGitHubEvents(userInfo.github_account)
    authorposts = Posts.objects.filter(author=userInfo)
    publicPosts = Posts.objects.filter(permission="PUBLIC").exclude(author=userInfo)
    
    friends = list(Friends.objects.all())
    friend_check = [x.username2 for x in friends if (x.username1 == me and x.accept== 1)] + [x.username1 for x in friends if (x.username2== me and x.accept== 1)]
    
    friend_infos = []
    for friend in friend_check:
        friendDict = dict()
        friendUser = Users.objects.get(username=friend)
        friendDict["username"] = friend
        friendDict["guid"] = friendUser.guid
        friend_infos.append(friendDict)

    authorData = post2Json(currentHost, authorposts).get("posts")
    publicPosts = post2Json(currentHost, publicPosts).get("posts")
    serverOnlyPosts = getServerOnlyPosts(me, currentHost, friend_check)
    friendsPosts = getAllFriendPosts(me, currentHost, friend_check)
    
    mergedList = githubActivity + authorData + publicPosts + serverOnlyPosts + friendsPosts
    mergedList.sort(key = lambda item:datetime.strptime((item["pubDate"]), '%b %d, %Y at %H:%M'), reverse = True)

    return render_to_response('main/postwall.html', {"user_id": userInfo.guid, "username": request.session['username'], "posts": mergedList, "comment_form":CommentForm(), "friends": friend_infos}, context)

'''
    This method gets all the posts made by the currently authenticated
    user's friends by querying the database.
    
    @param  user        currently authenticated user
    @param  host        current host
    @param  friendlist  username list of friends
    @return             list of all posts
'''
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

'''
    This method gets all the posts made by the currently authenticated
    user's friends within the same server by querying the database.
    
    @param  user        currently authenticated user
    @param  host        current host
    @param  friendlist  username list of friends
    @return             list of all posts
'''
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

'''
    Navigate to the Create Post page to display the django form for
    post creation
'''
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

def comments(request,userID,post_id):
    if request.method == "POST":
        if 'comment_submit_form' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                user = Users.objects.get(guid=userID)
                post = Posts.objects.get(guid=post_id)
                comment = Comment.objects.create(guid=uuid.uuid4(), postguid = post, author = user, comment = form['comment'].value())
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
    if not can_share_posts(username):
        return HttpResponseForbidden()
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
    RESTFul for http://localhost:8000/author/<author UUID>/posts
    
    GET all posts made by the user.
'''
def authorposts(request, user_id):
    username = request.session["username"]

    if not can_share_posts(username):
        return HttpResponseForbidden()
    if request.method == "GET":
        currentHost = request.get_host()
        userInfo = Users.objects.get(guid=user_id)
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

@staff_member_required
def activate_user(request, guid):
    context = RequestContext(request)
    if request.method == "POST":
        user = Users.objects.get(guid=guid)
        user.active = True
        user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@staff_member_required
def delete_user(request, guid):
    context = RequestContext(request)
    if request.method == "POST":
        user = Users.objects.get(guid=guid)
        user.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@staff_member_required
def modify_user(request, guid):
    context = RequestContext(request)
    user = Users.objects.get(guid=guid)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('server_admin')
        
    form = UserForm(instance=user)
    return render_to_response('main/modify_user.html', {'form':form}, context)

def post2Json(host, queryset):
    post_lists = dict()
    querylist = []
    for queryResult in queryset:
        authorInfo = Users.objects.get(guid=queryResult.author.guid)
        user = {}
        user["id"] = authorInfo.guid
        # TODO change this when we are communicating with other servers
        # they may have to specify their url?
        user["host"] = host
        user["displayname"] = authorInfo.username
        user["url"] = host+"/author/"+str(authorInfo.guid)
        
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
        req = urllib2.Request("http://"+host+"/author/"+str(queryResult.author.guid)+"/posts/"+str(queryResult.guid)+"/comments/")
        print req
        getCommentJson = urllib2.urlopen(req).read()
        
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
        authorInfo = Users.objects.get(guid=queryResult.author.guid)
        user = {}
        user["id"] = authorInfo.guid
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
    
    This function is called when /posts/<post_id> is called with GET, POST,
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
    @param post_id      (currently DB ID but should be SHA1 ID) of post in URI
    
    @return             For GET, JSON representation of specified post information
                        FOR POST, message for either updated/added
                        FOR PUT, message indicating insertion of new post
                        For Delete, message indicating deletion of post
'''
@csrf_exempt
def post(request, post_id):
    username = request.session["username"]
    currentHost = request.get_host()
    if request.method == 'GET':
        userInfo = Users.objects.get(username=username)
        post = Posts.objects.filter(guid=post_id)
        jsonResult = post2Json(currentHost, post)
        return HttpResponse(jsonResult, content_type="application/json")
    if request.method == 'POST':
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
            userInfo = Users.objects.get(username=username)
            old_post = Posts.objects.get(guid=post_id)

            postList = urlparse.parse_qs(request.body)
                
            title = str(postList["title"][0])
            origin = currentHost
            source = currentHost
            description = str(postList["description"][0])
            contentType = "text/html"
            content = str(postList["content"][0])
            categories = str(postList["category"][0])
            pubDate = datetime.now().date()
            visibility = str(postList["permission"][0])

            old_post.title = title
            old_post.source = source
            old_post.origin = origin
            old_post.category = categories
            old_post.description = description
            old_post.content_type = "text/html"
            old_post.content = content
            old_post.author = userInfo
            old_post.pubDate = datetime.now().date()
            old_post.visibility = visibility

            old_post.save()
            
            userInfo = Users.objects.get(username=username)
            post = Posts.objects.filter(guid=post_id)
            jsonResult = post2Json(currentHost, post)
            
            return HttpResponse(json.dumps(jsonResult), content_type="application/json")
    elif request.method == 'PUT':
        try:
            userInfo = Users.objects.get(username=username)
            old_post = Posts.objects.get(guid=post_id)
        except ObjectDoesNotExist:
            return HttpResponse("<p>Username/Post ID specified does not existin the databasee</p>\r\n", content_type="text/html")

        postList = json.loads(urlparse.parse_qs(request.body))
        for post in postList:
            title = post["title"]
            origin = post["origin"]
            source = post["source"]
            description = post["description"]
            contentType = post["content_type"]
            content = post["content"]
            categories = ",".join(post["categories"])
            pubDate = datetime.now().date()
            visibility = post["visibility"]

            old_post.title = title
            old_post.source = source
            old_post.origin = origin
            old_post.category = categories
            old_post.description = description
            old_post.content_type = "text/html"
            old_post.content = content
            old_post.author = userInfo
            old_post.pubDate = datetime.now().date()
            old_post.visibility = permission

            old_post.save()
        return HttpResponse("<p>The Specified post has been updated!</p>\r\n", content_type="text/html")


    elif request.method == 'DELETE':
        #check if the user is admin/author of post
        userInfo = Users.objects.get(username=username)
        postInfo = Posts.objects.get(guid=post_id)
        
        #server admins and the author has the permissions to delete the post
        if userInfo.role == "admin" or postInfo.author.guid == userInfo.guid:
            postInfo.delete()
            return HttpResponse("<p>Post has been deleted.</p>\r\n", content_type="text/html")
        #user specified is not author/server admin, so give them a warning
        else:
            return HttpResponse("<p>You do not have permission to delete this post.</p>\r\n", content_type="text/html")
    else:
        return HttpResponseNotAllowed

def images(request):
    context = RequestContext(request)
    username=request.session["username"]
    if not can_share_images(username):
        return HttpResponseForbidden()
    if request.method == 'GET':
        form = ImageForm()
        images = Image.objects.filter(user=Users.objects.get(username=request.session["username"]))
        return render_to_response('main/images.html', {'images':images,'form':form}, context)
    elif request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        
        if form.is_valid():
            image_up = form.save(commit=False)
            print user
            image_up.user = Users.objects.get(username=request.session["username"])
            image_up.save()
            return HttpResponseRedirect('/images/')
            
        else:   
            form = form.errors
            return HttpResponseRedirect('/images/')
    else:
        return HttpResponseNotAllowed
  

@require_http_methods(["POST"])
@csrf_exempt
def friends (request,username):
  if request.method == 'POST':
    data = json.loads(request.body)
    match = []
    try:
        name = Users.objects.get(guid=data["author"]).username
    except:
        name = ""

    if username == data["author"]:
        authorlist = data["authors"]
        for author in authorlist:
            
            try:
                friendname = Users.objects.get(guid=author).username
            except:
                friendname = ""

            num_results = Friends.objects.filter(username1=friendname,username2=name,accept=1).count() + Friends.objects.filter(username1=name,username2=friendname,accept=1).count()

            if num_results > 0:
                match.append(author)
        newjson  = dict()
        newjson["query"] = "friends"
        newjson["author"] = username
        newjson["friends"] = match
        return HttpResponse(json.loads(json.dumps(json.dumps(newjson))), content_type="application/json")

    else:
        return HttpResponse("<p>You do not have appropriate json author.</p>\r\n", content_type="text/html") 
  else: 
    return HttpResponseNotAllowed

@require_http_methods(["POST"])
@csrf_exempt
def friend (request, username, friend_id):
    if request.method == 'POST':
        try:
            friendname = Users.objects.get(guid=friend_id).username
        except:
            friendname = ""

        try:
            name = Users.objects.get(guid=username).username
        except:
            name = ""

        num_results = Friends.objects.filter(username1=friendname,username2=name,accept=1).count() + Friends.objects.filter(username1=name,username2=friendname,accept=1).count()
        conclusion = ""
        
        if num_results > 0:
            conclusion = "YES"
        else:
            conclusion = "NO"

        newjson  = dict()
        newjson["query"] = "friends"
        newjson["authors"] = [username,friend_id]
        newjson["friends"] = conclusion

        return HttpResponse(json.loads(json.dumps(json.dumps(newjson))), content_type="application/json")
    else: 
        return HttpResponseNotAllowed

@require_http_methods(["POST"])
@csrf_exempt
def friendrequest (request):
  if request.method == 'POST':
    data = json.loads(request.body)
    host = "http://" + request.get_host() + "/"
    print host
    print data["author"]["host"]
    if data["author"]["host"] == host:
        if data["friend"]["author"]["host"] == host:
            friends = Friends.objects.create(username1 = data["author"]["displayname"], username2=data["friend"]["author"]["displayname"], accept=0)
            return HttpResponse("<p>Friend Request has been sent!</p>\r\n", content_type="text/html")
        else:
            friends = Friends.objects.create(username1 = data["author"]["displayname"], username2=data["friend"]["author"]["displayname"], accept=0,server=data["friend"]["author"]["host"])
            return HttpResponse("<p>Friend Request has been sent!</p>\r\n", content_type="text/html")
    elif data["friend"]["author"]["host"] == host:
            friends = Friends.objects.create(username2 = data["author"]["displayname"], username1=data["friend"]["author"]["displayname"], accept=0,server=data["author"]["host"])
            return HttpResponse("<p>Friend Request has been sent!</p>\r\n", content_type="text/html")
    else:
        return HttpResponse("<p>Friend Request using wrong host!</p>\r\n", content_type="text/html")
  else: 
    return HttpResponseNotAllowed
  
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
@csrf_exempt
def user(request, userID):
  context=RequestContext(request)

  if (request.method == "GET"):
    if (len(Users.objects.filter(guid = userID)) == 1):
      #if the user exists, return their data
      user = Users.objects.get(guid = userID)
      return HttpResponse(json.dumps({"guid": userID, "username": user.username, "password": user.password, "role": user.role, "registerDate": str(user.register_date), "active": user.active, "github": user.github_account}))
    else:
      #if the user doesn't exist, return an error message
      return HttpResponse(json.dumps({"error": "The requested user does not exist"}))
  elif ((request.method == "POST") or (request.method == "PUT")):
    data = json.loads(request.body)
    if (len(Users.objects.exclude(guid = userID).filter(username = data["username"])) == 1):
      #is the username already taken?
      return HttpResponse(json.dumps({"error": "Username already exists"}))
    elif (len(Users.objects.filter(guid = userID)) == 1):
      #if the user exists, update it
      Users.objects.filter(guid = userID).update(username = data["username"], password = data["password"], github_account = data["github"])
    else:
      #if the user doesn't exist, create it
      username = data["username"]
      password = data["password"]
      role = "Author"
      registerDate = datetime.now().date()
      active = 0
      github = data["github"]
      newUser = Users(guid = userID, username=username, password=password, role=role, register_date=registerDate, active=active, github_account=github)
      newUser.save()
    user = Users.objects.get(guid = userID)
    return HttpResponse(json.dumps({"guid": userID, "username": user.username, "password": user.password, "role": user.role, "registerDate": str(user.register_date), "active": user.active, "github": user.github_account}))
  else:
    if (len(Users.objects.filter(guid = userID)) == 1):
      #if the user exists, delete it
      Users.objects.get(guid = userID).delete()
      return HttpResponse(json.dumps({"message": "The user has been successfully deleted"}))
    else:
      #if the user doesn't exist, return an error message
      return HttpResponse(json.dumps({"error": "The requested user does not exist"}))


def get_server_permission(perm):
    try:
        return ServerPermission.objects.get(permission=perm)
    except:
        return ServerPermission.objects.create(permission=perm,value=False)

def can_share_posts(username):
    try:
        ServerPermission.objects.get(permission='can_share_posts', value=True)
        return True 
    except:
        if Users.objects.filter(username = username).exists():
            return True
        return False

def can_share_images(username):
    try:
        ServerPermission.objects.get(permission='can_share_images', value=True)
        return True 
    except:
        if Users.objects.filter(username = username).exists():
            return True
        return False

def doSomething():
  return null

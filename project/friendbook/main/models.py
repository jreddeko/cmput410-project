from django.db import models
from django.forms import ModelForm

PERMISSION_LEVELS = (
    ("PUBLIC"    ,"public"),
    ("FOAF"      , "friends of all friends"),
    ("FRIENDS"   , "friends"),
    ("PRIVATE"   , "private"),
    ("SERVERONLY", "server only"),
)

class Users(models.Model):
    username = models.TextField(unique=True)
    password = models.TextField()
    role = models.TextField()
    register_date = models.DateTimeField(auto_now_add=True, blank=True)
    active = models.BooleanField()
    github_account = models.TextField(blank=True)

class Posts(models.Model):
    guid = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=30)
    source = models.URLField(blank=True)
    origin = models.URLField(blank=True)
    description = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    content_type = models.CharField(max_length=30)
    content = models.TextField()
    author   = models.ForeignKey(Users)
    permission = models.CharField(max_length=100,choices=PERMISSION_LEVELS)
    pubdate = models.DateTimeField(auto_now_add=True, blank=True)


class Comment(models.Model):
    guid = models.CharField(max_length=100,primary_key=True)
    postguid = models.ForeignKey(Posts)
    author = models.ForeignKey(Users)
    comment = models.TextField()
    pubDate = models.DateTimeField(auto_now_add=True, blank=True)

class Friends(models.Model):
    username1 = models.TextField()
    username2 = models.TextField()
    accept = models.BooleanField()
    server = models.TextField(blank=True)

class Image(models.Model):
    user = models.ForeignKey(Users)
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images')

class ImageForm(ModelForm):
    class Meta:
        model = Image
        exclude = {'user',}

class PostsForm(ModelForm):
    class Meta:
        model = Posts
        fields = ['title','category','description','content','permission']
        exclude = ("author",)

    def __init__(self, *args, **kwargs):
        super(PostsForm, self).__init__(*args, **kwargs)
        self.fields['permission'].widget.attrs.update({'class':'col-sm-9 form-control','style':"width: 90%;"})
        self.fields['title'].widget.attrs.update({'style':"width: 90%;",'placeholder':"Please input the author's username."})
        self.fields['category'].widget.attrs.update({'style':"width: 90%;",'placeholder':"(e.g. Medical, Health)"})
        self.fields['description'].widget.attrs.update({'style':"width: 90%;",'placeholder':"Description of the post"})

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        exclude = ("postguid",)
        def __init__(self, *args, **kwargs):
            super(PostsForm, self).__init__(*args, **kwargs)
            self.fields['coment'].widget.attrs.update({'style':"width: 90%;"})
        
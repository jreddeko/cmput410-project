from django.db import models

class Users(models.Model):
    username = models.TextField(unique=True)
    password = models.TextField()
    role = models.TextField()
    register_date = models.DateTimeField(auto_now_add=True, blank=True)
    active = models.BooleanField()
    github_account = models.TextField(blank=True)

class Posts(models.Model):
    title = models.CharField(max_length=30)
    source = models.TextField(blank=True)
    origin = models.TextField(blank=True)
    category = models.TextField(blank=True)
    description = models.TextField(blank=True)
    content_type = models.TextField()
    content = models.TextField()
    owner_id = models.ForeignKey(Users)
    permission = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)
    visibility = models.TextField()

class Comment(models.Model):
	post_id = models.ForeignKey(Posts)
	owner_id = models.ForeignKey(Users)
	comment = models.TextField()
	pub_date = models.DateTimeField(auto_now_add=True, blank=True)

class Friends(models.Model):
	username1 = models.ForeignKey(Users, related_name= "friends_username1",to_field="username")
	username2 = models.ForeignKey(Users, related_name= "friends_username2",to_field="username")
	accept = models.BooleanField()



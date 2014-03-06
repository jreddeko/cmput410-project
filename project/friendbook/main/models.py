from django.db import models

class Users(models.Model):
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)
    role = models.CharField(max_length=30)
    register_date = models.DateField()
    active = models.BooleanField()
    github_account = models.TextField(blank=True)


class Posts(models.Model):
	title = models.CharField(max_length=30)
	source = models.CharField(max_length=30)
	origin = models.CharField(max_length=30)
	owner_id = models.ForeignKey(Users)
	permission = models.CharField(max_length=30)
	content_type = models.CharField(max_length=30)
	content = models.TextField()
	pub_date = models.DateField()
	visibility = models.CharField(max_length=30)

class Comment(models.Model):
	post_id = models.ForeignKey(Posts)
	owner_id = models.ForeignKey(Users)
	comment = models.TextField()
	pub_date = models.DateField()

class Friends(models.Model):
	username1 = models.ForeignKey(Users, related_name= "friends_username1")
	username2 = models.ForeignKey(Users, related_name= "friends_username2")
	accept = models.BooleanField()



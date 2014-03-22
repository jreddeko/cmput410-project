from django.test import TestCase
from main.models import Users, Posts
from datetime import datetime

class FriendbookTestCase(TestCase):
    def setUp(self):
        self.bob = Users.objects.create(username = "bob", password = 'ajsdkfljaslkdf', role = 'author', active = False, github_account = "")
        self.fred = Users.objects.create(username = "fred", password = '1231234124', role = 'author', active = False, github_account = "")
        self.tom = Users.objects.create(username = "tom", password = 'ajsdkfljaslkdf', role = 'author', active = False, github_account = "")
        self.dick = Users.objects.create(username = "dick", password = '45klejwkrl', role = 'author', active = False, github_account = "")
        
        self.testPost = Posts.objects.create(title="test title", source="", origin="http://google.ca", category="testing, results", description="test description", content_type="text/html", content="<p>test Content</p>", owner_id=self.bob, permission="private", visibility="private")
	def test_users(self):
		users = Users.objects.filter(username=self.bob.username)
		self.assertEqual(users.count(),1)
		bob = users.get(username=self.bob.username)
		self.assertEqual(bob.username, self.bob.username)
		self.assertEqual(bob.password, self.bob.password)
		self.assertEqual(bob.role,self.bob.role)

    def test_posts(self):
    	post = Posts.objects.get(pk=self.testPost.id)
        self.assertEqual(post.title,self.testPost.title)
        self.assertEqual(post.source,self.testPost.source)
        self.assertEqual(post.origin,self.testPost.origin)
        self.assertEqual(post.description,self.testPost.description)
        self.assertEqual(post.permission,self.testPost.permission)
        self.assertEqual(post.visibility,self.testPost.visibility)
        self.assertEqual(post.content,self.testPost.content)
        self.assertEqual(post.content_type,self.testPost.content_type)
        c = Client()
        c.post('author/bob/posts/', )


# Create your tests here.

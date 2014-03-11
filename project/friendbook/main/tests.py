from django.test import TestCase
from main.models import Users, Posts
from datetime import datetime

class FriendbookTestCase(TestCase):
    def setUp(self):
        Users.objects.create(username = "bob", password = 'ajsdkfljaslkdf', role = 'author', active = False, github_account = "")
        Users.objects.create(username = "fred", password = '1231234124', role = 'author', active = False, github_account = "")
        Users.objects.create(username = "tom", password = 'ajsdkfljaslkdf', role = 'author', active = False, github_account = "")
        Users.objects.create(username = "dick", password = '45klejwkrl', role = 'author', active = False, github_account = "")
        if Users.objects.filter(username="bob").exists():
			return
        else:
			Users.objects.create(username = "bob", password = '45klejwkrl', role = 'author', active = False, github_account = "")

        author1 = Users.objects.get(username="tom")
        author2 = Users.objects.get(username="bob")
        today = datetime.now().date()
        Posts.objects.create(title="test title", source="", origin="http://google.ca", category="testing, results", description="test description", content_type="text/html", content="<p>test Content</p>", owner_id=author1.id, permission="private", pub_date=today, visibility="private")
        if Posts.objects.filter(owner_id=author1).exists():
			return
        else:
			Posts.objects.create(title="test title", source="", origin="http://google.ca", category="testing, results", description="test description", content_type="text/html", content="<p>test Content</p>", owner_id=author1.id, permission="private", pub_date=today, visibility="private")
        
        Posts.objects.create(title="test title2", source="http://google.ca", origin="", category="testing2, results2", description="test description2", content_type="text/html", content="<p>test Content2</p>", owner_id=author2.id, permission="private", pub_date=today, visibility="private")
        
        if Posts.objects.filter(owner_id=author2).exists():
			return
        else:
			Posts.objects.create(title="test title2", source="http://google.ca", origin="", category="testing2, results2", description="test description2", content_type="text/html", content="<p>test Content2</p>", owner_id=author2.id, permission="private", pub_date=today, visibility="private")
    def test_users(self):
        users = Users.objects.filter(username="bob")
        self.assertEqual(users.count(),1)
        bob = users.get(username="bob")
        self.assertEqual(bob.username, "bob")
        self.assertEqual(bob.password, "ajsdkfljaslkdf")
        self.assertEqual(bob.role,'author')

    def test_posts(self):
        author = Users.objects.get(username="bob")
        post = Posts.objects.filter(owner_id=author.id)
        self.assertEqual(post.count(),0)
        self.assertEqual(post.title, "test title2")
        self.assertEqual(post.source, "http://google.ca")
        self.assertEqual(post.origin, "")
        self.assertEqual(post.description, "test title2")
        self.assertEqual(post.permission, "private")
        self.assertEqual(post.visibility, "private")
        self.assertEqual(post.content, "<p>test Content2</p>")
        self.assertEqual(post.content_type, "text/html")


# Create your tests here.

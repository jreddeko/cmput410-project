from django.test import TestCase
from main.models import Users, Posts
class AnimalTestCase(TestCase):
	def setUp(self):
		Users.objects.create(username = "bob", password = 'ajsdkfljaslkdf', role = 'author', active = False, github_account = "")
		Users.objects.create(username = "fred", password = '1231234124', role = 'author', active = False, github_account = "")
		Users.objects.create(username = "tom", password = 'ajsdkfljaslkdf', role = 'author', active = False, github_account = "")
		Users.objects.create(username = "dick", password = '45klejwkrl', role = 'author', active = False, github_account = "")
		if Users.objects.filter(username="bob").exists():
			return
		else:
			Users.objects.create(username = "bob", password = '45klejwkrl', role = 'author', active = False, github_account = "")

	def test_users(self):
		users = Users.objects.filter(username="bob")
		self.assertEqual(users.count(),1)
		bob = users.get(username="bob")
		self.assertEqual(bob.username, "bob")
		self.assertEqual(bob.password, "ajsdkfljaslkdf")
		self.assertEqual(bob.role,'author')

# Create your tests here.

import os
from datetime import datetime
import pytz
utc=pytz.UTC

def populate():
    add_user(username="gayoung", password="test", role="author", active=1, git="gayoung")
    add_user(username="matt", password="test", role="author", active=1, git="")
    add_user(username="bob", password="test", role="author", active=1, git="")
    add_user(username="david", password="test", role="author", active=1, git="")
    add_user(username="sarah", password="test", role="author", active=1, git="")

def add_user(username, password, role, active, git):
    today = utc.localize(datetime.now())
    user = Users.objects.get_or_create(username=username, password=password, role=role, register_date=today, active=active, github_account=git)[0]
    return user

def add_friend(username1, username2, accept):
    user1Info = Users.objects.get(username=username1)
    user2Info = Users.objects.get(username=username2)
    friend = Friends.objects.get_or_create(username1=user1Info, username2=user2Info, accept=accept)
    return friend

# Start execution here!
if __name__ == '__main__':
    print "Starting Rango population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'friendbook.settings')
    from main.models import Users, Posts, Comment, Friends
    populate()
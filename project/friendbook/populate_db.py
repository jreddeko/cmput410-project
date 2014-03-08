import os
from datetime import datetime

def populate():
    add_user(id=1, username="gayoung", password="test", role="author", active=1, git="gayoung")

def add_user(id, username, password, role, active, git):
    today = datetime.now().date()
    user = Users.objects.get_or_create(id=id, username=username, password=password, role=role, register_date=today, active=active, github_account=git)[0]
    return user

# Start execution here!
if __name__ == '__main__':
    print "Starting Rango population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'friendbook.settings')
    from main.models import Users, Posts, Comment, Friends
    populate()
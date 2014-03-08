from django.contrib import admin

from main.models import Users, Posts, Comment, Friends

admin.site.register(Users)
admin.site.register(Posts)
admin.site.register(Comment)
admin.site.register(Friends)

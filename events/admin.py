from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Fav)
admin.site.register(Event)
admin.site.register(Comment)
admin.site.register(Notification)
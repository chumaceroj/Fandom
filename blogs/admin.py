from django.contrib import admin
# Importing Blog & Comment models
from .models import Blog, Comment

# Registers models
admin.site.register(Blog)
admin.site.register(Comment)


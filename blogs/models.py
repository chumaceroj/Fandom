from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Blog(models.Model):
    title = models.CharField(max_length=200)
    # The content of the Blog
    content = models.TextField()
    # ForeignKey links blog to the User account
    # If the User deletes their account, keep the blog on the site (author = null)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Automatically saves the exact date & time of creation
    created_at = models.DateTimeField(auto_now_add=True)
    # Y/N for oprhaning 
    is_orphaned = models.BooleanField(default=False)
    # Y/N for anonymization
    is_anonymous = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
class Comment(models.Model):
    # Links comment to specific Blog post (one-way connection)
    # "related_name" is a shortcut: allows us to grab all comments by looking at a Blog
    # Automatically deletes comments from deleted Blog
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name = 'comments')
    # Links comment to User
    # If the User deletes their account, keep the comment (author = null)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_orphaned = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Comment by {self.author} at {self.created_at} on {self.blog.title}"
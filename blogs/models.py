from django.db import models
from django.contrib.auth.models import User


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
        return f"{self.title} by {self.get_display_author()}"
    
    def orphan(self):
        """Permanently remove the author link, but the content stays posted"""
        self.author = None
        self.is_orphaned = True
        self.save() # saves the changes to the database

    def can_edit(self):
        """Checks if the blog can still be edited"""
        if self.is_orphaned:
            return False
        return True
    
    def anonymize(self):
        """Hide author from public but keep the link in the database"""
        self.is_anonymous = True
        self.save()

    def deanonymize(self):
        """Reveal author again"""
        self.is_anonymous = False
        self.save()

    def transfer(self, new_owner):
        """Transfer blog ownership to another user"""
        self.author = new_owner
        self.save()
        
    def get_display_author(self):
        """Returns the name to display publicly"""
        if self.is_orphaned:
            return "orphan_account"
        if self.is_anonymous:
            return "Anonymous"
        if self.author is None: # only reaches if is_orphaned is False
            return "deleted_user"
        return self.author.username

    
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
    
    def orphan(self):
        self.author = None
        self.is_orphaned = True
        self.save()

    def can_edit(self):
        if self.is_orphaned:
            return False
        return True
    
    def anonymize(self):
        self.is_anonymous = True
        self.save()

    def deanonymize(self):
        self.is_anonymous = False
        self.save()

    def get_display_author(self):
        if self.is_orphaned:
            return "orphan_account"
        if self.is_anonymous:
            return "Anonymous"
        if self.author is None:
            return "deleted_user"
        return self.author.username
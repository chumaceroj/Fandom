from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog, Comment, Profile, Collaboration, Invitation, TransferRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q


def index(request): # request is an object Django creates every time someone visits a page (request.user, request.method, request.POST, request.path)
    # Grab all Blog objects from the database, newest first
    blogs = Blog.objects.all().order_by('-created_at')
    # Send the blogs to the HTML template to be displayed
    # 'blogs/index.html' is the template file path
    # {'blogs': blogs} passes the data to the template
    # so {{ blogs }} in the HTML can access it
    return render(request, 'blogs/index.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    # tries to find a blog with the given id, and returns 404 page if not found,
    # with the blog_id coming from the URL
    blog = get_object_or_404(Blog, id = blog_id)
    # sends the blog to the HTML template
    return render(request, 'blogs/detail.html', {'blog': blog})

def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id) # finds the blog in the database
    # only the author can edit, and only if not orphaned
    # If someone tries to visit /blogs/name/edit/ but they're not the author, 
    # redirect them back to the blog page
    if not blog.can_edit(request.user):
        return redirect('blog_detail', blog_id=blog_id)
   
    # request.method tells us HOW the user got here
    # 'GET' = they clicked a link to visit the edit page (show the form)
    # 'POST' = they filled out the form and clicked Save (process the data)
    if request.method == 'POST': #
        # request.POST is a dictionary of all the form data
        # 'title' and 'content' match the "name" attributes in the HTML form
        blog.title = request.POST.get('title') # gets what they typed in the title field
        blog.content = request.POST.get('content') # gets what they typed in the content field
        blog.save() # Save changes to the database
        # After saving, redirect to the blog detail page
        # blog_detail is the name we gave this URL in urls.py
        return redirect('blog_detail', blog_id=blog_id)
    
    # If GET request, just show the edit form with current data filled in
    return render(request, 'blogs/edit_blog.html', {'blog': blog})

def orphan_blog(request, blog_id):
    # only allows POST requests so someone can't type in a URL to orphan a story
    # they must click the button, which sends POST
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)
        
        # only blog author can orpahn it
        if blog.author == request.user: # request.user is whoevers logged in
            blog.orphan()

        # redirect to the blog page after orphaning
        return redirect('blog_detail', blog_id=blog_id)
    
def anonymize_blog(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)

        if blog.author == request.user:
            if blog.is_anonymous:  
                blog.deanonymize()
            else:
                blog.anonymize()
    return redirect('blog_detail', blog_id=blog_id)

def transfer_blog(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)
        if blog.author == request.user:
            # Get the username they typed in
            username = request.POST.get('new_owner_username')
            try:
                # Try to find that user
                new_owner = User.objects.get(username=username)
                blog.transfer(new_owner)
            except User.DoesNotExist:
                # Username doesn't exist — just redirect back
                pass
    return redirect('blog_detail', blog_id=blog_id)

@login_required
def add_comment(request, blog_id):
    # get the specific blog post using its ID/return a 404 page if it doesn't exist
    blog = get_object_or_404(Blog, id=blog_id)
    # if the user just submitted a post request
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        parent_comment = None

        # if replying to a comment, get the parent
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)

        if content:
            #create a new comment and save it to the database
            Comment.objects.create(
                #link it to the blog object
                blog = blog,
                author = request.user,
                parent = parent_comment,
                # save the text the user submitted
                content = content
        )
        
    # redirect browser to the blog page & show the new comment
    return redirect('blog_detail', blog_id=blog.id)

@login_required
def anonymize_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
        
    if comment.can_edit(request.user):
        if comment.is_anonymous:
            comment.deanonymize()
        else:
            comment.anonymize()
        
    return redirect('blog_detail', blog_id=comment.blog.id)

@login_required     
def orphan_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
        
    if comment.can_edit(request.user):
        comment.orphan()

    return redirect('blog_detail', blog_id=comment.blog.id)

def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if not comment.can_edit(request.user):
        return redirect('blog_detail', blog_id=comment.blog.id)
    if request.method == 'POST':
        comment.content = request.POST.get('content')
        comment.save()
        return redirect('blog_detail', blog_id=comment.blog.id)
    return render(request, 'blogs/edit_comment.html', {'comment': comment})

def profile(request, username):
    profile_user = get_object_or_404(User, username=username) # Find the user by their username
    
    try: # Find their profile (bio)
        user_profile = Profile.objects.get(user=profile_user)
    except Profile.DoesNotExist:
        user_profile = None
    
    blogs = Blog.objects.filter( # Get their blogs, excluding orphaned and anonymized
        author=profile_user,
        is_orphaned=False,
        is_anonymous=False
    ).order_by('-created_at')
    
    # Get blogs where this user is a collaborator
    collab_blog_ids = Collaboration.objects.filter(
        user=profile_user,
        role='collaborator'
    ).values_list('blog_id', flat=True)
    
    collab_blogs = Blog.objects.filter(
        id__in=collab_blog_ids,
        is_orphaned=False,
        is_anonymous=False
    ).order_by('-created_at')
    
    # Combine owned and collab blogs, sorted by date
    from itertools import chain
    all_blogs = sorted(
        chain(blogs, collab_blogs),
        key=lambda b: b.created_at,
        reverse=True
    )
    
    comments = Comment.objects.filter( # Get their comments, excluding orphaned and anonymized
        author=profile_user,
        is_orphaned=False,
        is_anonymous=False
    ).order_by('-created_at')
    
    return render(request, 'blogs/profile.html', { # Send everything to the template
        'profile_user': profile_user,
        'user_profile': user_profile,
        'blogs': all_blogs,
        'comments': comments,
    })

def edit_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    if profile_user != request.user: # Only the profile owner can edit their bio
        return redirect('profile', username=username)
    
    try: # Get or create their profile
        user_profile = Profile.objects.get(user=profile_user)
    except Profile.DoesNotExist:
        user_profile = Profile.objects.create(user=profile_user, biography='') # creates a blank bio if never created
    if request.method == 'POST':
        user_profile.biography = request.POST.get('biography')
        user_profile.save()
        return redirect('profile', username=username)
    return render(request, 'blogs/edit_profile.html', {'user_profile': user_profile})

def create_blog(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        blog = Blog.objects.create(
            title=title,
            content=content,
            author=request.user
        )
        Collaboration.objects.create(
            blog=blog,
            user=request.user,
            role='owner'
        )
        # send invitations to collaborators if any usernames were entered
        collaborator_usernames = request.POST.get('collaborator_usernames', '')
        if collaborator_usernames.strip():
            for username in collaborator_usernames.split(','):
                username = username.strip()
                if not username:
                    continue
                try:
                    invited_user = User.objects.get(username=username)
                except User.DoesNotExist:
                    continue
                if invited_user == request.user:
                    continue
                Invitation.objects.create(
                    blog=blog,
                    invited_by=request.user,
                    invited_user=invited_user,
                )
        return redirect('blog_detail', blog_id=blog.id)
    return render(request, 'blogs/create_blog.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            # if user enters the wrong information
            return render(request, 'blogs/login.html', {'error': 'Invalid credentials. Re-enter your username and password.'})
    return render(request, 'blogs/login.html')

def logout_user(request):
    logout(request)
    return redirect('index')

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # checks that username doesn't already exist
        if User.objects.filter(username=username).exists():
            return render(request, 'blogs/register.html', {'error': 'Username already taken.'})
        
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('index')
    return render(request, 'blogs/register.html')

def profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'blogs/profile_settings.html')

def delete_account(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        user = request.user
        logout(request)  # log them out first
        user.delete()    # triggers Cascade for profile, SET_NULL for blogs/comments
        return redirect('index')
    return render(request, 'blogs/delete_account.html')

def change_username(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        method = request.POST.get('method')  # preserves old username
        
        if User.objects.filter(username=new_username).exists(): # Check new username isn't taken
            return render(request, 'blogs/change_username.html', {'error': 'Username already taken.'})
        
        if method == 'preserve_old_username': # Freeze current username on all existing blogs and comments
            Blog.objects.filter(author=request.user).update(original_author_name=request.user.username)
            Comment.objects.filter(author=request.user).update(original_author_name=request.user.username)
        
        # Change the username
        request.user.username = new_username
        request.user.save()
        
        return redirect('profile', username=new_username)
    return render(request, 'blogs/change_username.html')

def post_settings(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if not blog.is_owner(request.user):
        return redirect('blog_detail', blog_id=blog_id)
    
    collaborators = Collaboration.objects.filter(blog=blog).exclude(role='owner')
    pending_invites = Invitation.objects.filter(blog=blog, status='pending')
    
    return render(request, 'blogs/post_settings.html', {
        'blog': blog,
        'collaborators': collaborators,
        'pending_invites': pending_invites,
    })

def invite_collaborator(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)
        if not blog.is_owner(request.user):
            return redirect('blog_detail', blog_id=blog_id)
        
        username = request.POST.get('collaborator_username')
        try:
            invited_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('post_settings', blog_id=blog_id)
        
        if invited_user == request.user:
            return redirect('post_settings', blog_id=blog_id)
        if Collaboration.objects.filter(blog=blog, user=invited_user).exists():
            return redirect('post_settings', blog_id=blog_id)
        existing_invite = Invitation.objects.filter(blog=blog, invited_user=invited_user).first()
        if existing_invite:
            if existing_invite.status == 'pending':
                return redirect('post_settings', blog_id=blog_id)
            # if previously declined or accepted, reset to pending
            existing_invite.status = 'pending'
            existing_invite.save()
            return redirect('post_settings', blog_id=blog_id)
        
        Invitation.objects.create(
            blog=blog,
            invited_by=request.user,
            invited_user=invited_user,
        )
        return redirect('post_settings', blog_id=blog_id)
    return redirect('index')


def accept_invitation(request, invitation_id):
    if request.method == 'POST':
        invitation = get_object_or_404(Invitation, id=invitation_id)
        if invitation.invited_user != request.user:
            return redirect('notifications')
        
        invitation.status = 'accepted'
        invitation.save()
        
        Collaboration.objects.create(
            blog=invitation.blog,
            user=request.user,
            role='collaborator'
        )
        return redirect('notifications')
    return redirect('notifications')


def decline_invitation(request, invitation_id):
    if request.method == 'POST':
        invitation = get_object_or_404(Invitation, id=invitation_id)
        if invitation.invited_user != request.user:
            return redirect('notifications')
        
        invitation.status = 'declined'
        invitation.save()
        return redirect('notifications')
    return redirect('notifications')


def remove_collaborator(request, blog_id, collaboration_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)
        if not blog.is_owner(request.user):
            return redirect('post_settings', blog_id=blog_id)
        
        collaboration = get_object_or_404(Collaboration, id=collaboration_id, blog=blog)
        if collaboration.role != 'owner':
            collaboration.delete()
        return redirect('post_settings', blog_id=blog_id)
    return redirect('index')


def leave_collaboration(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)
        collaboration = Collaboration.objects.filter(blog=blog, user=request.user, role='collaborator').first()
        if collaboration:
            collaboration.delete()
        return redirect('blog_detail', blog_id=blog_id)
    return redirect('index')


def reassign_owner(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)
        if not blog.is_owner(request.user):
            return redirect('post_settings', blog_id=blog_id)
        
        new_owner_collab_id = request.POST.get('new_owner_id')
        try:
            new_owner_collab = Collaboration.objects.get(
                id=new_owner_collab_id, blog=blog, role='collaborator'
            )
        except Collaboration.DoesNotExist:
            return redirect('post_settings', blog_id=blog_id)
        
        new_owner = new_owner_collab.user
        
        new_owner_collab.role = 'owner'
        new_owner_collab.save()
        
        old_owner_collab, created = Collaboration.objects.get_or_create(
            blog=blog, user=request.user,
            defaults={'role': 'owner'}
        )
        old_owner_collab.role = 'collaborator'
        old_owner_collab.save()
        
        blog.transfer(new_owner)
        return redirect('blog_detail', blog_id=blog_id)
    return redirect('index')

@login_required
def notifications(request):
    # all pending collab invites
    pending_invitations = Invitation.objects.filter(
        invited_user=request.user,
        status='pending'
    ).order_by('-created_at')

    # all approved/denied transfer requests that haven't been dismissed by this user
    transfer_notifications = TransferRequest.objects.filter(
        (Q(requester=request.user, requester_notified=False) |
         Q(target_user_identifier=request.user.username, target_notified=False)),
        status__in=['APPROVED', 'DENIED']
    ).order_by('-created_at')
    
    return render(request, 'blogs/notifications.html', {
        'pending_invitations': pending_invitations,
        'transfer_notifications' : transfer_notifications,
    })

# clear/dismiss transfer notifications once viewed
@login_required
def clear_transfer_notification(request, transfer_id):
    if request.method == 'POST':
        # get transfer request matching transfer_id & requester
        transfer = get_object_or_404(
            TransferRequest, 
            Q(requester=request.user) | Q(target_user_identifier=request.user.username),
            id=transfer_id,
        )
        # mark as dismissed only for whichever account clicked "Dismiss"
        if transfer.requester == request.user:
            transfer.requester_notified = True
        if transfer.target_user_identifier == request.user.username:
            transfer.target_notified = True
        
        transfer.save()
    return redirect('notifications')

# only logged-in users can access this view
@login_required
def request_admin_transfer(request, blog_id):
    # save the blog ID (404 error if not found)
    blog = get_object_or_404(Blog, id=blog_id)
    
    if blog.author != request.user:
        # show error message if unauthorized
        messages.error(request, "You do not have permission to transfer this post.")
        # redirect back to blog details
        return redirect('index')

    if request.method == 'POST':
        # save the target username entered in the form
        target_identifier = request.POST.get('target_user_identifier', '').strip()
        
        if target_identifier:
            # check if target user exists in FanVerse
            user_exists = User.objects.filter(
                Q(username=target_identifier) | Q(email=target_identifier)
            ).exists()

            if not user_exists:
                messages.error(
                    request,
                    "The username you entered is not associated with a FanVerse acount. Please re-enter the username correctly."
                )
                return redirect('post_settings', blog_id=blog.id)

            # prevent transferring to oneself
            if target_identifier == request.user.username or target_identifier == request.user.email:
                messages.error(request, "You cannot transfer a post to yourself.")
                return redirect('post_settings', blog_id=blog.id)
            
            # create/save a new TransferRequest in the database
            TransferRequest.objects.create(
                # attach the current blog
                blog=blog,
                # set the logged-in user as requester and save the requested target username
                requester=request.user,
                target_user_identifier=target_identifier
            )
            # show the success message to the user
            messages.success(request, "Request has been submitted successfully. You will receive a response in approximately 48 hours.")
        else:
            # show an error message if the input field was blank
            messages.error(request, "Please enter a valid username.")

    return redirect('post_settings', blog_id=blog.id)
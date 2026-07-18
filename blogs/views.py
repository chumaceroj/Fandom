from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog, Comment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


# Create your views here.

def index(request):
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
    if blog.is_orphaned or blog.author != request.user:
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
    return render(request, 'blogs/edit.html', {'blog': blog})

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
            
def add_comment(request, blog_id):
    # if the user just submitted a post request
    if request.method == 'POST':
        # get the specific blog post using its ID/return a 404 page if it doesn't exist
        blog = get_object_or_404(Blog, id=blog_id)
        # if the user is logged in, grab the content they submitted on the form
        if request.user.is_authenticated:
            content = request.POST.get('content')
        
        #create a new comment and save it to the database
        Comment.objects.create(
            #link it to the blog object
            blog = blog,
            author = request.user,
            # save the text the user submitted
            content = content
        )
    # redirect browser to the blog page & show the new comment
    return redirect('blog_detail', blog_id=blog_id)

def anonymize_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        
        if comment.author == request.user:
            if comment.is_anonymous:
                comment.deanonymize()
            else:
                comment.anonymize()
        
        return redirect('blog_detail', blog_id=comment.blog.id)
    return redirect('index')

        
def orphan_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        
        if comment.author == request.user:
            comment.orphan()

        return redirect('blog_detail', blog_id=comment.blog.id)
    return redirect('index')

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
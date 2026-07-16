from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog, Comment


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
    return render(request, 'blogs/detail.html', {'blog': blog })
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
            
def add_comment(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)
        content = request.POST.get('content')
        
        Comment.objects.create(
            blog=blog,
            author=request.user if request.user.is_authenticated else None,
            content=content
        )
    return redirect('blog_detail', blog_id=blog_id)

        

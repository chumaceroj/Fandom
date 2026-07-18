from django.urls import path

from . import views

# List of URL routes for Blog pages ("url_pattern", function, nickname_for_route)
urlpatterns = [
    # shows all blogs
    path("", views.index, name="index"),
    # /blogs/3/ → shows blog with id=3
    # <int:blog_id> captures the number from the URL and passes it to the view
    path('<int:blog_id>/', views.blog_detail, name='blog_detail'),
    # /blogs/3/edit/ → edit form for blog with id=3
    path('<int:blog_id>/edit/', views.edit_blog, name='edit_blog'),
    # /blogs/3/orphan/ → orphan blog with id=3
    path('<int:blog_id>/orphan/', views.orphan_blog, name='orphan_blog'),
    path('<int:blog_id>/anonymize/', views.anonymize_blog, name='anonymize_blog'),
    path('<int:blog_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:blog_id>/transfer/', views.transfer_blog, name='transfer_blog'),
    path('comment/<int:comment_id>/anonymize/', views.anonymize_comment, name='anonymize_comment'),
    path('comment/<int:comment_id>/orphan/', views.orphan_comment, name='orphan_comment'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
]
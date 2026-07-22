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
    path('create/', views.create_blog, name='create_blog'),
    # /blogs/3/orphan/ → orphan blog with id=3
    path('<int:blog_id>/orphan/', views.orphan_blog, name='orphan_blog'),
    path('<int:blog_id>/anonymize/', views.anonymize_blog, name='anonymize_blog'),
    path('<int:blog_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:blog_id>/transfer/', views.transfer_blog, name='transfer_blog'),
    path('comment/<int:comment_id>/anonymize/', views.anonymize_comment, name='anonymize_comment'),
    path('comment/<int:comment_id>/orphan/', views.orphan_comment, name='orphan_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('change-username/', views.change_username, name='change_username'),
    path('<int:blog_id>/settings/', views.post_settings, name='post_settings'),
    path('<int:blog_id>/invite/', views.invite_collaborator, name='invite_collaborator'),
    path('<int:blog_id>/remove-collaborator/<int:collaboration_id>/', views.remove_collaborator, name='remove_collaborator'),
    path('<int:blog_id>/leave/', views.leave_collaboration, name='leave_collaboration'),
    path('<int:blog_id>/reassign/', views.reassign_owner, name='reassign_owner'),
    path('invitation/<int:invitation_id>/accept/', views.accept_invitation, name='accept_invitation'),
    path('invitation/<int:invitation_id>/decline/', views.decline_invitation, name='decline_invitation'),
    path('notifications/', views.notifications, name='notifications'),
    path('blog/<int:blog_id>/request-transfer/', views.request_admin_transfer, name='request_admin_transfer'),
]
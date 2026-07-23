from django.contrib import admin
# Importing Blog & Comment models
from .models import Blog, Comment, Profile, TransferRequest

# Registers models
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Profile)

# admin class to handle the transfer requests
@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    # what to display in the admin list view
    list_display = ('blog', 'requester', 'target_user_identifier', 'status', 'created_at')
    # filtering options in the right sidebar
    list_filter = ('status', 'created_at')
    # allows search across these fields
    search_fields = ('blog__title', 'requester__username', 'target_user_identifier')
    # admin actions for approval/denial
    actions = ['approve_transfer', 'deny_transfer']

    # approving selected transfer requests
    @admin.action(description='Approve selected transfer requests')
    def approve_transfer(self, request, queryset):
        # loop through each request
        for transfer in queryset:
            # only process requests that are pending
            if transfer.status == 'PENDING':
                # find a user matching the requested username
                from django.contrib.auth.models import User
                # search by username
                new_owner = User.objects.filter(username=transfer.target_user_identifier).first() or \
                            User.objects.filter(email=transfer.target_user_identifier).first()
                # if the user (to be transferred to) exists
                if new_owner:
                    # user transfer method in model to handle ownership
                    transfer.blog.transfer(new_owner)
                    # make the request status approved
                    transfer.status = 'APPROVED'
                    # save the transfer request record
                    transfer.save()

    # denying selected transfer requests
    @admin.action(description='Deny selected transfer requests')
    def deny_transfer(self, request, queryset):
        # update the status of all selected requests to Denied
        queryset.update(status='DENIED')
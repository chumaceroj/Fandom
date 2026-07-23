from .models import Invitation, TransferRequest
# importing logical operators (or, and, not)
from django.db.models import Q

def notification_count(request):
    if request.user.is_authenticated:
        # count pending collab invitations
        count = Invitation.objects.filter(
            invited_user=request.user,
            status='pending'
        ).count()

        # grab all transfer requests that the logged-in user hasn't dismissed
        transfer_count = TransferRequest.objects.filter(
            (Q(requester=request.user, requester_notified=False) |
             Q(target_user_identifier=request.user.username, target_notified=False)),
            status__in=['APPROVED', 'DENIED']
        ).count()

        # return total unread notifications count
        return {'notification_count': count + transfer_count}
    return {'notification_count': 0}
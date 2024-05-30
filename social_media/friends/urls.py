from django.urls import path, include
from .views import UserRegistrationView, UserLoginView, UserLogoutView, FriendRequestSentView, FriendRequestRejectView, PendingFriendRequestListView, FriendRequestAcceptedView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('sent/', FriendRequestSentView.as_view(), name='request-sent'),
    path('reject/', FriendRequestRejectView.as_view(), name='request-reject'),
    path('accepted/', FriendRequestAcceptedView.as_view(), name='request-accepted'),
    path('pending_requests/', PendingFriendRequestListView.as_view(), name='request-pending'),
]

from django.urls import path, include
from .views import (UserRegistrationView, UserLoginView, UserLogoutView, FriendRequestListView, FriendRequestDetailView, SearchUserView)
                    # FriendRequestSentView, FriendRequestRejectView, PendingFriendRequestListView, FriendRequestAcceptedView)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('sent/', FriendRequestListView.as_view(), name='request-sent'),
    path('reject/', FriendRequestDetailView.as_view(), name='request-reject'),
    path('accepted/', FriendRequestDetailView.as_view(), name='request-accepted'),
    path('pending_requests/', FriendRequestListView.as_view(), name='request-pending'),
    path('search/', SearchUserView.as_view(), name='request-search'),
]

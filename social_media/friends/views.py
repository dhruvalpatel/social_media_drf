from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, FriendRequestSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from .models import User, FriendRequest, StatusType


class UserRegistrationView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs) -> Response:
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            if created:
                token.delete()  # Delete the token if it was already created
                token = Token.objects.create(user=user)
            return Response({'token': token.key, 'email': user.email})
        else:
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.headers)
        token_key = request.auth.key
        token = Token.objects.get(key=token_key)
        token.delete()
        return Response({'detail': 'Successfully logged out.'})


class FriendRequestListView(APIView):
    """FriendRequest List or create View"""
    throttle_scope = 'sent'
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """FriendRequest List or create View"""
        target_user = User.objects.get(email=request.data.get('target_user'))
        data = {}
        data['from_user'] = request.user.pk
        data['to_user'] = target_user.pk
        data['status'] = StatusType.PENDING
        serializer = FriendRequestSerializer(data=data)
        if FriendRequest.objects.filter(**data).exists():
            return Response('Friend request was already sent', status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request) -> Response:
        """FriendRequest List View"""
        friend_requests = FriendRequest.objects.filter(to_user=request.user.pk, status=StatusType.PENDING)
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return Response(serializer.data)


class FriendRequestDetailView(APIView):
    """FriendRequest Detail View"""
    permission_classes = [IsAuthenticated]

    def get_object(self, from_user: "User", to_user: "User", status: StatusType) -> FriendRequest:
        try:
            return FriendRequest.objects.get(from_user=from_user, to_user=to_user, status=status)
        except FriendRequest.DoesNotExist:
            raise Http404

    def put(self, request):
        """FriendRequest accept or reject View"""
        from_user = User.objects.get(email=request.data.get('from_user'))
        friend_request = self.get_object(from_user=from_user, to_user=request.user.pk, status=StatusType.PENDING)
        data = dict()
        data["from_user"] = from_user.pk
        data["to_user"] = request.user.pk
        if request.data.get("accept", False):
            data['status'] = StatusType.ACCEPTED
        else:
            data['status'] = StatusType.REJECTED
        serializer = FriendRequestSerializer(friend_request, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchUserView(APIView):
    """Search User view"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.filter(email__exact=request.data.get('email'))
        if users:
            serializer = UserSerializer(users.first())
        else:
            users = User.objects.filter(email__contains=request.data.get('email'))
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

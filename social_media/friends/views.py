from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, FriendRequestSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .models import User, FriendRequest, StatusType

class UserRegistrationView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
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


class FriendRequestSentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        to_user = User.objects.get(email=request.data.get('to_user'))
        data['from_user'] = request.user.pk
        data['to_user'] = to_user.pk
        data['status'] = StatusType.PENDING
        serializer = FriendRequestSerializer(data=data)

        if FriendRequest.objects.filter(**data).exists():
            raise serializer.ValidationError('This friend request is already sent.')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class FriendRequestRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        from_user = User.objects.get(email=request.data.get('from_user'))
        data['to_user'] = request.user.pk
        data['from_user'] = from_user.pk
        if FriendRequest.objects.filter(status=StatusType.REJECTED, **data).exists():
            return Response('This friend request is already rejected.')
        else:
            friend_request = FriendRequest.objects.filter(to_user=request.user.pk,
                                                from_user=request.data.get('from_user'),
                                                status=StatusType.PENDING).first()
            if friend_request:
                friend_request.status = StatusType.REJECTED
                friend_request.is_deleted = True
                friend_request.save()
                data['status'] = StatusType.REJECTED
                return Response(data, status=status.HTTP_201_CREATED)
            return Response("nOT PRESENT", status=status.HTTP_400_BAD_REQUEST)


class FriendRequestAcceptedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        from_user = User.objects.get(email=request.data.get('from_user'))
        data['to_user'] = request.user.pk
        data['from_user'] = from_user.pk
        import pdb; pdb.set_trace()
        if FriendRequest.objects.filter(status=StatusType.ACCEPTED, **data).exists():
            return Response('This friend request is already ACCEPTED.')
        else:
            friend_request = FriendRequest.objects.filter(to_user=request.user.pk,
                                                from_user=request.data.get('from_user'),
                                                status=StatusType.PENDING).first()
            if friend_request:
                friend_request.status = StatusType.ACCEPTED
                friend_request.is_deleted = True
                friend_request.save()
                request.user.friends.add(from_user)
                from_user.friends.add(request.user)
                data['status'] = StatusType.ACCEPTED
                return Response(data, status=status.HTTP_201_CREATED)
            return Response("Not Present", status=status.HTTP_400_BAD_REQUEST)


class PendingFriendRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        friend_requests = FriendRequest.objects.filter(to_user=request.user.pk, status=StatusType.PENDING)
        if friend_requests:
            serializer = FriendRequestSerializer(friend_requests, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)



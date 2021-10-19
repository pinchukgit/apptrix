from rest_framework import viewsets, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    UserSerializer,
    UserSerializerWithAvatar,
    UserAuthenticateSerializer,
    UserListSerializer
)
from .models import User
from .service import UserFilter
from rest_framework.permissions import IsAuthenticated, AllowAny


def send_email(user1, user2):
    template = "«Вы понравились {first_name}! Почта участника: {email}»"
    user1.email_user(
        message=template.format(first_name=user2.first_name,
                                email=user2.email),
        from_email=user2.email,
        subject="Apptrix"
    )
    user2.email_user(
        message=template.format(first_name=user1.first_name,
                                email=user1.email),
        from_email=user1.email,
        subject="Apptrix"
    )


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        if request.data.get('avatar'):
            serializer = UserSerializerWithAvatar(data=request.data)
        else:
            serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=201)
        else:
            return Response(status=400)


class UserAuthenticateViewSet(viewsets.views.APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserAuthenticateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserMatchViewSet(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):

        user = get_object_or_404(User, pk=pk)
        if request.user in user.likes.all():
            send_email(request.user, user)
        else:
            user.likes.add(request.user)
        return Response(status=status.HTTP_200_OK)


class UserListView(viewsets.ModelViewSet):

    serializer_class = UserListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    class Meta:
        model = User


from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.core.files import File
from .serializers import UserSerializer, UserSerializerWithAvatar
from .models import User


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        if request.data.get('avatar'):
            serializer = UserSerializerWithAvatar(data=request.data)
        else:
            serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        else:
            return Response(status=400)

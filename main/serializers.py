from rest_framework import serializers
from .models import User
import os
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from apptrix import settings
from io import BytesIO
from django.contrib.auth import authenticate


watermark_dir = os.path.join(settings.BASE_DIR, "watermark")
transparency = 50
watermark_size_percent = 80


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "password",
                  "likes", "latitude", "longitude", "avatar")
        extra_kwargs = {'password': {'write_only': True},
                        "likes": {"read_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserListSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField("get_distance",
                                                 read_only=True)

    class Meta:
        model = User
        fields = ("id",
                  "email",
                  "first_name",
                  "last_name",
                  "distance",
                  "watemark_avatar")

    def get_distance(self, owner):

        return owner.get_geo_distance(
            self.context['request'].user.latitude,
            self.context['request'].user.longitude)


class UserSerializerWithAvatar(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password", "avatar",
                 "watemark_avatar")
        extra_kwargs = {'password': {'write_only': True}, }

    def create(self, validated_data):
        img = Image.open(validated_data.get('avatar'))
        img_format = img.format
        img_mode = img.mode
        img_width, img_height = img.size
        img = img.convert("RGBA")
        watermark = Image.open(
            os.path.join(watermark_dir,"watermark.png")).convert("RGBA")
        watermark.thumbnail(
            size=(int(img_width * watermark_size_percent / 100),
                  int(img_height * watermark_size_percent / 100)))
        watermark_width, watermark_height = watermark.size
        paste_mask = watermark.split()[3].point(
            lambda i: i * transparency / 100.)
        tranparent = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        tranparent.paste(img, (0, 0))
        offset = ((img_width - watermark_width) // 2,
                  (img_height - watermark_height) // 2)
        tranparent.paste(watermark, offset, mask=paste_mask)
        tranparent = tranparent.convert(img_mode)
        buffer = BytesIO()
        tranparent.save(fp=buffer, format=img_format.lower())
        validated_data['watemark_avatar'] = InMemoryUploadedFile(
            buffer,
            None,
            validated_data['avatar'].name,
            img_format.lower(),
            img.tell,
            None
        )
        return User.objects.create_user(**validated_data)


class UserAuthenticateSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        print(attrs)
        email = attrs.get('email', None)
        password = attrs.get("password", None)

        if not email:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )
        if not password:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=email,
                            password=password)

        if not user:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            "token": user.token
        }


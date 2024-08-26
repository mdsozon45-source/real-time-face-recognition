from rest_framework import serializers

from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'image', 'encoding']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # Create a new user profile with the provided data
        user_profile = UserProfile.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            image=validated_data.get('image', None),
            encoding=validated_data.get('encoding', None)
        )
        return user_profile

class FaceRecognitionInputSerializer(serializers.Serializer):
    image = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)

class FaceRecognitionOutputSerializer(serializers.Serializer):
    names = serializers.ListField(child=serializers.CharField())

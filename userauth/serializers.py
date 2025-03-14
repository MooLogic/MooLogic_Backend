from rest_framework import serializers

from django.contrib.auth.models import User, Farm


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ('id', 'username', 'email', 'password')


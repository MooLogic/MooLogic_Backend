from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'full_name', 'phone_number', 
            'profile_picture', 'role', 'worker_role', 'farm',
            'get_email_notification', 'get_push_notification', 
            'get_sms_notification', 'oversite_access', 'language'
        )
        read_only_fields = ('id', 'date_joined', 'last_login')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


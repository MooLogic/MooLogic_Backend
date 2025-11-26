from rest_framework import serializers
from .models import User
import random
import re


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'full_name', 'phone_number', 
            'profile_picture', 'role', 'worker_role', 'farm', 'bio',
            'get_email_notifications', 'get_push_notifications', 
            'get_sms_notifications', 'oversite_access', 'language',
            'email_verified'
        )
        read_only_fields = ('id', 'date_joined', 'last_login', 'email_verified')

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


class SignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        phone = attrs.get("phone_number")

        # Require at least ONE of them
        if not email and not phone:
            raise serializers.ValidationError("Either email or phone number is required.")

        # Uniqueness checks
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists.")
        if phone and User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError("Phone number already exists.")

        return attrs

    def generate_username(self, full_name):
        base = re.sub(r"[^a-zA-Z]", "", full_name.replace(" ", "").lower())
        suffix = random.randint(100, 999)
        return f"{base}_{suffix}"

    def create(self, validated_data):
        full_name = validated_data["full_name"]
        password = validated_data["password"]

        username = self.generate_username(full_name)

        user = User.objects.create_user(
            email=validated_data.get("email"),
            phone_number=validated_data.get("phone_number"),
            username=username,
            full_name=full_name,
            password=password,
        )

        return user
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.contrib.auth import update_session_auth_hash

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from .serializers import UserSerializer
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter



@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    User signup view with JWT authentication.
    """
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')

    if not email or not username or not password:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(email=email, username=username, password=password)

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        'message': 'User registered successfully',
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
        },
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }, status=status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    User login view with JWT authentication.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(email=email, password=password)

    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
        },
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # Generate password reset token
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    reset_url = f"http://localhost:3000/reset-password/{uidb64}/{token}"  # Change frontend URL

    # Send email
    send_mail(
        'Password Reset Request',
        f'Click the link to reset your password: {reset_url}',
        'no-reply@example.com',
        [email],
        fail_silently=False,
    )

    return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    uidb64 = request.data.get('uidb64')
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    if not uidb64 or not token or not new_password:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    # Reset password
    user.set_password(new_password)
    user.save()

    return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    """
    Edit user profile.
    """
    user = request.user  # Get the authenticated user

    # Get the updated fields from request data
    name = request.data.get('name', user.name)  # Default to existing value if not provided
    username = request.data.get('username', user.username)
    email = request.data.get('email', user.email)
    role = request.data.get('role', user.role)
    language = request.data.get('language', user.language)

    # Check if the new email or username is already taken
    if User.objects.exclude(id=user.id).filter(email=email).exists():
        return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.exclude(id=user.id).filter(username=username).exists():
        return Response({'error': 'Username already in use'}, status=status.HTTP_400_BAD_REQUEST)

    # Update the user's profile
    user.name = name
    user.username = username
    user.email = email
    user.role = role
    user.language = language
    user.save()

    return Response({
        'message': 'Profile updated successfully',
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'name': user.name,
            'role': user.role,
            'language': user.language,
        }
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password.
    """
    user = request.user  # Get the authenticated user

    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response({'error': 'Both old and new passwords are required'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)  # Update the password securely
    user.save()

    # Keep the user logged in after password change
    update_session_auth_hash(request, user)

    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout user and blacklist the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh_token')

        if refresh_token:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()  # Blacklist the token

        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh access token using refresh token.
    """
    refresh_token = request.data.get('refresh_token')

    if not refresh_token:
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)

        return Response({'access_token': new_access_token}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])  # Change to PUT
@permission_classes([IsAuthenticated])
def update_user_role(request):
    """
    Update the role of a user.
    Only admin or authorized users should be able to update another user's role.
    """
    user_id = request.data.get('user_id')
    new_role = request.data.get('role')

    if not user_id or not new_role:
        return Response({'error': 'User ID and new role are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate the role value
    valid_roles = dict(User.ROLE_CHOICES)
    if new_role not in valid_roles:
        return Response({'error': 'Invalid role provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the current user has permission to update the role
    if not request.user.is_superuser:  # Only allow superusers to change roles for others
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    # Update the role of the user
    user.role = new_role
    user.save()

    # Optionally, serialize the updated user data to return a response
    user_data = UserSerializer(user).data

    return Response({
        'message': 'User role updated successfully',
        'user': user_data
    }, status=status.HTTP_200_OK)

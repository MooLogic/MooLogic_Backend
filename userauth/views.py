from django.contrib.auth import authenticate
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.conf import settings

from core.models import Farm
from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.core.files.storage import default_storage
import os

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
import uuid

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
    User login view with JWT authentication using email.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=email, password=password)  # Authenticate with email

    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'full_name': user.full_name,
            'farm': user.farm.name if user.farm else None,
            'role': user.role,
            'language': user.language,
            'worker_role': user.worker_role,
        },
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }, status=status.HTTP_200_OK)


#get user by id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, user_id):
    """
    Get user by ID.
    """
    try:
        user = User.objects.get(id=user_id)
        return Response({
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'full_name': user.full_name,
            'phone_number': user.phone_number,
            'farm': user.farm.farm_code if user.farm else None,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'role': user.role,
            'language': user.language,
            'worker_role': user.worker_role,
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_farm_users(request):
    """
    Get all users in the farm.
    """
    users = User.objects.filter(farm=request.user.farm)
    serializer = UserSerializer(users, many=True)
    print(serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Request password reset email."""
    email = request.data.get('email')
    if not email:
        return Response({
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'No user found with this email'
        }, status=status.HTTP_404_NOT_FOUND)

    # Generate reset token
    token = user.generate_password_reset_token()
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{user.id}/{token}"

    try:
        send_mail(
            'Reset your password',
            f'Click this link to reset your password: {reset_url}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response({
            'message': 'Password reset email sent'
        })
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return Response({
            'error': 'Failed to send password reset email'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password with token."""
    user_id = request.data.get('user_id')
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    if not all([user_id, token, new_password]):
        return Response({
            'error': 'All fields are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid user'
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if token is valid and not expired (24 hours)
    if (user.password_reset_token != token or
        user.password_reset_sent_at + timedelta(hours=24) < timezone.now()):
        return Response({
            'error': 'Invalid or expired reset token'
        }, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.password_reset_token = None
    user.password_reset_sent_at = None
    user.save()

    return Response({
        'message': 'Password reset successfully'
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    """
    Edit user profile.
    """
    user = request.user  # Get the authenticated user

    # Get the updated fields from request data
    full_name = request.data.get('name', user.name)  # Default to existing value if not provided
    username = request.data.get('username', user.username)
    email = request.data.get('email', user.email)
    role = request.data.get('role', user.role)
    language = request.data.get('language', user.language)
    phone_number = request.data.get('phone_number', user.phone_number)
    profile_picture = request.data.get('profile_picture', user.profile_picture)
    worker_role = request.data.get('worker_role', user.worker_role)
    get_email_notification = request.data.get('get_email_notification', user.get_email_notification)
    get_push_notification = request.data.get('get_push_notification', user.get_push_notification)
    get_sms_notification = request.data.get('get_sms_notification', user.get_sms_notification)

    # Check if the new email or username is already taken
    if User.objects.exclude(id=user.id).filter(email=email).exists():
        return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.exclude(id=user.id).filter(username=username).exists():
        return Response({'error': 'Username already in use'}, status=status.HTTP_400_BAD_REQUEST)

    # Update the user's profile
    user.name = full_name
    user.username = username
    user.email = email
    user.role = role
    user.language = language
    user.phone_number = phone_number
    user.profile_picture = profile_picture
    user.worker_role = worker_role
    user.get_email_notification = get_email_notification
    user.get_push_notification = get_push_notification
    user.get_sms_notification = get_sms_notification
    
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
            'phone_number': user.phone_number,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'worker_role': user.worker_role,
            'get_email_notification': user.get_email_notification,
            'get_push_notification': user.get_push_notification,
            'get_sms_notification': user.get_sms_notification,

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

from rest_framework_simplejwt.exceptions import TokenError

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

    except TokenError as e:
        return Response({'error': f'Invalid or expired refresh token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])  
@permission_classes([IsAuthenticated])
def update_user_role(request):
    """
    Update user role.
    """
    user_id = request.data.get('user_id')
    new_role = request.data.get('role')

    if not new_role:
        return Response({'error': 'Role is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if new_role == 'worker' or new_role == 'government':
        
        try:
            user = User.objects.get(id=user_id)
            user.role = new_role
            user.is_active = False  
            user.save()
            return Response({'message': 'User role updated successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            user = User.objects.get(id=user_id)
            user.role = new_role 
            user.save()
            return Response({'message': 'User role updated successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


#function to add aworker to farm
@api_view(['POST'])
@permission_classes([AllowAny])
def update_worker_farm(request):
    """
    Update a worker's farm and role.
    """
    user_id = request.data.get('user_id')
    farm_id = request.data.get('farm_code')
    worker_role = request.data.get('workerRole')
    print("user_di : " + str(user_id))
    print("farm_id : " + str(farm_id))
    print("worker_role : " + str(worker_role))
    if not user_id or not farm_id or not worker_role:
        return Response({'error': 'user_id, farm_code, and workerRole are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
        farm = Farm.objects.get(farm_code=farm_id)  # Assuming `id` is used; use `code=farm_id` if farm_code is a custom field

        user.farm = farm
        user.worker_role = worker_role
        user.is_active = True  # Activate the worker once assigned
        print(user)
        print(farm)
        user.save()

        return Response({'message': 'Worker assigned to farm successfully'}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    except Farm.DoesNotExist:
        return Response({'error': 'Farm not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_email_verification(request):
    """Check if user's email is verified."""
    return Response({
        'is_verified': request.user.email_verified
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_verification_email(request):
    """Send email verification link."""
    user = request.user
    if user.email_verified:
        return Response({
            'message': 'Email is already verified'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Generate new verification token
    token = user.generate_email_verification_token()
    
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{user.id}/{token}"
    
    # HTML email template
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Verify Your Email Address</h2>
                <p>Hello {user.full_name or user.username},</p>
                <p>Thank you for registering with Loonko. To complete your registration and access all features, please verify your email address by clicking the button below:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email Address</a>
                </p>
                <p>Or copy and paste this link in your browser:</p>
                <p style="background-color: #f3f4f6; padding: 10px; border-radius: 5px;">{verification_url}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you did not create an account with MooLogic, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 0.875rem;">This is an automated message, please do not reply to this email.</p>
            </div>
        </body>
    </html>
    """
    
    # Plain text version for email clients that don't support HTML
    plain_message = f"""
    Hello {user.full_name or user.username},

    Thank you for registering with MooLogic. To verify your email address, please click the following link:

    {verification_url}

    This link will expire in 24 hours.

    If you did not create an account with MooLogic, please ignore this email.
    """
    
    try:
        send_mail(
            subject='Verify your MooLogic email address',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return Response({
            'message': 'Verification email sent successfully'
        })
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return Response({
            'error': 'Failed to send verification email'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verify email with token."""
    user_id = request.data.get('user_id')
    token = request.data.get('token')

    print(f"Verifying email for user_id: {user_id}, token: {token}")

    try:
        user = User.objects.get(id=user_id)
        print(f"Found user: {user.email}")
        print(f"User verification token: {user.email_verification_token}")
        print(f"Token sent at: {user.email_verification_sent_at}")
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid user'
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if token is valid and not expired (24 hours)
    if (str(user.email_verification_token) != token or
        user.email_verification_sent_at + timedelta(hours=24) < timezone.now()):
        print(f"Token validation failed:")
        print(f"Stored token: {user.email_verification_token}")
        print(f"Received token: {token}")
        print(f"Token sent at: {user.email_verification_sent_at}")
        print(f"Current time: {timezone.now()}")
        return Response({
            'error': 'Invalid or expired verification token'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Mark email as verified and generate a new token
    user.email_verified = True
    user.email_verification_token = uuid.uuid4()  # Generate new token instead of setting to None
    user.email_verification_sent_at = None  # Reset sent time
    user.save()

    return Response({
        'message': 'Email verified successfully'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile_picture(request):
    """Update user's profile picture."""
    if 'profile_picture' not in request.FILES:
        return Response({
            'error': 'No image file provided'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    
    # Delete old profile picture if it exists
    if user.profile_picture:
        try:
            default_storage.delete(user.profile_picture.path)
        except:
            pass

    # Save new profile picture
    file = request.FILES['profile_picture']
    filename = default_storage.save(f'profile_pictures/{user.id}_{file.name}', file)
    user.profile_picture = filename
    user.save()

    return Response({
        'message': 'Profile picture updated successfully',
        'profile_picture_url': request.build_absolute_uri(user.profile_picture.url)
    })

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile information."""
    user = request.user
    data = request.data

    # Update basic information
    if 'name' in data:
        user.full_name = data['name']
    if 'username' in data:
        if User.objects.exclude(id=user.id).filter(username=data['username']).exists():
            return Response({
                'error': 'Username already taken'
            }, status=status.HTTP_400_BAD_REQUEST)
        user.username = data['username']
    if 'email' in data and data['email'] != user.email:
        if User.objects.exclude(id=user.id).filter(email=data['email']).exists():
            return Response({
                'error': 'Email already taken'
            }, status=status.HTTP_400_BAD_REQUEST)
        user.email = data['email']
        user.email_verified = False  # Require re-verification for new email
    if 'phone_number' in data:
        user.phone_number = data['phone_number']
    if 'bio' in data:
        user.bio = data['bio']
    if 'language' in data:
        user.language = data['language']

    # Update notification preferences
    if 'get_email_notifications' in data:
        user.get_email_notifications = data['get_email_notifications']
    if 'get_push_notifications' in data:
        user.get_push_notifications = data['get_push_notifications']
    if 'get_sms_notifications' in data:
        user.get_sms_notifications = data['get_sms_notifications']

    # Update worker role if applicable
    if user.role == 'worker' and 'worker_role' in data:
        user.worker_role = data['worker_role']

    user.save()

    return Response({
        'message': 'Profile updated successfully',
        'user': UserSerializer(user).data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Get the current authenticated user's profile data
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)



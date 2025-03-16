from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
    def test_signup(self):
        response = self.client.post('/api/signup/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_login(self):
        response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_request_password_reset(self):
        response = self.client.post('/api/password-reset/', {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_reset_password(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.post('/api/password-reset-confirm/', {
            'uidb64': uidb64,
            'token': token,
            'new_password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_edit_profile(self):
        response = self.client.put('/api/edit-profile/', {
            'username': 'updateduser',
            'email': 'updated@example.com'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_change_password(self):
        response = self.client.put('/api/change-password/', {
            'old_password': 'password123',
            'new_password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout(self):
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

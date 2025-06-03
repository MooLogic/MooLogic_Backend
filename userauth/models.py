from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255, blank=True, default='')
    phone_number = models.CharField(max_length=15, blank=True, default='')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')

    # Email verification fields
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(null=True, blank=True, default=uuid.uuid4)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    # Password reset fields
    password_reset_token = models.UUIDField(null=True, blank=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)

    ROLE_CHOICES = (
        ('owner', 'Farm Owner'),
        ('government', 'Government'),
        ('worker', 'Dairy Worker'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)

    WORKER_ROLE_CHOICES = (
        ('veterinary', 'Veterinary'),
        ('milktracker', 'Milk production tracker'),
        ('manager', 'Farm Manager'),
        ('finance', 'Finance'),
        ('generalpurpose', 'General Purpose'),
    )

    worker_role = models.CharField(max_length=20, choices=WORKER_ROLE_CHOICES, default='generalpurpose',
                                   blank=True, null=True)
    farm = models.ForeignKey('core.Farm', on_delete=models.CASCADE, null=True, blank=True)

    # Notification preferences
    get_email_notifications = models.BooleanField(default=True)
    get_push_notifications = models.BooleanField(default=False)
    get_sms_notifications = models.BooleanField(default=False)

    oversite_access = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('am', 'Amharic'),
        ('or', 'Oromiffa'),
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def generate_email_verification_token(self):
        self.email_verification_token = uuid.uuid4()
        self.email_verification_sent_at = timezone.now()
        self.save()
        return self.email_verification_token

    def generate_password_reset_token(self):
        self.password_reset_token = uuid.uuid4()
        self.password_reset_sent_at = timezone.now()
        self.save()
        return self.password_reset_token
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from core.models import Farm



class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, username, **extra_fields):
        if not email:
            raise ValueError("You must provide an email address")
        if not username:
            raise ValueError("You must provide a username")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user  

    def create_user(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)  # Ensure users are active by default
        return self._create_user(email, password, username, **extra_fields)

    def create_superuser(self, email, password, username, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # Superusers must be active
        return self._create_user(email, password, username, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255, blank=True, default='')

    phone_number = models.CharField(max_length=15, blank=True, default='')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    ROLE_CHOICES = (
        ('owner', 'Famr Owner'),
        ('manager', 'Farm Manager'),
        ('worker','Dairy Worker'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)

    WORKER_ROLE_CHOICES = (
        ('vaterinary', 'Veterinary'),
        ('milktracker', 'Milk production tracker'),
        ('manager', 'Farm Manager'),
        ('finance', 'Finance'),
        ('generalpurpose', 'General Purpose'),
    )

    worker_role = models.CharField(max_length=20, choices=WORKER_ROLE_CHOICES, default='generalpurpose', blank=True, null=True)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, null=True, blank=True)

    get_email_notification = models.BooleanField(default=True)
    get_push_notification = models.BooleanField(default=False)
    get_sms_notification = models.BooleanField(default=False)

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

    def get_full_name(self):
        return self.name or self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.email

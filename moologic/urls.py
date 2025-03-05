# Description: This file is the main URL configuration for the project. It includes the URL configuration for the admin site, the userauth app, the finance_tracker app, the core app, the milk_tracker app, and the health_manager app.
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path("auth/", include("userauth.urls")),
    path('api/financial/', include('finance_tracker.urls')),
    path("core/", include("core.urls")),
    path('milk/', include('milk_tracker.urls')),
    path('health/', include('health_manager.urls')),
    # path('health/', include('health_manager.urls'))

]

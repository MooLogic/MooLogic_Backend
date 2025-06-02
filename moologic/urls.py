# Description: This file is the main URL configuration for the project. It includes the URL configuration for the admin site, the userauth app, the finance_tracker app, the core app, the milk_tracker app, and the health_manager app.
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("auth/", include("userauth.urls")),
    path('financial/', include('finance_tracker.urls')),
    path("core/", include("core.urls")),
    path('milk/', include('milk_tracker.urls')),
    path('health/', include('health_manager.urls')),
    # path('health/', include('health_manager.urls'))
    path('api/predictor/', include('predictor.urls', namespace='predictor')),
    path('api/prompt_prediction/',include('prompt_prediction.urls',namespace='prompt_prediction')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

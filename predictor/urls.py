from django.urls import path
from .views import ImagePredictionView

app_name = 'predictor'

urlpatterns = [
    path('', ImagePredictionView.as_view(), name='image_prediction'),
]
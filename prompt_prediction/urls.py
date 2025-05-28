from django.urls import path
from .views import DiseaseDetectionView

app_name = 'prompt_prediction'

urlpatterns = [
    path('', DiseaseDetectionView.as_view(), name='symptom_prediction'),
]
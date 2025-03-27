from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CattleViewSet, InseminationViewSet, BirthRecordViewSet, AlertViewSet, create_farm

router = DefaultRouter()
router.register(r'cattle', CattleViewSet)
router.register(r'insemination', InseminationViewSet)
router.register(r'birth-record', BirthRecordViewSet)
router.register(r'alerts', AlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('farm/', create_farm, name='farm'),
]
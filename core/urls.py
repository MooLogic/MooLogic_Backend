from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CattleViewSet, InseminationViewSet, BirthRecordViewSet, AlertViewSet, create_farm, delete_farm, update_farm, get_farms, get_farm

router = DefaultRouter()
router.register(r'cattle', CattleViewSet)
router.register(r'insemination', InseminationViewSet)
router.register(r'birth-record', BirthRecordViewSet)
router.register(r'alerts', AlertViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('create-farm/', create_farm, name='create-farm'),
    path('delete-farm/<int:farm_id>/', delete_farm, name='delete-farm'),
    path('update-farm/<int:farm_id>/', update_farm, name='update-farm'),
    path('get-farms/', get_farms, name='get-farms'),
    path('get-farm/<int:farm_id>/', get_farm, name='get-farm'),

]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinancialRecordViewSet, ProfitSnapshotViewSet

router = DefaultRouter()
router.register(r'records', FinancialRecordViewSet, basename='financial-record')
router.register(r'profit-snapshots', ProfitSnapshotViewSet, basename='profit-snapshot')

urlpatterns = [
    path('', include(router.urls)),
]
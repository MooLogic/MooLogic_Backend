from django.urls import path
from . import views 

urlpatterns = [
    path('addcattle/', views.create_cattle, name='create_cattle'),
    path('getallcattle/', views.get_all_cattle, name='get_all_cattle'),
    path('getcattlebyid/<int:cattle_id>/', views.get_cattle_by_id, name='get_cattle_by_id'),
    path('updatecattle/<int:cattle_id>/', views.update_cattle_by_id, name='update_cattle'),
    path('deletecattle/<int:cattle_id>/', views.delete_cattle_by_id, name='delete_cattle'),
]
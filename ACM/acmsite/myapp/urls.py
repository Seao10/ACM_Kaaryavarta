from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stock/', views.stocks, name='stocks'),
    path('mf/', views.mutual_funds, name='mf'),
    path('nv/', views.new_view, name='nv')
]

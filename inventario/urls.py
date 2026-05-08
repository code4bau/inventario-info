from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('activos/', views.ItemListView.as_view(), name='item_list'),
    path('movimiento/nuevo/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('reporte/', views.generate_report, name='generate_report'),
]

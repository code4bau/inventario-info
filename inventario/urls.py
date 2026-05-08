from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('activos/', views.ItemListView.as_view(), name='item_list'),
    path('movimiento/nuevo/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('movimiento/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('movimiento/<int:pk>/eliminar/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path('reporte/', views.generate_report, name='generate_report'),
]

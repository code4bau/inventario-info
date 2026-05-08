from django.urls import path
from . import views

urlpatterns = [
    path('', views.IPListView.as_view(), name='ip_list'),
    path('nueva/', views.IPCreateView.as_view(), name='ip_create'),
    path('<int:pk>/editar/', views.IPUpdateView.as_view(), name='ip_update'),
    path('<int:pk>/eliminar/', views.IPDeleteView.as_view(), name='ip_delete'),
    path('<int:pk>/ping/', views.toggle_ip_status, name='ip_ping'),
]

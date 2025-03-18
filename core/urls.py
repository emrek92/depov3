from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Ürün Yönetimi
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Kategori Yönetimi
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Birim Yönetimi
    path('units/', views.unit_list, name='unit_list'),
    path('units/create/', views.unit_create, name='unit_create'),
    path('units/<int:pk>/edit/', views.unit_edit, name='unit_edit'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),
    
    # Tedarikçi Yönetimi
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # Warehouse Management URLs
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/create/', views.warehouse_create, name='warehouse_create'),
    path('warehouses/<int:pk>/edit/', views.warehouse_edit, name='warehouse_edit'),
    path('warehouses/<int:pk>/delete/', views.warehouse_delete, name='warehouse_delete'),
    
    # Stok Hareketleri
    path('stock-movements/', views.stock_movement_list, name='stock_movement_list'),
    path('stock-movements/in/', views.stock_in_create, name='stock_in_create'),
    path('stock-movements/out/', views.stock_out_create, name='stock_out_create'),
    path('stock-movements/transfer/', views.stock_transfer_create, name='stock_transfer_create'),
    
    # Raporlar
    path('reports/', views.reports, name='reports'),
    path('reports/stock/', views.stock_report, name='stock_report'),
    path('reports/stock-value/', views.stock_value_report, name='stock_value_report'),
    path('reports/movement/', views.movement_report, name='movement_report'),
    
    # Kullanıcı Yönetimi
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/roles/', views.user_role_assignment, name='user_role_assignment'),
    
    # Rol Yönetimi
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:pk>/edit/', views.role_edit, name='role_edit'),
    path('roles/<int:pk>/delete/', views.role_delete, name='role_delete'),
    path('roles/<int:pk>/permissions/', views.role_permissions, name='role_permissions'),
    
    # İzin Yönetimi
    path('permissions/', views.permission_list, name='permission_list'),
    path('permissions/create/', views.permission_create, name='permission_create'),
    path('permissions/<int:pk>/edit/', views.permission_edit, name='permission_edit'),
    path('permissions/<int:pk>/delete/', views.permission_delete, name='permission_delete'),
] 
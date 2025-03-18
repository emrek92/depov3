from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import UserRole, RolePermission

def has_permission(permission_codename):
    """
    İstekte bulunan kullanıcının belirtilen izne sahip olup olmadığını kontrol eder.
    Eğer izin yoksa, kullanıcıyı dashboard'a yönlendirir ve bir hata mesajı gösterir.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Admin kullanıcısı ise her zaman erişim sağla
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Kullanıcının rollerini al
            user_roles = UserRole.objects.filter(user=request.user).select_related('role')
            
            # Kullanıcının rollerine bağlı izinleri kontrol et
            has_access = False
            for user_role in user_roles:
                if RolePermission.objects.filter(
                    role=user_role.role,
                    permission__codename=permission_codename
                ).exists():
                    has_access = True
                    break
            
            if has_access:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Bu işlemi yapmak için yetkiniz yok.')
                return redirect('dashboard')
        
        return _wrapped_view
    
    return decorator

def admin_required(view_func):
    """
    İstekte bulunan kullanıcının yönetici izinlerine sahip olup olmadığını kontrol eder.
    Yönetici izni, 'admin_access' permission_codename ile belirlenir.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Admin kullanıcısı ise her zaman erişim sağla
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Kullanıcının rollerini al
        user_roles = UserRole.objects.filter(user=request.user).select_related('role')
        
        # Kullanıcının admin_access izni var mı kontrol et
        has_admin_access = False
        for user_role in user_roles:
            if RolePermission.objects.filter(
                role=user_role.role,
                permission__codename='admin_access'
            ).exists():
                has_admin_access = True
                break
        
        if has_admin_access:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Bu işlemi yapmak için yönetici yetkisine sahip olmanız gerekiyor.')
            return redirect('dashboard')
    
    return _wrapped_view 
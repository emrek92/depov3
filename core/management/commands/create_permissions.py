from django.core.management.base import BaseCommand
from core.models import Permission

class Command(BaseCommand):
    help = 'Sistem izinlerini oluşturur'

    def handle(self, *args, **options):
        # Temel izinleri tanımla
        permissions = [
            # Yönetici izni
            ('admin_access', 'Yönetici Erişimi', 'Sistem yönetimi için tam erişim'),
            
            # Dashboard izinleri
            ('view_dashboard', 'Dashboard Görüntüleme', 'Dashboard sayfasını görüntüleme izni'),
            
            # Ürün izinleri
            ('view_products', 'Ürünleri Görüntüleme', 'Ürün listesini görüntüleme izni'),
            ('add_product', 'Ürün Ekleme', 'Yeni ürün ekleme izni'),
            ('edit_product', 'Ürün Düzenleme', 'Mevcut ürünleri düzenleme izni'),
            ('delete_product', 'Ürün Silme', 'Ürünleri silme izni'),
            
            # Kategori izinleri
            ('view_categories', 'Kategorileri Görüntüleme', 'Kategori listesini görüntüleme izni'),
            ('add_category', 'Kategori Ekleme', 'Yeni kategori ekleme izni'),
            ('edit_category', 'Kategori Düzenleme', 'Mevcut kategorileri düzenleme izni'),
            ('delete_category', 'Kategori Silme', 'Kategorileri silme izni'),
            
            # Birim izinleri
            ('view_units', 'Birimleri Görüntüleme', 'Birim listesini görüntüleme izni'),
            ('add_unit', 'Birim Ekleme', 'Yeni birim ekleme izni'),
            ('edit_unit', 'Birim Düzenleme', 'Mevcut birimleri düzenleme izni'),
            ('delete_unit', 'Birim Silme', 'Birimleri silme izni'),
            
            # Tedarikçi izinleri
            ('view_suppliers', 'Tedarikçileri Görüntüleme', 'Tedarikçi listesini görüntüleme izni'),
            ('add_supplier', 'Tedarikçi Ekleme', 'Yeni tedarikçi ekleme izni'),
            ('edit_supplier', 'Tedarikçi Düzenleme', 'Mevcut tedarikçileri düzenleme izni'),
            ('delete_supplier', 'Tedarikçi Silme', 'Tedarikçileri silme izni'),
            
            # Depo izinleri
            ('view_warehouses', 'Depoları Görüntüleme', 'Depo listesini görüntüleme izni'),
            ('add_warehouse', 'Depo Ekleme', 'Yeni depo ekleme izni'),
            ('edit_warehouse', 'Depo Düzenleme', 'Mevcut depoları düzenleme izni'),
            ('delete_warehouse', 'Depo Silme', 'Depoları silme izni'),
            
            # Stok hareket izinleri
            ('view_stock_movements', 'Stok Hareketlerini Görüntüleme', 'Stok hareketlerini görüntüleme izni'),
            ('add_stock_in', 'Stok Girişi', 'Stok girişi yapma izni'),
            ('add_stock_out', 'Stok Çıkışı', 'Stok çıkışı yapma izni'),
            ('add_stock_transfer', 'Stok Transferi', 'Depolar arası stok transferi yapma izni'),
            
            # Rapor izinleri
            ('view_reports', 'Raporları Görüntüleme', 'Raporları görüntüleme izni'),
            ('export_reports', 'Rapor Dışa Aktarma', 'Raporları Excel/PDF olarak dışa aktarma izni'),
            
            # Kullanıcı yönetimi izinleri
            ('view_users', 'Kullanıcıları Görüntüleme', 'Kullanıcı listesini görüntüleme izni'),
            ('add_user', 'Kullanıcı Ekleme', 'Yeni kullanıcı ekleme izni'),
            ('edit_user', 'Kullanıcı Düzenleme', 'Mevcut kullanıcıları düzenleme izni'),
            ('delete_user', 'Kullanıcı Silme', 'Kullanıcıları silme izni'),
            
            # Rol yönetimi izinleri
            ('view_roles', 'Rolleri Görüntüleme', 'Rol listesini görüntüleme izni'),
            ('add_role', 'Rol Ekleme', 'Yeni rol ekleme izni'),
            ('edit_role', 'Rol Düzenleme', 'Mevcut rolleri düzenleme izni'),
            ('delete_role', 'Rol Silme', 'Rolleri silme izni'),
            ('manage_permissions', 'İzinleri Yönetme', 'Rol izinlerini yönetme izni'),
        ]
        
        created_count = 0
        existing_count = 0
        
        for codename, name, description in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': name,
                    'description': description
                }
            )
            
            if created:
                created_count += 1
            else:
                existing_count += 1
                # İzin zaten var, bilgilerini güncelle
                permission.name = name
                permission.description = description
                permission.save()
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} yeni izin oluşturuldu. {existing_count} mevcut izin güncellendi.')) 
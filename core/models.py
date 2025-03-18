from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Kategori Adı')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'

    def __str__(self):
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=50, verbose_name='Birim Adı')
    symbol = models.CharField(max_length=10, verbose_name='Sembol')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Birim'
        verbose_name_plural = 'Birimler'

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name='Tedarikçi Adı')
    code = models.CharField(max_length=50, unique=True, verbose_name='Tedarikçi Kodu')
    contact_person = models.CharField(max_length=100, blank=True, verbose_name='İletişim Kişisi')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    email = models.EmailField(blank=True, verbose_name='E-posta')
    address = models.TextField(blank=True, verbose_name='Adres')
    tax_number = models.CharField(max_length=20, blank=True, verbose_name='Vergi Numarası')
    tax_office = models.CharField(max_length=100, blank=True, verbose_name='Vergi Dairesi')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tedarikçi'
        verbose_name_plural = 'Tedarikçiler'

    def __str__(self):
        return f"{self.name} ({self.code})"

class Warehouse(models.Model):
    name = models.CharField(max_length=100, verbose_name='Depo Adı')
    code = models.CharField(max_length=50, unique=True, verbose_name='Depo Kodu')
    location = models.CharField(max_length=200, verbose_name='Konum')
    address = models.TextField(blank=True, verbose_name='Adres')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Depo Sorumlusu')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Depo'
        verbose_name_plural = 'Depolar'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Ürün Adı')
    code = models.CharField(max_length=50, unique=True, verbose_name='Ürün Kodu')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Kategori')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name='Birim')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='Tedarikçi')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Depo')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Alış Fiyatı')
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Satış Fiyatı')
    min_stock = models.IntegerField(default=0, verbose_name='Minimum Stok')
    current_stock = models.IntegerField(default=0, verbose_name='Mevcut Stok')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'

    def __str__(self):
        return f"{self.name} ({self.code})"

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Giriş'),
        ('out', 'Çıkış'),
        ('transfer', 'Transfer'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Ürün')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='Depo')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name='Hareket Tipi')
    quantity = models.IntegerField(verbose_name='Miktar')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Birim Fiyat')
    reference_no = models.CharField(max_length=50, verbose_name='Referans No')
    notes = models.TextField(blank=True, verbose_name='Notlar')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='İşlemi Yapan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stok Hareketi'
        verbose_name_plural = 'Stok Hareketleri'

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity}"

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roller'

class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'İzin'
        verbose_name_plural = 'İzinler'

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('role', 'permission')
        verbose_name = 'Rol İzni'
        verbose_name_plural = 'Rol İzinleri'

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')
        verbose_name = 'Kullanıcı Rolü'
        verbose_name_plural = 'Kullanıcı Rolleri' 
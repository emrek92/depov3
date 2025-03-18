from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db import models
from django.db.models import Q, Sum, F, Count, DecimalField
from django.db.models.functions import TruncDate
from datetime import datetime
from django.contrib.auth.models import User
from .models import Product, Category, Unit, Supplier, Warehouse, StockMovement, Role, Permission, RolePermission, UserRole
from .forms import ProductForm, CategoryForm, UnitForm, SupplierForm, WarehouseForm, StockMovementForm, StockReportForm, StockValueReportForm, MovementReportForm, UserForm, UserEditForm, RoleForm, PermissionForm, RolePermissionForm, UserRoleForm
from django import forms
from django.http import HttpResponse
import xlsxwriter
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from .decorators import has_permission, admin_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@has_permission('view_dashboard')
def dashboard(request):
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_suppliers': Supplier.objects.count(),
        'total_warehouses': Warehouse.objects.count(),
        'low_stock_products': Product.objects.filter(current_stock__lte=models.F('min_stock')),
        'recent_movements': StockMovement.objects.select_related('product', 'warehouse').order_by('-created_at')[:10],
    }
    return render(request, 'core/dashboard.html', context)

@login_required
@has_permission('view_products')
def product_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    supplier_filter = request.GET.get('supplier', '')
    warehouse_filter = request.GET.get('warehouse', '')

    products = Product.objects.select_related('category', 'unit', 'supplier', 'warehouse').all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    if supplier_filter:
        products = products.filter(supplier_id=supplier_filter)
        
    if warehouse_filter:
        products = products.filter(warehouse_id=warehouse_filter)

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    warehouses = Warehouse.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'suppliers': suppliers,
        'warehouses': warehouses,
        'search_query': search_query,
        'category_filter': category_filter,
        'supplier_filter': supplier_filter,
        'warehouse_filter': warehouse_filter,
    }
    return render(request, 'core/product_list.html', context)

@login_required
@has_permission('add_product')
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ürün başarıyla oluşturuldu.')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'core/product_form.html', {
        'form': form,
        'title': 'Yeni Ürün Ekle'
    })

@login_required
@has_permission('edit_product')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ürün başarıyla güncellendi.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'core/product_form.html', {
        'form': form,
        'title': 'Ürün Düzenle',
        'product': product
    })

@login_required
@has_permission('delete_product')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Ürün başarıyla silindi.')
        return redirect('product_list')
    
    return render(request, 'core/product_confirm_delete.html', {
        'product': product
    })

@login_required
@has_permission('view_products')
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Ürünün toplam stok değerini hesapla
    total_value = product.current_stock * product.purchase_price
    
    # Ürünle ilgili son stok hareketlerini getir
    movements = StockMovement.objects.filter(product=product).order_by('-created_at')[:10]
    
    context = {
        'product': product,
        'total_value': total_value,
        'movements': movements
    }
    
    return render(request, 'core/product_detail.html', context)

@login_required
@has_permission('view_categories')
def category_list(request):
    search_query = request.GET.get('search', '')
    
    categories = Category.objects.all()
    
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Her kategori için ürün sayısını hesapla
    for category in categories:
        category.product_count = Product.objects.filter(category=category).count()
    
    return render(request, 'core/category_list.html', {
        'categories': categories,
        'search_query': search_query,
    })

@login_required
@has_permission('add_category')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori başarıyla oluşturuldu.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'core/category_form.html', {
        'form': form,
        'title': 'Yeni Kategori Ekle'
    })

@login_required
@has_permission('edit_category')
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori başarıyla güncellendi.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'core/category_form.html', {
        'form': form,
        'title': 'Kategori Düzenle',
        'category': category
    })

@login_required
@has_permission('delete_category')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Kategori başarıyla silindi.')
        return redirect('category_list')
    
    return render(request, 'core/category_confirm_delete.html', {
        'category': category
    })

@login_required
@has_permission('view_units')
def unit_list(request):
    search_query = request.GET.get('search', '')
    units = Unit.objects.all()

    if search_query:
        units = units.filter(
            Q(name__icontains=search_query) |
            Q(symbol__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'units': units,
        'search_query': search_query,
    }
    return render(request, 'core/unit_list.html', context)

@login_required
@has_permission('add_unit')
def unit_create(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Birim başarıyla oluşturuldu.')
            return redirect('unit_list')
    else:
        form = UnitForm()
    
    return render(request, 'core/unit_form.html', {
        'form': form,
        'title': 'Yeni Birim Ekle'
    })

@login_required
@has_permission('edit_unit')
def unit_edit(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Birim başarıyla güncellendi.')
            return redirect('unit_list')
    else:
        form = UnitForm(instance=unit)
    
    return render(request, 'core/unit_form.html', {
        'form': form,
        'title': 'Birim Düzenle',
        'unit': unit
    })

@login_required
@has_permission('delete_unit')
def unit_delete(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    
    if request.method == 'POST':
        unit.delete()
        messages.success(request, 'Birim başarıyla silindi.')
        return redirect('unit_list')
    
    return render(request, 'core/unit_confirm_delete.html', {
        'unit': unit
    })

@login_required
@has_permission('view_suppliers')
def supplier_list(request):
    search_query = request.GET.get('search', '')
    suppliers = Supplier.objects.all()

    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(tax_number__icontains=search_query) |
            Q(tax_office__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'suppliers': suppliers,
        'search_query': search_query,
    }
    return render(request, 'core/supplier_list.html', context)

@login_required
@has_permission('add_supplier')
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tedarikçi başarıyla oluşturuldu.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    
    return render(request, 'core/supplier_form.html', {
        'form': form,
        'title': 'Yeni Tedarikçi Ekle'
    })

@login_required
@has_permission('edit_supplier')
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tedarikçi başarıyla güncellendi.')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'core/supplier_form.html', {
        'form': form,
        'title': 'Tedarikçi Düzenle',
        'supplier': supplier
    })

@login_required
@has_permission('delete_supplier')
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Tedarikçi başarıyla silindi.')
        return redirect('supplier_list')
    
    return render(request, 'core/supplier_confirm_delete.html', {
        'supplier': supplier
    })

@login_required
@has_permission('view_warehouses')
def warehouse_list(request):
    search_query = request.GET.get('search', '')
    warehouses = Warehouse.objects.all()
    
    if search_query:
        warehouses = warehouses.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(manager__icontains=search_query)
        )
    
    return render(request, 'core/warehouse_list.html', {'warehouses': warehouses})

@login_required
@has_permission('add_warehouse')
def warehouse_create(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, 'Depo başarıyla oluşturuldu.')
            return redirect('warehouse_list')
    else:
        form = WarehouseForm()
    
    return render(request, 'core/warehouse_form.html', {'form': form})

@login_required
@has_permission('edit_warehouse')
def warehouse_edit(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, 'Depo başarıyla güncellendi.')
            return redirect('warehouse_list')
    else:
        form = WarehouseForm(instance=warehouse)
    
    return render(request, 'core/warehouse_form.html', {'form': form, 'warehouse': warehouse})

@login_required
@has_permission('delete_warehouse')
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    
    if request.method == 'POST':
        warehouse.delete()
        messages.success(request, 'Depo başarıyla silindi.')
        return redirect('warehouse_list')
    
    return render(request, 'core/warehouse_confirm_delete.html', {'warehouse': warehouse})

@login_required
@has_permission('view_stock_movements')
def stock_movement_list(request):
    search_query = request.GET.get('search', '')
    movement_type = request.GET.get('movement_type', '')
    warehouse_filter = request.GET.get('warehouse', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    movements = StockMovement.objects.select_related('product', 'warehouse', 'created_by').all().order_by('-created_at')
    
    # Kullanıcı filtreleri
    if search_query:
        movements = movements.filter(
            Q(product__name__icontains=search_query) |
            Q(product__code__icontains=search_query) |
            Q(reference_no__icontains=search_query)
        )
    
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
        
    if warehouse_filter:
        movements = movements.filter(warehouse_id=warehouse_filter)
        
    if user_filter:
        movements = movements.filter(created_by_id=user_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            movements = movements.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            movements = movements.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Filtreleme için gerekli veriler
    warehouses = Warehouse.objects.all().order_by('name')
    users = User.objects.filter(is_active=True).order_by('username')
    
    context = {
        'movements': movements,
        'search_query': search_query,
        'movement_type': movement_type,
        'warehouse_filter': warehouse_filter,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
        'movement_types': StockMovement.MOVEMENT_TYPES,
        'warehouses': warehouses,
        'users': users,
    }
    
    return render(request, 'core/stock_movement_list.html', context)

@login_required
@has_permission('add_stock_in')
def stock_in_create(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.movement_type = 'in'  # Giriş hareketi olarak sabitliyoruz
            movement.created_by = request.user
            
            # Stok miktarını artır
            product = movement.product
            product.current_stock += movement.quantity
            product.save()
            movement.save()
            
            messages.success(request, 'Stok giriş hareketi başarıyla oluşturuldu.')
            return redirect('stock_movement_list')
    else:
        form = StockMovementForm(initial={'movement_type': 'in'})
        # Form içinden movement_type alanını gizliyoruz
        form.fields['movement_type'].widget = forms.HiddenInput()
    
    return render(request, 'core/stock_in_form.html', {'form': form, 'title': 'Stok Giriş İşlemi'})

@login_required
@has_permission('add_stock_out')
def stock_out_create(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.movement_type = 'out'  # Çıkış hareketi olarak sabitliyoruz
            movement.created_by = request.user
            
            # Stok kontrolü ve miktarını azalt
            product = movement.product
            if product.current_stock >= movement.quantity:
                product.current_stock -= movement.quantity
                product.save()
                movement.save()
                
                messages.success(request, 'Stok çıkış hareketi başarıyla oluşturuldu.')
                return redirect('stock_movement_list')
            else:
                messages.error(request, f'Yetersiz stok miktarı! Mevcut stok: {product.current_stock} {product.unit.symbol}')
    else:
        form = StockMovementForm(initial={'movement_type': 'out'})
        # Form içinden movement_type alanını gizliyoruz
        form.fields['movement_type'].widget = forms.HiddenInput()
    
    return render(request, 'core/stock_out_form.html', {'form': form, 'title': 'Stok Çıkış İşlemi'})

@login_required
@has_permission('add_stock_transfer')
def stock_transfer_create(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            # Kaynak depodan çıkış
            source_movement = form.save(commit=False)
            source_movement.movement_type = 'out'  # Kaynak depodan çıkış
            source_movement.created_by = request.user
            
            # Birim fiyatı ve miktarı kaydet
            quantity = source_movement.quantity
            unit_price = source_movement.unit_price
            
            # Kaynak depodan ürün çıkışını kontrol et
            current_stock = source_movement.product.current_stock
            if quantity > current_stock:
                messages.error(request, f'Yetersiz stok! Mevcut stok: {current_stock}')
                warehouses = Warehouse.objects.filter(is_active=True).order_by('name')
                return render(request, 'core/stock_transfer_form.html', {'form': form, 'warehouses': warehouses})
            
            # Hedef depoyu al
            target_warehouse_id = request.POST.get('target_warehouse')
            if not target_warehouse_id:
                messages.error(request, 'Hedef depo seçilmedi!')
                warehouses = Warehouse.objects.filter(is_active=True).order_by('name')
                return render(request, 'core/stock_transfer_form.html', {'form': form, 'warehouses': warehouses})
            
            target_warehouse = get_object_or_404(Warehouse, id=target_warehouse_id)
            
            # Kaynak ve hedef depo aynı olmamalı
            if source_movement.warehouse.id == target_warehouse.id:
                messages.error(request, 'Kaynak ve hedef depo aynı olamaz!')
                warehouses = Warehouse.objects.filter(is_active=True).order_by('name')
                return render(request, 'core/stock_transfer_form.html', {'form': form, 'warehouses': warehouses})
            
            # Kaynak depodan çıkış kaydı
            source_movement.save()
            
            # Ürünün stok miktarını azalt (kaynak depo)
            source_movement.product.current_stock -= quantity
            source_movement.product.save()
            
            # Hedef depoya giriş kaydı
            target_movement = StockMovement(
                product=source_movement.product,
                warehouse=target_warehouse,
                movement_type='in',
                quantity=quantity,
                unit_price=unit_price,
                reference_no=source_movement.reference_no,
                notes=f"Transfer: {source_movement.warehouse.name} deposundan transfer",
                created_by=request.user
            )
            target_movement.save()
            
            # Ürünün stok miktarını artır (hedef depo)
            # Bu gerekli değil çünkü zaten product.current_stock kullanıyoruz
            # ancak depo bazlı stok takibi yapılacaksa burası önemli
            
            messages.success(request, 'Stok transfer işlemi başarıyla gerçekleştirildi.')
            return redirect('stock_movement_list')
    else:
        form = StockMovementForm(initial={'movement_type': 'transfer'})
        # Form içinden movement_type alanını gizliyoruz
        form.fields['movement_type'].widget = forms.HiddenInput()
    
    warehouses = Warehouse.objects.filter(is_active=True).order_by('name')
    return render(request, 'core/stock_transfer_form.html', {'form': form, 'warehouses': warehouses, 'title': 'Stok Transfer İşlemi'})

@login_required
@has_permission('view_reports')
def reports(request):
    context = {
        'stock_report_form': StockReportForm(),
        'stock_value_report_form': StockValueReportForm(),
        'movement_report_form': MovementReportForm(),
    }
    return render(request, 'core/reports.html', context)

@login_required
def stock_report(request):
    form = StockReportForm(request.GET)
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        warehouse = form.cleaned_data.get('warehouse')
        category = form.cleaned_data.get('category')

        # Başlangıç stok durumu
        products = Product.objects.all()
        if warehouse:
            products = products.filter(stockmovement__warehouse=warehouse)
        if category:
            products = products.filter(category=category)

        # Stok hareketleri
        movements = StockMovement.objects.all()
        if start_date:
            movements = movements.filter(created_at__gte=start_date)
        if end_date:
            movements = movements.filter(created_at__lte=end_date)
        if warehouse:
            movements = movements.filter(warehouse=warehouse)
        if category:
            movements = movements.filter(product__category=category)

        # Ürün bazında stok hareketleri
        stock_data = []
        for product in products:
            product_movements = movements.filter(product=product)
            in_qty = product_movements.filter(movement_type='IN').aggregate(total=Sum('quantity'))['total'] or 0
            out_qty = product_movements.filter(movement_type='OUT').aggregate(total=Sum('quantity'))['total'] or 0
            
            stock_data.append([
                product.code,
                product.name,
                product.category.name if product.category else '-',
                product.unit.symbol,
                product.current_stock,
                in_qty,
                out_qty,
                product.current_stock - (in_qty - out_qty)  # Başlangıç stoku
            ])

        context = {
            'report_title': 'Stok Durumu Raporu',
            'headers': ['Ürün Kodu', 'Ürün Adı', 'Kategori', 'Birim', 'Mevcut Stok', 'Giriş', 'Çıkış', 'Başlangıç Stok'],
            'data': stock_data,
            'filters': {
                'Başlangıç Tarihi': start_date.strftime('%d.%m.%Y') if start_date else 'Belirtilmedi',
                'Bitiş Tarihi': end_date.strftime('%d.%m.%Y') if end_date else 'Belirtilmedi',
                'Depo': warehouse.name if warehouse else 'Tümü',
                'Kategori': category.name if category else 'Tümü'
            }
        }
    else:
        context = {
            'report_title': 'Stok Durumu Raporu',
            'headers': [],
            'data': [],
            'filters': {}
        }
    
    return render(request, 'core/report_results.html', context)

@login_required
def stock_value_report(request):
    form = StockValueReportForm(request.GET)
    if form.is_valid():
        warehouse = form.cleaned_data.get('warehouse')
        category = form.cleaned_data.get('category')

        products = Product.objects.all()
        if warehouse:
            products = products.filter(stockmovement__warehouse=warehouse)
        if category:
            products = products.filter(category=category)

        stock_data = []
        total_value = 0
        
        for product in products:
            value = product.current_stock * product.purchase_price
            total_value += value
            
            stock_data.append([
                product.code,
                product.name,
                product.category.name if product.category else '-',
                product.unit.symbol,
                product.current_stock,
                f"{product.purchase_price:.2f} ₺",
                f"{value:.2f} ₺"
            ])

        context = {
            'report_title': 'Stok Değer Raporu',
            'headers': ['Ürün Kodu', 'Ürün Adı', 'Kategori', 'Birim', 'Miktar', 'Birim Fiyat', 'Toplam Değer'],
            'data': stock_data,
            'totals': ['', '', '', '', '', 'Toplam:', f"{total_value:.2f} ₺"],
            'filters': {
                'Depo': warehouse.name if warehouse else 'Tümü',
                'Kategori': category.name if category else 'Tümü'
            }
        }
    else:
        context = {
            'report_title': 'Stok Değer Raporu',
            'headers': [],
            'data': [],
            'totals': [],
            'filters': {}
        }
    
    return render(request, 'core/report_results.html', context)

@login_required
@has_permission('view_reports')
def movement_report(request):
    if request.method == 'POST':
        form = MovementReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            movement_type = form.cleaned_data['movement_type']
            warehouse = form.cleaned_data['warehouse']
            category = form.cleaned_data['category']
            
            # Başlangıç sorgusu
            movements = StockMovement.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            ).order_by('-created_at')
            
            # Filtreler
            if movement_type:
                movements = movements.filter(movement_type=movement_type)
            
            if warehouse:
                movements = movements.filter(warehouse=warehouse)
            
            if category:
                movements = movements.filter(product__category=category)
            
            # Toplam değerler
            total_in = movements.filter(movement_type='in').aggregate(
                total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
            )['total'] or 0
            
            total_out = movements.filter(movement_type='out').aggregate(
                total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
            )['total'] or 0
            
            # Filtre bilgilerini hazırla
            filters = []
            if start_date:
                filters.append(f"Başlangıç Tarihi: {start_date}")
            if end_date:
                filters.append(f"Bitiş Tarihi: {end_date}")
            if movement_type:
                movement_name = dict(StockMovement.MOVEMENT_TYPES).get(movement_type, '')
                filters.append(f"Hareket Tipi: {movement_name}")
            if warehouse:
                filters.append(f"Depo: {warehouse.name}")
            if category:
                filters.append(f"Kategori: {category.name}")
            
            # PDF veya Excel çıktısı istendi mi?
            export_format = request.POST.get('export_format')
            if export_format == 'pdf':
                return export_as_pdf(movements, 'Stok Hareketleri Raporu', filters, total_in, total_out)
            elif export_format == 'excel':
                return export_as_excel(movements, 'Stok Hareketleri Raporu', filters, total_in, total_out)
            
            context = {
                'movements': movements,
                'total_in': total_in,
                'total_out': total_out,
                'net_value': total_in - total_out,
                'report_title': 'Stok Hareketleri Raporu',
                'filters': filters,
                'show_form': False
            }
            
            return render(request, 'core/report_results.html', context)
    else:
        form = MovementReportForm()
    
    return render(request, 'core/movement_report.html', {'form': form})

def export_as_excel(movements, title, filters, total_in, total_out):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Formatlar
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
    cell_format = workbook.add_format({'border': 1})
    date_format = workbook.add_format({'border': 1, 'num_format': 'dd.mm.yyyy hh:mm'})
    number_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
    total_format = workbook.add_format({'bold': True, 'bg_color': '#E6E6E6', 'border': 1, 'num_format': '#,##0.00'})
    
    # Başlık
    worksheet.write(0, 0, title, workbook.add_format({'bold': True, 'font_size': 14}))
    
    # Filtreler
    row = 2
    worksheet.write(row, 0, "Filtreler:", workbook.add_format({'bold': True}))
    row += 1
    for i, filter_text in enumerate(filters):
        worksheet.write(row, 0, filter_text)
        row += 1
    
    row += 1
    
    # Tablo başlıkları
    headers = ['Tarih', 'Ürün', 'Depo', 'Hareket Tipi', 'Miktar', 'Birim Fiyat', 'Toplam Değer', 'Referans No', 'İşlem Yapan']
    for col, header in enumerate(headers):
        worksheet.write(row, col, header, header_format)
    
    # Veriler
    row += 1
    for movement in movements:
        worksheet.write_datetime(row, 0, movement.created_at, date_format)
        worksheet.write(row, 1, f"{movement.product.name} ({movement.product.code})", cell_format)
        worksheet.write(row, 2, movement.warehouse.name, cell_format)
        
        movement_type_display = dict(StockMovement.MOVEMENT_TYPES).get(movement.movement_type, '')
        worksheet.write(row, 3, movement_type_display, cell_format)
        
        worksheet.write(row, 4, movement.quantity, number_format)
        worksheet.write(row, 5, movement.unit_price, number_format)
        
        total_value = movement.quantity * movement.unit_price
        worksheet.write(row, 6, total_value, number_format)
        
        worksheet.write(row, 7, movement.reference_no, cell_format)
        user_name = movement.created_by.get_full_name() if movement.created_by.get_full_name() else movement.created_by.username
        worksheet.write(row, 8, user_name, cell_format)
        
        row += 1
    
    # Toplamlar
    row += 1
    worksheet.write(row, 5, "Toplam Giriş Değeri:", total_format)
    worksheet.write(row, 6, total_in, total_format)
    
    row += 1
    worksheet.write(row, 5, "Toplam Çıkış Değeri:", total_format)
    worksheet.write(row, 6, total_out, total_format)
    
    row += 1
    worksheet.write(row, 5, "Net Değer:", total_format)
    worksheet.write(row, 6, total_in - total_out, total_format)
    
    # Sütun genişlikleri
    worksheet.set_column(0, 0, 20)  # Tarih
    worksheet.set_column(1, 1, 30)  # Ürün
    worksheet.set_column(2, 2, 15)  # Depo
    worksheet.set_column(3, 3, 15)  # Hareket Tipi
    worksheet.set_column(4, 4, 10)  # Miktar
    worksheet.set_column(5, 5, 15)  # Birim Fiyat
    worksheet.set_column(6, 6, 15)  # Toplam Değer
    worksheet.set_column(7, 7, 15)  # Referans No
    worksheet.set_column(8, 8, 20)  # İşlem Yapan
    
    workbook.close()
    
    # Excel dosyasını yanıt olarak gönder
    output.seek(0)
    
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=stok_hareketleri_raporu_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response

def export_as_pdf(movements, title, filters, total_in, total_out):
    template = get_template('core/report_pdf_template.html')
    context = {
        'movements': movements,
        'report_title': title,
        'filters': filters,
        'total_in': total_in,
        'total_out': total_out,
        'net_value': total_in - total_out,
    }
    
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=stok_hareketleri_raporu_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    
    # HTML'i PDF'ye dönüştür
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Hata kontrolü
    if pisa_status.err:
        return HttpResponse('PDF oluşturulurken bir hata oluştu.', status=500)
    
    return response

@login_required
@has_permission('view_users')
def user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'core/user_list.html', {'users': users})

@login_required
@admin_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Kullanıcı başarıyla oluşturuldu.')
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'core/user_form.html', {'form': form, 'title': 'Yeni Kullanıcı Ekle'})

@login_required
@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kullanıcı başarıyla güncellendi.')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'core/user_form.html', {'form': form, 'title': 'Kullanıcı Düzenle'})

@login_required
@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Kullanıcı başarıyla silindi.')
        return redirect('user_list')
    return render(request, 'core/confirm_delete.html', {'object': user, 'title': 'Kullanıcı Silme'})

@login_required
@admin_required
def role_list(request):
    roles = Role.objects.all().order_by('name')
    return render(request, 'core/role_list.html', {'roles': roles})

@login_required
@admin_required
def role_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            messages.success(request, 'Rol başarıyla oluşturuldu.')
            return redirect('role_list')
    else:
        form = RoleForm()
    return render(request, 'core/role_form.html', {'form': form, 'title': 'Yeni Rol Ekle'})

@login_required
@admin_required
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rol başarıyla güncellendi.')
            return redirect('role_list')
    else:
        form = RoleForm(instance=role)
    return render(request, 'core/role_form.html', {'form': form, 'title': 'Rol Düzenle'})

@login_required
@admin_required
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        messages.success(request, 'Rol başarıyla silindi.')
        return redirect('role_list')
    return render(request, 'core/confirm_delete.html', {'object': role, 'title': 'Rol Silme'})

@login_required
@admin_required
def role_permissions(request, pk):
    role = get_object_or_404(Role, pk=pk)
    permissions = Permission.objects.all().order_by('name')
    
    if request.method == 'POST':
        selected_permissions = request.POST.getlist('permissions')
        
        # Mevcut izinleri temizle
        RolePermission.objects.filter(role=role).delete()
        
        # Seçilen izinleri ekle
        for permission_id in selected_permissions:
            permission = Permission.objects.get(id=permission_id)
            RolePermission.objects.create(role=role, permission=permission)
        
        messages.success(request, f'"{role.name}" rolü için izinler başarıyla güncellendi.')
        return redirect('role_list')
    
    # Rolün mevcut izinlerini al
    role_permission_ids = RolePermission.objects.filter(role=role).values_list('permission_id', flat=True)
    
    context = {
        'role': role,
        'permissions': permissions,
        'role_permission_ids': role_permission_ids,
    }
    
    return render(request, 'core/role_permissions.html', context)

@login_required
@admin_required
def permission_list(request):
    permissions = Permission.objects.all().order_by('name')
    return render(request, 'core/permission_list.html', {'permissions': permissions})

@login_required
@admin_required
def permission_create(request):
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            permission = form.save()
            messages.success(request, 'İzin başarıyla oluşturuldu.')
            return redirect('permission_list')
    else:
        form = PermissionForm()
    return render(request, 'core/permission_form.html', {'form': form, 'title': 'Yeni İzin Ekle'})

@login_required
@admin_required
def permission_edit(request, pk):
    permission = get_object_or_404(Permission, pk=pk)
    if request.method == 'POST':
        form = PermissionForm(request.POST, instance=permission)
        if form.is_valid():
            form.save()
            messages.success(request, 'İzin başarıyla güncellendi.')
            return redirect('permission_list')
    else:
        form = PermissionForm(instance=permission)
    return render(request, 'core/permission_form.html', {'form': form, 'title': 'İzin Düzenle'})

@login_required
@admin_required
def permission_delete(request, pk):
    permission = get_object_or_404(Permission, pk=pk)
    if request.method == 'POST':
        permission.delete()
        messages.success(request, 'İzin başarıyla silindi.')
        return redirect('permission_list')
    return render(request, 'core/confirm_delete.html', {'object': permission, 'title': 'İzin Silme'})

@login_required
@admin_required
def user_role_assignment(request, user_id):
    user = get_object_or_404(User, id=user_id)
    roles = Role.objects.all().order_by('name')
    
    if request.method == 'POST':
        selected_roles = request.POST.getlist('roles')
        
        # Mevcut rolleri temizle
        UserRole.objects.filter(user=user).delete()
        
        # Seçilen rolleri ekle
        for role_id in selected_roles:
            role = Role.objects.get(id=role_id)
            UserRole.objects.create(user=user, role=role)
        
        messages.success(request, f'"{user.username}" kullanıcısı için roller başarıyla güncellendi.')
        return redirect('user_list')
    
    # Kullanıcının mevcut rollerini al
    user_role_ids = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
    
    context = {
        'user_obj': user,
        'roles': roles,
        'user_role_ids': user_role_ids,
    }
    
    return render(request, 'core/user_roles.html', context) 
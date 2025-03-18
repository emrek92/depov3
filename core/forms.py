from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Product, Category, Unit, Supplier, Warehouse, StockMovement, Role, Permission, RolePermission, UserRole

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'code', 'category', 'unit', 'supplier', 'warehouse',
                 'purchase_price', 'sale_price', 'min_stock', 'current_stock', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'code': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'category': forms.Select(attrs={'class': 'form-select rounded-md shadow-sm mt-1 block w-full'}),
            'unit': forms.Select(attrs={'class': 'form-select rounded-md shadow-sm mt-1 block w-full'}),
            'supplier': forms.Select(attrs={'class': 'form-select rounded-md shadow-sm mt-1 block w-full'}),
            'warehouse': forms.Select(attrs={'class': 'form-select rounded-md shadow-sm mt-1 block w-full'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full', 'step': '0.01'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea rounded-md shadow-sm mt-1 block w-full', 'rows': 3}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea rounded-md shadow-sm mt-1 block w-full', 'rows': 3}),
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'symbol', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'symbol': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea rounded-md shadow-sm mt-1 block w-full', 'rows': 3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'code', 'contact_person', 'phone', 'email', 'address', 'tax_number', 'tax_office', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'code': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'contact_person': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500', 'rows': 3}),
            'tax_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'tax_office': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500', 'rows': 3}),
        }

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'code', 'address', 'phone', 'manager', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input px-4 py-3 rounded-md'}),
            'code': forms.TextInput(attrs={'class': 'form-input px-4 py-3 rounded-md'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea px-4 py-3 rounded-md', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-input px-4 py-3 rounded-md'}),
            'manager': forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea px-4 py-3 rounded-md', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece aktif kullanıcıları göster
        self.fields['manager'].queryset = User.objects.filter(is_active=True)

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'warehouse', 'movement_type', 'quantity', 'unit_price', 'reference_no', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'warehouse': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'movement_type': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500', 'min': '0.01', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500', 'min': '0.01', 'step': '0.01'}),
            'reference_no': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500', 'rows': 3}),
        }

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'password1': forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'password2': forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }

class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500', 'rows': 3}),
        }

class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['name', 'codename', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'codename': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500', 'rows': 3}),
        }

class RolePermissionForm(forms.ModelForm):
    class Meta:
        model = RolePermission
        fields = ['role', 'permission']
        widgets = {
            'role': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'permission': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
        }

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserRole
        fields = ['user', 'role']
        widgets = {
            'user': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'role': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
        }

class StockReportForm(forms.Form):
    start_date = forms.DateField(
        label='Başlangıç Tarihi',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input px-4 py-3 rounded-md'})
    )
    end_date = forms.DateField(
        label='Bitiş Tarihi',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input px-4 py-3 rounded-md'})
    )
    warehouse = forms.ModelChoiceField(
        label='Depo',
        queryset=Warehouse.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-md'})
    )
    category = forms.ModelChoiceField(
        label='Kategori',
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-md'})
    )

class StockValueReportForm(forms.Form):
    warehouse = forms.ModelChoiceField(
        label='Depo',
        queryset=Warehouse.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-md'})
    )
    category = forms.ModelChoiceField(
        label='Kategori',
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-md'})
    )

class MovementReportForm(forms.Form):
    start_date = forms.DateField(
        label='Başlangıç Tarihi',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input px-4 py-3 rounded-md'})
    )
    end_date = forms.DateField(
        label='Bitiş Tarihi',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input px-4 py-3 rounded-md'})
    )
    movement_type = forms.ChoiceField(
        label='Hareket Tipi',
        choices=[('', 'Tümü')] + StockMovement.MOVEMENT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-md'})
    )
    warehouse = forms.ModelChoiceField(
        label='Depo',
        queryset=Warehouse.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-md'})
    )
    category = forms.ModelChoiceField(
        label='Kategori',
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select px-4 py-3 rounded-md'})
    ) 
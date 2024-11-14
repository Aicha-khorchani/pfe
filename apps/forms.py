from django import forms
from .models import Command, Delivery, facture, retour, customer, item, itemvariant, lead, supplier, bonreception ,Livreurs
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import customuser, AdminUser 

# Base styled form
class StyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name , field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-lg bg-gray text-dark border border-primary',  
                'placeholder': field.label or '',  
            })
            if isinstance(field, forms.DateField):
                field.widget.attrs.update({
                    'type': 'date',
                    'class': 'form-control form-control-lg bg-gray text-dark border border-primary',
                })
            elif isinstance(field, forms.ChoiceField):
                field.widget.attrs.update({
                    'class': 'form-select form-select-lg bg-gray text-dark border border-primary',  
                })


class LivreurCreationForm(StyledForm):  
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'id': 'username'
        }),
        label='Username'
    )
    
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Full Name',
            'id': 'full_name'
        }),
        label='Full Name'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'id': 'email'
        }),
        label='Email'
    )
    
    number = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number',
            'id': 'number'
        }),
        label='Phone Number'
    )
    
    company_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Company Name',
            'id': 'company_name'
        }),
        label='Company Name'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'id': 'password1'
        }),
        label='Password'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'id': 'password2'
        }),
        label='Confirm Password'
    )

    class Meta:
        model = Livreurs
        fields = ['username', 'full_name', 'email', 'number', 'company_name']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  
        if commit:
            user.save()  
        return user


class AdminUserCreationForm(StyledForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Full Name',
            'id': 'full_name'
        }),
        label='Full Name'
    )
    
    email = forms.EmailField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Email Address',
            'id': 'email'
        }),
        label='email'
    )
    
    position = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Position',
            'id': 'position'
        }),
        label='position'
    )

    department = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Department',
            'id': 'department'
        }),
        label='department'
    )


    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'id': 'password'
        }),
        label='password'
    )

    class Meta:
        model = AdminUser
        fields = ['username', 'email', 'full_name', 'position', 'department', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = True
        if commit:
            user.save()
        return user


class customuserCreationForm(StyledForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = customuser 
        fields = ('username', 'full_name', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


class CustomUserChangeForm(StyledForm, UserChangeForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'full name', 'id': 'user_name'}), label='')
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'email address', 'id': 'email'}), label='')
    is_active = forms.BooleanField(widget=forms.CheckboxInput(), label='Active', required=False)
    is_staff = forms.BooleanField(widget=forms.CheckboxInput(), label='Staff', required=False)

    class Meta:
        model = customuser
        fields = ('username', 'email', 'full_name', 'is_active', 'is_staff')


class BonReceptionForm(StyledForm):
    supplier_id = forms.ModelChoiceField(queryset=supplier.objects.all(), required=True, label="Select supplier")
    item = forms.ModelChoiceField(queryset=item.objects.all(), required=True, label="Select Product")
    variant = forms.ModelChoiceField(queryset=itemvariant.objects.all(), required=True, label="Select Variant")

    class Meta:
        model = bonreception
        fields = ('delivery_address', 'delivery_date', 'supplier_id', 'item', 'variant', 'quantity_delivered', 'transportation_type', 'unit_of_measure')



class CustomUserCreationForm(StyledForm, UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True, help_text='Enter the full name of the user.')
    email = forms.EmailField(required=True, help_text='Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'password1', 'password2')


class FactureForm(StyledForm):
    customer = forms.ModelChoiceField(queryset=customer.objects.all(), required=True, label="Select customer")
    command = forms.ModelChoiceField(queryset=Command.objects.all(), required=True, label="Select command")
    product = forms.ModelChoiceField(queryset=item.objects.all(), required=True, label="Select Product")
    variant = forms.ModelChoiceField(queryset=itemvariant.objects.all(), required=True, label="Select Variant")
    class Meta:
        model = facture
        fields = ['datef', 'customer', 'command', 'addressf', 'product', 'tax', 'discount', 'payment_method', 'variant', 'qte_facture', 'ttc', 'price']
        exclude = ['facture_id']


class leadForm(StyledForm):
    class Meta:
        model = lead
        fields = ['company_name','contact_person', 'position', 'contact','score', 'description']


class UpdateitemForm(StyledForm):
    class Meta:
        model = item
        fields = ['product_name', 'unit_price', 'volume_price']
        exclude = ['item']


class UpdateItemVariant(StyledForm):
    class Meta:
        model = itemvariant
        fields = ['item', 'variant_name', 'variant_value']
        exclude = ['variant_id']


class customerForm(StyledForm):
    class Meta:
        model = customer
        fields = ['customer_name','contact_person','email','phone_number']
        exclude = ['customer']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, label="", widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg bg-light fs-6',
        'placeholder': 'full name',
        'id': 'user_name',
        'name': 'user_name',
        'required': ''
    }))
    password = forms.CharField(max_length=255, label="", widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg bg-light fs-6',
        'placeholder': 'password'
    }))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(request=None, username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid username or password")
        return self.cleaned_data


class UpdateLeadForm(StyledForm):
    class Meta:
        model = lead
        fields = ['company_name','contact_person', 'position', 'contact','score', 'description']


class UpdateSupplierForm(StyledForm):
    class Meta:
        model = supplier
        fields = ['supplier_name','contact_info', 'address', 'categories_supplied','payment_terms', 'cost', 'interaction_quality', 'feedback']


class UpdatecustomerForm(StyledForm):
    class Meta:
        model = customer
        fields = ['customer','customer_name','contact_person','email','phone_number']


class itemForm(StyledForm):
    class Meta:
        model = item
        fields = ['product_name', 'unit_price', 'volume_price']
        exclude = ['item']
        error_messages = {
            'product_name': {
                'required': 'Le nom du produit est obligatoire.',
                'max_length': 'Le nom du produit ne peut pas dépasser 255 caractères.',
            },
            'unit_price': {
                'required': 'Le prix unitaire est obligatoire.',
                'invalid': 'Le prix unitaire doit être un nombre.',
            },
            'volume_price': {
                'required': 'Le prix de volume est obligatoire.',
                'invalid': 'Le prix de volume doit être un nombre.',
            },
        }


class itemvariantForm(StyledForm):
    class Meta:
        model = itemvariant
        fields = ['item', 'variant_name', 'variant_value']
        exclude = ['variant']
        
class customerDeleteForm(forms.Form):
    customer_id = forms.IntegerField()  
    error_messages = {
            'customer_id': {
                'required': 'customer id est obligatoire.',
                'invalid': 'id doit être un nombre.',
            },
        }

    
class RetourDeleteForm(forms.Form):
    retour_id = forms.IntegerField() 
    error_messages = {
            'retour_id': {
                'required': 'retour id est obligatoire.',
                'invalid': 'id doit être un nombre.',
            },
        }    
 
class DeleteLeadForm(forms.Form):
    lead = forms.IntegerField()
    error_messages = {
            'lead': {
                'required': 'lead id est obligatoire.',
                'invalid': 'id doit être un nombre.',
            },
        }
    
class RetourForm(StyledForm):
    client = forms.ModelChoiceField(queryset=customer.objects.all(), required=True, label="Select Customer")
    supplier = forms.ModelChoiceField(queryset=supplier.objects.all(), required=True, label="Select Supplier")
    produit = forms.ModelChoiceField(queryset=item.objects.all(), required=True, label="Select Product")
    variant = forms.ModelChoiceField(queryset=itemvariant.objects.all(), required=True, label="Select Variant")
    livreur = forms.ModelChoiceField(queryset=Livreurs.objects.all(), required=True, label="Select Delivery Person")
    numero_c = forms.ModelChoiceField(queryset=Command.objects.all(), required=True, label="Select Command Number")

    class Meta:
        model = retour
        fields = ['supplier','date_retour', 'client', 'produit', 'quantite_retournee', 'raison_retour', 'livreur', 'informations_supp', 'numero_c', 'statut_retour', 'variant']
    
    
    
    
class DeleteSupplierForm(forms.Form):
    supplier_id = forms.IntegerField()
    error_messages = {
            'supplier_id': {
                'required': 'supplier id est obligatoire.',
                'invalid': 'id doit être un nombre.',
            },
        }

class ItemDeleteForm(forms.Form):
    item_id = forms.IntegerField()
    error_messages = {
            'item_id': {
                'required': 'item id est obligatoire.',
                'invalid': 'id doit être un nombre.',
            },
        }

class VariantDeleteForm(forms.Form):
    variant_id = forms.IntegerField()
    error_messages = {
            'variant_id': {
                'required': 'variant id est obligatoire.',
                'invalid': 'id doit être un nombre.',
            },
        }
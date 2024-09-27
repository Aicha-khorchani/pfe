from django import forms
from .models import   retour, customer, item, itemvariant,lead, supplier ,bonreception
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import customuser


class customuserCreationForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg bg-light fs-6', 'placeholder': 'full name', 'id': 'user_name'}), label='')
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg bg-light fs-6', 'placeholder': 'email address', 'id': 'email'}), label='')
    class Meta(UserCreationForm.Meta):
        model = customuser
        fields = ('username', 'full_name', 'email', 'password1', 'password2')
    def __init__(self, *args, **kwargs):
        super(customuserCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control form-control-lg bg-light fs-6'
            })


class BonReceptionForm(forms.ModelForm):
    class Meta:
        model = bonreception
        fields = [
            'delivery_date', 
            'delivery_address', 
            'supplier_id', 
            'item', 
            'quantity_delivered', 
            'unit_of_measure', 
            'transportation_type', 
            'variant_id'
        ]
        



class leadForm(forms.ModelForm):
    class Meta:
        model = lead
        fields = ['company_name','contact_person', 'position', 'contact','score', 'description']


class UpdateitemForm(forms.ModelForm):
    class Meta:
        model = item
        fields = [  'product_name',  'unit_price', 'volume_price']
        exclude = ['item']


class UpdateItemVariant(forms.ModelForm):
    class Meta:
        model = itemvariant
        fields = ['item', 'variant_name', 'variant_value']
        exclude= [ 'variant_id']

class customerForm(forms.ModelForm):
    class Meta:
        model = customer
        fields =['customer_name','contact_person','email','phone_number' ]
        exclude = ['customer']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, label="", widget=forms.TextInput(attrs={'class': 'form-control form-control-lg bg-light fs-6', 'placeholder': 'full name', 'id': 'user_name', 'name': 'user_name', 'required': ''}))
    password = forms.CharField(max_length=255, label="", widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg bg-light fs-6', 'placeholder': 'password'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(request=None, username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid username or password")
        return self.cleaned_data



class UpdateLeadForm(forms.ModelForm):
    class Meta:
        model = lead
        fields = ['company_name','contact_person', 'position', 'contact','score', 'description']

class UpdateSupplierForm(forms.ModelForm):
    class Meta:
        model = supplier
        fields = ['supplier_name','contact_info', 'address', 'categories_supplied','payment_terms', 'cost', 'interaction_quality', 'feedback']


class UpdatecustomerForm(forms.ModelForm):
    class Meta:
        model = customer
        fields =['customer','customer_name','contact_person','email','phone_number' ]

class itemForm(forms.ModelForm):
    class Meta:
        model = item
        fields = [ 'product_name', 'unit_price', 'volume_price']
        exclude = ['item']

class itemvariantForm(forms.ModelForm):
    class Meta:
        model = itemvariant
        fields = ['item', 'variant_name', 'variant_value']
        exclude = ['variant']
        
class customerDeleteForm(forms.Form):
    customer_id = forms.IntegerField()  
    
    
class RetourDeleteForm(forms.Form):
    retour_id = forms.IntegerField()  
    
class DeleteLeadForm(forms.Form):
    lead = forms.IntegerField()
    
class RetourForm(forms.ModelForm):
    class Meta:
        model = retour
        fields = ['supplier', 'client', 'produit', 'quantite_retournee', 'raison_retour', 'livreur', 'informations_supp', 'numero_c', 'statut_retour']
    
class DeleteSupplierForm(forms.Form):
    supplier_id = forms.IntegerField()

class ItemDeleteForm(forms.Form):
    item_id = forms.IntegerField()

class VariantDeleteForm(forms.Form):
    variant_id = forms.IntegerField()
from django import forms
from .models import    customer, orderitem, itemvariant,centreddata
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




class centreddataForm(forms.ModelForm):
    class Meta:
        model = centreddata
        fields = ['company_name','contact_person', 'position', 'contact','score', 'description']




class UpdateorderitemForm(forms.ModelForm):
    class Meta:
        model = orderitem
        fields = [ 'order_id', 'product_name', 'quantity', 'unit_price', 'total_price']
        exclude = ['item']


class UpdateVariantForm(forms.ModelForm):
    class Meta:
        model = itemvariant
        fields = ['item', 'variant_name', 'variant_value']
        exclude= [ 'variant']

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
        model = centreddata
        fields = ['company_name','contact_person', 'position', 'contact','score', 'description']


class UpdatecustomerForm(forms.ModelForm):
    class Meta:
        model = customer
        fields =['customer','customer_name','contact_person','email','phone_number' ]

class orderitemForm(forms.ModelForm):
    class Meta:
        model = orderitem
        fields = ['order_id', 'product_name', 'quantity', 'unit_price', 'total_price']
        exclude = ['item']

class itemvariantForm(forms.ModelForm):
    class Meta:
        model = itemvariant
        fields = ['item', 'variant_name', 'variant_value']
        exclude = ['variant']

class customerDeleteForm(forms.Form):
    customer = forms.IntegerField()
    
class DeleteLeadForm(forms.Form):
    centreddata = forms.IntegerField()
    

class OrderDeleteForm(forms.Form):
    order = forms.IntegerField()

class ItemDeleteForm(forms.Form):
    item = forms.IntegerField()

class VariantDeleteForm(forms.Form):
    variant = forms.IntegerField()
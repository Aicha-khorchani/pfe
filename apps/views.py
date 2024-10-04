from datetime import datetime
import decimal
import logging
import os
from venv import create
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from requests import request
from rest_framework.decorators import api_view
from  saleManagment.settings import MEDIA_ROOT
from .models import  Stock, customuser, facture, leaddata, lead, customer, itemvariant, item, supplier , retour,bonreception ,AdminUser
from .forms import CustomUserChangeForm, DeleteSupplierForm, FactureForm, UpdateSupplierForm, customerDeleteForm, ItemDeleteForm, LoginForm, UpdatecustomerForm,DeleteLeadForm, UpdateLeadForm, itemForm
from .forms import  UpdateitemForm, UpdateItemVariant, VariantDeleteForm, customuserCreationForm ,RetourForm,RetourDeleteForm,BonReceptionForm,AdminUserCreationForm  
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.db.models import F,Count
from django.contrib.auth.decorators import user_passes_test






def registration_view(request):
    if request.method == 'POST':
        form = customuserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = customuserCreationForm()
    return render(request, 'register.html', {'form': form})



@api_view(['GET', 'POST', 'PUT', 'DELETE'])

def add_bonreception(request):
    if request.method == 'POST':
        form = BonReceptionForm(request.POST)
        if form.is_valid():
            bonreception = form.save()
    #zdt partie hethy bch tautomatizi l stock
            stock, created = Stock.objects.get_or_create(item=bonreception.item, item_variant=bonreception.variant)
            if created :
                  stock.quantity_available = bonreception.quantity_delivered
            else:
                  stock.quantity_available += bonreception.quantity_delivered
            stock.save()
     #zdt partie hethy bch tautomatizi l stock
            return redirect('all_bonreception')
        else:
            print(form.errors)  
    else:
        form = BonReceptionForm()
    return render(request, 'addreception.html', {'form': form})


def update_bonreception(request, delivery):
    bonreception_instance = get_object_or_404(bonreception, pk=delivery)
    
    if request.method == 'POST':
        print(request.POST)  
        form = BonReceptionForm(request.POST, instance=bonreception_instance)  
        
        if form.is_valid():
            form.save() 
            return redirect('all_bonreception') 
        else:
            print(form.errors)  

    else:
        form = BonReceptionForm(instance=bonreception_instance) 

    return render(request, 'updatereception.html', {'form': form})


def all_bonreception(request):
    bonreceptions = bonreception.objects.all()
    return render(request, 'allreception.html', {'bonreceptions': bonreceptions})


def search_bonreception(request):
    searched = request.GET.get('searched', '')
    if searched:
        bonreceptions = bonreception.objects.filter(delivery=searched)
    else:
        bonreceptions = bonreception.objects.all()
    return render(request, 'search_bonreception.html', {'bonreceptions': bonreceptions, 'searched': searched})

def allcustomers(request):
    customers = customer.objects.all()
    return render(request, 'allcustomers.html', {'customers': customers})

def all_leads(request):
    leads = lead.objects.all()
    return render(request, 'all_leads.html', {'leads': leads})

def all_retour(request):
    retours = retour.objects.all()
    return render(request, 'allretour.html', {'retours': retours})

def add_retour(request):
    if request.method == 'POST':
        form = RetourForm(request.POST)
        if form.is_valid():
            retour = form.save()
            #zdt partie hethy 3 ligne bch notomatizi stock ba9i ken i5dm cv 
            stock, created = Stock.objects.get_or_create(item=retour.produit, item_variant=retour.variant)
            if created :
                stock.quantity_available = retour.quantite_retournee
            else :
                stock.quantity_available = stock.quantity_available + retour.quantite_retournee
            stock.save()
            #zdt partie hethy 3 ligne bch notomatizi stock ba9i ken i5dm cv 
            return redirect('all_retour')
    else:
        form = RetourForm()
    return render(request, 'addretour.html', {'form': form})

def update_retour(request, retour_id):
    retour_instance = get_object_or_404(retour, pk=retour_id)
    if request.method == 'POST':
        form = RetourForm(request.POST, instance=retour_instance)
        if form.is_valid():
            form.save()
            return redirect('all_retour') 
    else:
        form = RetourForm(instance=retour_instance)
    return render(request, 'updateretour.html', {'form': form})


def delete_bonreception(request):
    if request.method == 'POST':
        delivery_id = request.POST.get('delivery_id')
        bonreception_instance = get_object_or_404(bonreception, delivery=delivery_id)
        bonreception_instance.delete()
        return redirect('all_bonreception')

    return render(request, 'delete_bonreception.html')



def delete_retour(request):
    form = RetourDeleteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        retour_id = form.cleaned_data['retour_id']
        retour_obj = get_object_or_404(retour, pk=retour_id)  
        retour_obj.delete()
        return redirect('all_retour') 
    return render(request, 'delete_retour.html', {'form': form})



def search_return(request):
    if request.method == 'GET':
        searched = request.GET.get('searched','')
        if searched:
            retours = retour.objects.filter(retour__icontains=searched)
        else:
            retours= retour.objects.all()
        return render(request, 'search_return.html', {'retours': retours, 'searched': searched})
    else:
        return render(request, 'search_return.html',{})
    
                      


def customer_delete(request):
    form = customerDeleteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        customer_id = form.cleaned_data['customer_id']
        customer_obj = get_object_or_404(customer, pk=customer_id)  # Renamed local variable
        customer_obj.delete()
        return redirect('allcustomers')
    return render(request, 'deletecustomer.html', {'form': form})


def all_Details(request):
    leaddatas = leaddata.objects.all()
    return render(request, 'allleaddata.html', {'leaddatas': leaddatas})

def all_items(request):
    items = item.objects.all()
    itemvariants = itemvariant.objects.all()
    return render(request, 'allproducts.html', {'items': items, 'itemvariants': itemvariants})

def supplier_list(request):
    suppliers = supplier.objects.all()
    return render(request, 'allsupplier.html', {'suppliers': suppliers})


def search_supplier(request):
    if request.method == 'GET':
        search = request.GET.get('search', '')
        if search:
            query = Q(product_quality__icontains=search) | \
                    Q(supplier_name__icontains=search) | \
                    Q(contact_info__icontains=search) | \
                    Q(address__icontains=search) | \
                    Q(categories_supplied__icontains=search) | \
                    Q(payment_terms__icontains=search)| \
                    Q(feedback__icontains=search)
            suppliers = supplier.objects.filter(query)
        else:
            suppliers = supplier.objects.all()
        return render(request, 'searchsupplier.html', {'search': search,'suppliers': suppliers})
    else:
        return render(request, 'searchsupplier.html')



def search_customers(request):
    if request.method == "GET":
        searched = request.GET.get('searched', '')
        query = Q(customer_name__icontains=searched) | \
                Q(contact_person__icontains=searched) | \
                Q(email__icontains=searched) | \
                Q(phone_number__icontains=searched)
        customers = customer.objects.filter(query)
        return render(request, 'search_results.html', {'searched': searched, 'customers': customers})
    else:
        return render(request, 'search_results.html', {})


def add_customer(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        contact_person = request.POST.get('contact_person')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        customer.objects.create(
            customer_name=customer_name,
            contact_person=contact_person,
            email=email,
            phone_number=phone_number
        )
        return redirect('allcustomers')
    return render(request, 'addcustomer.html')



logger = logging.getLogger(__name__)


def get_stock_levels(request):
    stocks = Stock.objects.all()
    return render(request, 'allstock.html', {'stocks': stocks})





def search_product(request):
    if request.method == "GET":
        searched = request.GET.get('searched', '')
        if searched:
            query = Q(product_name__icontains=searched) | \
                    Q(unit_price__icontains=searched) | \
                    Q(volume_price__icontains=searched) 
            items = item.objects.filter(query)
        else:
            items = item.objects.all()
        return render(request, 'search_product.html', {'items': items, 'searched': searched})
    else:
        return render(request, 'search_product.html', {})



def search_lead(request):
    if request.method == 'GET':
        search = request.GET.get('search', '')
        if search:
            query = Q(company_name__icontains=search) | \
                    Q(contact_person__icontains=search) | \
                    Q(position__icontains=search) | \
                    Q(contact__icontains=search) | \
                    Q(description__icontains=search)
            leads = lead.objects.filter(query)
        else:
            leads = lead.objects.all()
        return render(request, 'searchlead.html', {'leads': leads})
    else:
        return render(request, 'searchlead.html')

    
    
def delete_facture(request):
    if request.method == 'POST':
        facture_id = request.POST.get('facture_id')  # Get the entered facture ID from the form
        try:
            fact = get_object_or_404(facture, pk=facture_id)  # Fetch the Facture using the entered ID
            fact.delete()  # Delete the facture
            return redirect('get_all_factures')  # Redirect after deletion
        except facture.DoesNotExist:
            return render(request, 'deletefacture.html', {'error': 'Facture ID does not exist'})  # Error if not found
    return render(request, 'deletefacture.html')  
   
   
def update_facture(request, id):
    fact = get_object_or_404(facture, facture=id)
    
    if request.method == 'POST':
        form = FactureForm(request.POST, instance=fact)
        if form.is_valid():
            form.save()
            return redirect('get_all_factures')  # Redirect after update
    else:
        form = FactureForm(instance=fact)
    
    return render(request, 'updatefacture.html', {'form': form})


def get_all_factures(request):
    factures = facture.objects.all()
    return render(request, 'allfacture.html', {'factures': factures})


def search_facture(request):
    if request.method == 'GET':
        searched_id = request.GET.get('searched', '')
        if searched_id:
            factures = facture.objects.filter(facture_id=searched_id)
        else:
            factures = facture.objects.all()
        
        return render(request, 'search_facture.html', {'factures': factures, 'searched': searched_id})
    
    
def add_facture(request):
    if request.method == 'POST':
        datef = request.POST.get('datef')
        customer_id = request.POST.get('customer_id')
        addressf = request.POST.get('addressf')
        product_id = request.POST.get('product')
        tax = request.POST.get('tax')
        discount = request.POST.get('discount')
        payment_method = request.POST.get('Payment_Method')
        variant_id = request.POST.get('variant')
        qte_facture = request.POST.get('qte_facture')
        ttc = request.POST.get('TTC')
        price = request.POST.get('price')
        try:
            customer_obj = customer.objects.get(pk=customer_id)
            product_obj = item.objects.get(pk=product_id)
            variant_obj = itemvariant.objects.get(pk=variant_id)
        except (customer.DoesNotExist, item.DoesNotExist, itemvariant.DoesNotExist):
            return render(request, 'addfacture.html', {
                'error': 'Invalid customer, product, or variant provided.'
            })

        facture_obj = facture(
            datef=datef,
            addressf=addressf,
            tax=tax,
            discount=discount,
            payment_method=payment_method,
            qte_facture=qte_facture,
            ttc=ttc,
            price=price,
            product=product_obj,
            variant=variant_obj,
            customer=customer_obj,
        )
        facture_obj.save()
            #zdt partie hethy bch tautomatizi l stock lba9i ken i5dem cv
        stock, created = Stock.objects.get_or_create(item=product_obj, item_variant=variant_obj)
        if created:
            stock.quantity_available = 0
        if stock.quantity_available < decimal.Decimal(facture_obj.qte_facture):
            return render(request, 'addfacture.html', {
                'error': 'Vous n\'avez pas assez de stock pour cette quantité.'
            })
        else:
            stock.quantity_available -= decimal.Decimal(facture_obj.qte_facture)
            stock.save()

        return redirect('get_all_factures')  
    else:
        return render(request, 'addfacture.html')


def updatelead(request, id):
    lead_instance = lead.objects.get(pk=id)
    if request.method == 'POST':
        form = UpdateLeadForm(request.POST, instance=lead_instance)
        if form.is_valid():
            print("Form is valid!")  # this line justfor test tw nfas5a ba3teli hoa w prints lkol
            form.save()
            return redirect('all_leads')
        else:
            print("Form is not valid!")
        for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
    else:
        form = UpdateLeadForm(instance=lead_instance)
    return render(request, 'updatelead.html', {'lead': lead_instance, 'form': form})



def update_customer(request, customer_id):
    customer_instance = customer.objects.get(pk=customer_id)
    if request.method == 'POST':
        form = UpdatecustomerForm(request.POST, instance=customer_instance)
        if form.is_valid():
            print("Form is valid!")  # this line justfor test tw nfas5a ba3teli hoa w prints lkol
            form.save()
            return redirect('allcustomers')
        else:
            print("Form is not valid!")
        for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
    else:
        form = UpdatecustomerForm(instance=customer_instance)
    return render(request, 'updatecustomer.html', {'customer': customer_instance, 'form': form})


def update_item_variant(request, variant_id):
    try:
        variant_instance = itemvariant.objects.get(variant_id=variant_id)
    except itemvariant.DoesNotExist:
        raise Http404("Item Variant does not exist")
    if request.method == 'POST':
        form = UpdateItemVariant(request.POST or None, instance=variant_instance)
        if form.is_valid():
            print("Form is valid!")  # this line just for testing purposes w bara
            form.save()
            return redirect('all_items')
        else:
            print("Form is not valid!")  # ntesty beha w bra
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
    else:
        form = UpdateItemVariant(instance=variant_instance)
    return render(request, 'updatevariant.html', {'itemvariant': variant_instance, 'form': form})

def delete_lead(request):
    form = DeleteLeadForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        lead_id = form.cleaned_data['lead']  
        lead_obj = get_object_or_404(lead, pk=lead_id)  
        lead_obj.delete()
        return redirect('all_leads')
    return render(request, 'deletelead.html', {'form': form})




def product_delete(request):
    form = ItemDeleteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item_id = form.cleaned_data['item_id']
        item_obj = get_object_or_404(item, pk=item_id)
        item_obj.delete()
        return redirect('all_items')
    return render(request, 'deleteproduct.html', {'form': form})

def delete_supplier(request):
    form = DeleteSupplierForm(request.POST or None)
    print("Form initialized")
    if request.method == 'POST':
       print("POST method detected")
    if form.is_valid():
        print("Form is valid")
        supplier_id = form.cleaned_data['supplier_id']  
        supplier_obj = get_object_or_404(supplier, pk=supplier_id)  
        supplier_obj.delete()
        return redirect('supplier_list')
    else:
        print("Form is invalid")  
        print(form.errors) 
        
    print("Template is being rendered")
    return render(request, 'deletesupplier.html', {'form': form})

def variant_delete(request):
    form = VariantDeleteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        variant_id = form.cleaned_data['variant_id']
        variant_obj = get_object_or_404(itemvariant, pk=variant_id)
        variant_obj.delete()
        return redirect('all_items')
    return render(request, 'deletevariant.html', {'form': form})


def add_item(request):
    if request.method == 'POST':
        form = itemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_items')
    else:
        form = itemForm()
    return render(request, 'addproduct.html', {'form': form})


def add_lead(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        contact_person = request.POST.get('contact_person')
        position = request.POST.get('position')
        contact = request.POST.get('contact')
        score = request.POST.get('score')
        description = request.POST.get('description')

        lead.objects.create(
            company_name=company_name,
            contact_person=contact_person,
            position=position,
            contact=contact,
            score=score,
            description=description,
        )
        return redirect('all_leads')

    return render(request, 'addlead.html')




def add_data(request):
    if request.method == 'POST':
        print("Form submitted successfully")
        lead_id = request.POST.get('lead_id')
        score = request.POST.get('score')
        status = request.POST.get('status')
        print("Lead ID:", lead_id)
        print("Score:", score)
        print("Status:", status)
        
        contract_file = request.FILES.get('contract_file')
        revenue = request.POST.get('revenue', '0')
        print("Contract File:", contract_file)
        print("Revenue:", revenue)
        # Check if required fields are missing
        if not lead_id or not score or not status:
            print("Missing required fields")
            return render(request, 'addleaddata.html', {'error': 'Lead ID, Score, and Status are required'})
        try:
            lead_instance = lead.objects.get(pk=lead_id)
            print("Lead found:", lead_instance)
        except lead.DoesNotExist:
            print("Lead ID does not exist")
            return render(request, 'addleaddata.html', {'error': 'Invalid lead ID'})
        
        # Validate revenue format
        try:
            revenue = Decimal(revenue)
            if revenue < 0:
                print("Revenue is negative")
                return render(request, 'addleaddata.html', {'error': 'Revenue must be greater than or equal to 0'})
        except InvalidOperation:
            print("Invalid revenue format")
            return render(request, 'addleaddata.html', {'error': 'Invalid revenue format'})
        
        # Create and save the leaddata instance
        try:
            new_data = leaddata.objects.create(
                lead=lead_instance,
                score=score,
                status=status,
                contract_file=contract_file,
                revenue=revenue
            )
            print("Data created successfully:", new_data)
        except Exception as e:
            print("Error saving data:", e)
            return render(request, 'addleaddata.html', {'error': 'An error occurred while saving data'})
        print("Redirecting to success page or lead list")
        return redirect('all_leads')  # Replace with your actual success URL
    # For GET requests, render the empty form
    print("Rendering form for GET request")
    return render(request, 'addleaddata.html')


def add_itemvariant(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item_instance = get_object_or_404(item, pk=item_id)
        variant_name= request.POST.get('variant_name')
        variant_value = request.POST.get('variant_value')
        itemvariant.objects.create(
            item =item_instance,
            variant_name=variant_name,
            variant_value=variant_value,
        )
        return redirect('all_items')
    return render(request, 'addvariant.html')





def doc(request):
    return render(request,"doc.html")

def invoice(request):
    return render(request,"invoice.html")

def returne(request):
    return render(request,"returne.html")

def reception(request):
    return render(request,"reception.html")

def home(request):
    return render(request,"home.html")

def stock(request):
    return render(request,"stock.html")

def partners(request):
    return render(request,"partners.html")

def admin(request):
    return render(request,"admin.html")


def leads(request):
    return render(request,"leads.html")

def update_password(request):
    return render(request, 'updatepassword.html')

def updatesupplier(request, supplier_id):
    supplier_instance = get_object_or_404(supplier,  pk=supplier_id)
    if request.method == "POST":
        form = UpdateSupplierForm(request.POST or None, instance=supplier_instance)
        if form.is_valid():
            print("Form is valid!")  # this line justfor test tw nfas5a ba3teli hoa w prints lkol
            form.save()
            return redirect('supplier_list')  
        else:
            print("Form is not valid!")  # ntesty beha w bra
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
    else:
        form = UpdateSupplierForm(instance=supplier_instance)
    return render(request, 'updatesupplier.html', {'supplier': supplier_instance, 'form': form})


def update_item(request, item_id):
    item_instance = get_object_or_404(item, item=item_id)
    if request.method == 'POST':
        form = UpdateitemForm(request.POST or None, instance=item_instance)
        if form.is_valid():
            print("Form is valid!")  # this line justfor test tw nfas5a ba3teli hoa w prints lkol
            form.save()
            return redirect('all_items')
        else:
            print("Form is not valid!")  # ntesty beha w bra
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
    else:
        form = UpdateitemForm(instance=item_instance)
    return render(request, 'updateproduct.html', {'order_item': item_instance, 'form': form})



def add_supplier(request):
    if request.method == 'POST':
        supplier_name = request.POST.get('supplier_name')
        contact_info = request.POST.get('contact_info')
        address = request.POST.get('address')
        categories_supplied = request.POST.get('categories_supplied')
        payment_terms = request.POST.get('payment_terms')
        product_quality = request.POST.get('product_quality')
        cost = request.POST.get('cost')
        interaction_quality = request.POST.get('interaction_quality')
        feedback = request.POST.get('feedback')

        # Convert fields to appropriate types if necessary
        try:
            product_quality = int(product_quality) if product_quality else None
            cost = int(cost) if cost else None
            interaction_quality = int(interaction_quality) if interaction_quality else None
        except ValueError:
            # Handle conversion error if necessary
            product_quality = cost = interaction_quality = None

        supplier.objects.create(
            supplier_name=supplier_name,
            contact_info=contact_info,
            address=address,
            categories_supplied=categories_supplied,
            payment_terms=payment_terms,
            product_quality=product_quality,
            cost=cost,
            interaction_quality=interaction_quality,
            feedback=feedback
        )

        return redirect('supplier_list')

    return render(request, 'addsupplier.html')



def  login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to a success page
            else:
                # Invalid login
                return render(request, 'login.html', {'form': form, 'error_message': 'Invalid username or password'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def  logout_view(request):
    logout(request)
    messages.success(request, ("you are  logged out !"))
    return redirect('login')


def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def user_list(request):
    print(f"User: {request.user}, Is Admin: {is_admin(request.user)}")  # Debug line
    if not is_admin(request.user):
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home') 
    users = customuser.objects.all()
    return render(request, 'user_list.html', {'users': users})


@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = customuserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.set_password(form.cleaned_data['password1'])  
            user.save() 
            messages.success(request, "User  created successfully!")
            return redirect('user_list')  
    else:
        form = customuserCreationForm()

    return render(request, 'user_form.html', {'form': form})



@user_passes_test(is_admin)
def user_update(request, user_id):
    user = get_object_or_404(customuser, id=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'user_form.html', {'form': form})


@user_passes_test(is_admin)
def user_delete(request, user_id):
    user = get_object_or_404(customuser, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'deleteuser.html', {'user': user})

@user_passes_test(is_admin)
def admin_user_create(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin user created successfully.")
            return redirect('admin_user_list') 
    else:
        form = AdminUserCreationForm()
    return render(request, 'createadmin.html', {'form': form})


@user_passes_test(is_admin)
def admin_user_update(request, user_id):
    admin_user = get_object_or_404(AdminUser, id=user_id)
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST, instance=admin_user)
        if form.is_valid():
            form.save()
            return redirect('admin_user_list')
    else:
        form = AdminUserCreationForm(instance=admin_user)
    return render(request, 'updateadmin.html', {'form': form})


@user_passes_test(is_admin)
def admin_user_delete(request, user_id):
    admin_user = get_object_or_404(AdminUser, id=user_id)
    if request.method == 'POST':
        admin_user.delete()
        return redirect('admin_user_list')
    return render(request, 'adminconfirm_delete.html', {'admin_user': admin_user})


@user_passes_test(is_admin)
def admin_user_list(request):
    if not is_admin(request.user): 
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home') 
    admin_users = AdminUser.objects.all()
    return render(request, 'admin_user_list.html', {'admin_users': admin_users}) 
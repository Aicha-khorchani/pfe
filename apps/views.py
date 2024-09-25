from datetime import datetime
import os
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from requests import request
from rest_framework.decorators import api_view
from  saleManagment.settings import MEDIA_ROOT
from .models import  adddata, centreddata, customer, itemvariant, orderitem, salesorder, supplier
from .forms import customerDeleteForm, ItemDeleteForm, LoginForm, OrderDeleteForm, UpdatecustomerForm,DeleteLeadForm, UpdateLeadForm
from .forms import  UpdateorderitemForm, UpdatesalesorderForm, UpdateVariantForm, VariantDeleteForm, customuserCreationForm
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from decimal import Decimal, InvalidOperation




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
def allcustomers(request):
    customers = customer.objects.all()
    return render(request, 'allcustomers.html', {'customers': customers})

def all_leads(request):
    centred_datas = centreddata.objects.all()
    return render(request, 'all_leads.html', {'centreddatas': centred_datas})


def all_Details(request):
    adddatas = adddata.objects.all()
    return render(request, 'leaddetail.html', {'adddatas': adddatas})


def sales_order_view(request):
    orders = salesorder.objects.all()
    return render(request, 'orders.html',{'orders': orders})



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
    return render(request, 'custemers.html')


def search_orders(request):
    if request.method == "GET":
        searched = request.GET.get('searched', '')
        if searched:
            orders = salesorder.objects.filter(order_id__iexact=searched)
        else:
            orders = salesorder.objects.all()
        return render(request, 'search_order.html', {'searched': searched, 'orders': orders})
    else:
        return render(request, 'search_order.html', {})
    
    
  
def search_product(request):
    if request.method == "GET":
        searched = request.GET.get('searched', '')
        if searched:
            order_items = orderitem.objects.filter(product_name__icontains=searched)
        else:
            order_items = orderitem.objects.all()
        return render(request, 'search_product.html', {'order_items': order_items, 'searched': searched})
    else:
        return render(request, 'search_product.html', {})



def search_customers(request):
    if request.method == "GET":
        searched = request.GET.get('searched', '')
        customers = customer.objects.filter(customer_name__icontains=searched)
        return render(request, 'search_results.html', {'searched': searched, 'customers': customers})
    else:
        return render(request, 'search_results.html', {})
    


def search_lead(request):
     if request.method == 'GET':
        search = request.GET.get('search', '')
        leads = centreddata.objects.filter(id__icontains=search)
        return render(request, 'searchlead.html', {'leads': leads})
     else:
        return render(request, 'searchlead.html')
    

def updatelead(request, id):
    centreddata_instance = centreddata.objects.get(pk=id)
    if request.method == 'POST':
        form = UpdateLeadForm(request.POST, instance=centreddata_instance)
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
        form = UpdateLeadForm(instance=centreddata_instance)
    return render(request, 'updatelead.html', {'centreddata': centreddata_instance, 'form': form})



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


def update_sales_order(request, order_id):
    sales_order_instance = get_object_or_404(salesorder, order_id=order_id)
    if request.method == 'POST':
        form = UpdatesalesorderForm(request.POST or None, instance=sales_order_instance)
        if form.is_valid():
            print("Form is valid!")  # this line justfor test tw nfas5a ba3teli hoa w prints lkol
            form.save()
            return redirect('orders')
        else:
            print("Form is not valid!")  # ntesty beha w bra
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
    else:
        form = UpdatesalesorderForm(instance=sales_order_instance)
    return render(request, 'updateorder.html', {'sales_order': sales_order_instance, 'form': form})


def update_order_item(request, item_id):
    order_item_instance = get_object_or_404(orderitem, item_id=item_id)
    if request.method == 'POST':
        form = UpdateorderitemForm(request.POST or None, instance=order_item_instance)
        if form.is_valid():
            print("Form is valid!")  # this line justfor test tw nfas5a ba3teli hoa w prints lkol
            form.save()
            return redirect('products')
        else:
            print("Form is not valid!")  # ntesty beha w bra
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
    else:
        form = UpdateorderitemForm(instance=order_item_instance)
    return render(request, 'updateproduct.html', {'order_item': order_item_instance, 'form': form})


def update_item_variant(request, variant_id):
    try:
        variant_instance = itemvariant.objects.get(variant_id=variant_id)
    except itemvariant.DoesNotExist:
        raise Http404("Item Variant does not exist")

    if request.method == 'POST':
        form = UpdateVariantForm(request.POST or None, instance=variant_instance)
        if form.is_valid():
            print("Form is valid!")  # this line just for testing purposes w bara
            form.save()
            return redirect('products')
        else:
            print("Form is not valid!")  # ntesty beha w bra
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
    else:
        form = UpdateVariantForm(instance=variant_instance)

    return render(request, 'updatevariant.html', {'item_variant': variant_instance, 'form': form})





def add_sales_order(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        customer_instance = get_object_or_404(customer, pk=customer_id)
        order_date_str = request.POST.get('order_date')
        order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()
        total_amount = request.POST.get('total_amount')
        salesorder.objects.create(
            customer=customer_instance,
            order_date=order_date,
            total_amount=total_amount
        )
        return redirect('orders')
    return render(request, 'addorder.html')


def delete_lead(request):
        form = DeleteLeadForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            centreddata_id = form.cleaned_data['centreddata_id']
            lead = get_object_or_404(centreddata,pk=centreddata_id)
            lead.delete()
            return redirect('all_leads')
        return render(request, 'deletelead.html', {'form': form})
 



def customer_delete(request):
    form = customerDeleteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        customer_id = form.cleaned_data['customer_id']
        customer = get_object_or_404(customer, pk=customer_id)
        customer.delete()
        return redirect('allcustomers')
    return render(request, 'deletecustomer.html', {'form': form})




def order_delete(request):
    form = OrderDeleteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        order_id = form.cleaned_data['order_id']
        order = get_object_or_404(salesorder, pk=order_id)
        order.delete()
        return redirect('orders')
    return render(request, 'deleteorder.html', {'form': form})


def product_delete(request):
    form = ItemDeleteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item_id = form.cleaned_data['item_id']
        item = get_object_or_404(orderitem, pk=item_id)
        item.delete()
        return redirect('products')
    return render(request, 'deleteproduct.html', {'form': form})


def variant_delete(request):
    form = VariantDeleteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        variant_id = form.cleaned_data['variant_id']
        variant = get_object_or_404(itemvariant, pk=variant_id)
        variant.delete()
        return redirect('products')
    return render(request, 'deletevariant.html', {'form': form})


def add_orderitem(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        salesorder_instance = get_object_or_404(salesorder, pk=order_id)
        product_name = request.POST.get('product_name')
        quantity = request.POST.get('quantity')
        unit_price = request.POST.get('unit_price')
        total_price = request.POST.get('total_price')
        orderitem.objects.create(
            order=salesorder_instance,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price
        )
        return redirect('products')
    return render(request, 'addproduct.html')


def add_centred_data(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        contact_person = request.POST.get('contact_person')
        position = request.POST.get('position')
        contact = request.POST.get('contact')
        score = request.POST.get('score')
        description = request.POST.get('description')

        centreddata.objects.create(
            company_name=company_name,
            contact_person=contact_person,
            position=position,
            contact=contact,
            score=score,
            description=description,
        )

        return redirect('all_leads')

    return render(request, 'enterlead.html')



def add_data(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        owner = request.POST.get('owner')
        contract_file = request.FILES.get('contract_file')
        nextdate = request.POST.get('nextdate')
        revenue = request.POST.get('revenue')
        size = request.POST.get('size')
        number = request.POST.get('number')
        score = request.POST.get('score')
        worker = request.POST.get('worker')
        leadsrc = request.POST.get('leadsrc')
        sector = request.POST.get('sector')
        status = request.POST.get('status')
        note = request.POST.get('note')

        # Validate lead_id
        try:
            lead = centreddata.objects.get(pk=lead_id)
        except centreddata.DoesNotExist:
            return render(request, 'leadsview.html', {'error': 'Invalid lead ID'})

        # Validate revenue
        try:
            revenue = Decimal(revenue)
            if revenue <= 0:
                return render(request, 'leadsview.html', {'error': 'Revenue must be greater than 0'})
        except InvalidOperation:
            return render(request, 'leadsview.html', {'error': 'Invalid revenue format'})

        # Validate nextdate
        if not nextdate:
            return render(request, 'leadsview.html', {'error': 'Next date is required'})

        # Convert size and number to decimals if present
        try:
            size = Decimal(size) if size else None
            number = Decimal(number) if number else None
        except InvalidOperation:
            return render(request, 'leadsview.html', {'error': 'Invalid format for size or number'})

        # Create new record
        adddata.objects.create(
            lead=lead,
            owner=owner,
            contract_file=contract_file,
            nextdate=nextdate,
            revenue=revenue,
            size=size,
            number=number,
            score=score,
            worker=worker,
            leadsrc=leadsrc,
            sector=sector,
            status=status,
            note=note
        )

        return render(request, 'leadsview.html', {'success': 'Data added successfully'})
    
    return render(request, 'leadsview.html')





def add_itemvariant(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(orderitem, pk=item_id)
        variant_name= request.POST.get('variant_name')
        variant_value = request.POST.get('variant_value')
        itemvariant.objects.create(
            item_id=item,
            variant_name=variant_name,
            variant_value=variant_value,
        )
        return redirect('products')
    return render(request, 'addvariant.html')


def products(request):
    order_items = orderitem.objects.all()
    item_variants = itemvariant.objects.all()
    context = {
        'order_items': order_items,
        'item_variants': item_variants,
    }
    return render(request, 'products.html', context)


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


def home(request):
    return render(request,"home.html")

def leads(request):
    return render(request,"leads.html")

def update_password(request):
    return render(request, 'updatepassword.html')


def leadsview(request):
    return render(request, 'leadsview.html')

def add_supplier(request):
    if request.method == 'POST':
        # Retrieve POST data
        supplier_name = request.POST.get('supplier-name')
        contact_info = request.POST.get('supp-contact')
        address = request.POST.get('Address')
        categories_supplied = request.POST.get('Categorie')
        payment_terms = request.POST.get('Payment')
        product_quality = request.POST.get('product_q')
        cost = request.POST.get('Cost')
        interaction_quality = request.POST.get('interaction_q')
        feedback = request.POST.get('Feedback')

        # Convert fields to appropriate types if necessary
        try:
            product_quality = int(product_quality) if product_quality else None
            cost = int(cost) if cost else None
            interaction_quality = int(interaction_quality) if interaction_quality else None
        except ValueError:
            # Handle conversion error if necessary
            product_quality = cost = interaction_quality = None

        # Create supplier object
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

    return render(request, 'supplier.html')



def supplier_list(request):
    suppliers = supplier.objects.all()
    print(suppliers) 
    return render(request, 'supplier_list.html', {'suppliers': suppliers})

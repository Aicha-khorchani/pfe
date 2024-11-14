import decimal
import logging
from django.db import IntegrityError 
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.decorators import api_view
from .models import  Livreurs, Note, Stock, customuser, facture, leaddata, lead, customer, itemvariant, item, supplier,Notification , retour,bonreception ,AdminUser,Delivery,Command
from .forms import CustomUserChangeForm, DeleteSupplierForm, FactureForm, LivreurCreationForm, UpdateSupplierForm, customerDeleteForm, ItemDeleteForm, LoginForm, UpdatecustomerForm,DeleteLeadForm, UpdateLeadForm, itemForm
from .forms import  UpdateitemForm, UpdateItemVariant, VariantDeleteForm, customuserCreationForm ,RetourForm,RetourDeleteForm,BonReceptionForm,AdminUserCreationForm  
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import user_passes_test ,login_required







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
    suppliers = supplier.objects.all()  
    products = item.objects.all()
    variants = itemvariant.objects.all()

    return render(request, 'addreception.html', {'form': form,'suppliers': suppliers,'products': products,'variants': variants,})



def update_bonreception(request, delivery):
    bonreception_instance = get_object_or_404(bonreception, pk=delivery)
    if request.method == 'POST':
        print(request.POST)  
        form = BonReceptionForm(request.POST, instance=bonreception_instance)  
        
        if form.is_valid():
            updated_bonreception_instance = form.save()
            stock, created = Stock.objects.get_or_create(
                item=updated_bonreception_instance.item,
                item_variant=updated_bonreception_instance.variant
            )
            if created:
                stock.quantity_available = updated_bonreception_instance.quantity_delivered
            else:
                stock.quantity_available += (updated_bonreception_instance.quantity_delivered - bonreception_instance.quantity_delivered)
            stock.save()

            return redirect('all_bonreception') 
        else:
            print(form.errors)  

    else:
        form = BonReceptionForm(instance=bonreception_instance) 

    suppliers = supplier.objects.all()
    products = item.objects.all()
    variants = itemvariant.objects.all()

    return render(request, 'updatereception.html', {'form': form,'suppliers': suppliers,'products': products,'variants': variants,})


def all_bonreception(request):
    bonreceptions = bonreception.objects.all()
    return render(request, 'allreception.html', {'bonreceptions': bonreceptions})


def search_bonreception(request):
    if request.method == 'GET':
        searched = request.GET.get('searched', '')
        if searched:
            results = bonreception.objects.filter(
                Q(delivery_date__icontains=searched) |
                Q(delivery_address__icontains=searched) |
                Q(supplier_id__supplier_name__icontains=searched) |
                Q(item__product_name__icontains=searched) |
                Q(quantity_delivered__icontains=searched) |
                Q(unit_of_measure__icontains=searched) |
                Q(transportation_type__icontains=searched) |
                Q(variant__variant_name__icontains=searched)
            )
        else:
            results = bonreception.objects.all()
        return render(request, 'search_bonreception.html', {'results': results, 'searched': searched})
    else:
        return render(request, 'search_bonreception.html', {})




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
            if created:
                stock.quantity_available = retour.quantite_retournee
            else:
                stock.quantity_available += retour.quantite_retournee
            stock.save()
              #zdt partie hethy 3 ligne bch notomatizi stock ba9i ken i5dm cv 
            return redirect('all_retour')
        else:
          print(form.errors)
          print(request.POST)
        
    else:
        form = RetourForm()
        
    clients = customer.objects.all()  
    suppliers = supplier.objects.all()  
    produits = item.objects.all()  
    variants = itemvariant.objects.all()  
    livreurs = Livreurs.objects.all() 
    numero_cs = Command.objects.all()
    
    return render(request, 'addretour.html', {'form': form,'clients': clients,'suppliers': suppliers,'produits': produits,'variants': variants,'livreurs': livreurs,'numero_cs': numero_cs,})











def update_retour(request, retour_id):
    retour_instance = get_object_or_404(retour, pk=retour_id)
    old_quantite_retournee = retour_instance.quantite_retournee 
    
    if request.method == 'POST':
        form = RetourForm(request.POST, instance=retour_instance)
        if form.is_valid():
            new_retour_instance = form.save(commit=False)
            new_quantite_retournee = new_retour_instance.quantite_retournee 

            stock_instance = Stock.objects.get(item=new_retour_instance.produit, item_variant=new_retour_instance.variant)

            difference = new_quantite_retournee - old_quantite_retournee

            if difference > 0:
                stock_instance.quantity_available += difference
            elif difference < 0:
                stock_instance.quantity_available += difference  
            
            stock_instance.save()

            new_retour_instance.save()

            return redirect('all_retour')
    else:
        form = RetourForm(instance=retour_instance)
        
        clients = customer.objects.all()  
        suppliers = supplier.objects.all()  
        produits = item.objects.all()  
        variants = itemvariant.objects.all()  
        livreurs = Delivery.objects.all() 
        numero_cs = Command.objects.all()

    return render(request, 'updateretour.html', {
        'form': form,
        'clients': clients,
        'suppliers': suppliers,
        'produits': produits,
        'variants': variants,
        'livreurs': livreurs,
        'numero_cs': numero_cs,
    })







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
        searched = request.GET.get('searched', '')
        if searched:
            retours = retour.objects.filter(
                Q(supplier__supplier_name__icontains=searched) |
                Q(client__customer_name__icontains=searched) |
                Q(produit__product_name__icontains=searched) |
                Q(variant__variant_name__icontains=searched) |
                Q(quantite_retournee__icontains=searched) |
                Q(raison_retour__icontains=searched) |
                Q(date_retour__icontains=searched) |
                Q(livreur__icontains=searched) |
                Q(informations_supp__icontains=searched) |
                Q(numero_c__icontains=searched) |
                Q(statut_retour__icontains=searched)
            )
        else:
            retours = retour.objects.all()
        return render(request, 'search_return.html', {'retours': retours, 'searched': searched})
    else:
        return render(request, 'search_return.html', {})
    
                      


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


def search_itemvariant(request):
    if request.method == "GET":
        search2 = request.GET.get('search2', '')
        if search2:
            query = Q(variant_name__icontains=search2) | \
                    Q(variant_value__icontains=search2) | \
                    Q(item__product_name__icontains=search2)
            itemvariants = itemvariant.objects.filter(query)
        else:
            itemvariants = itemvariant.objects.all()
        return render(request, 'search_itemvariant.html', {'itemvariants': itemvariants, 'search2': search2})
    else:
        return render(request, 'search_itemvariant.html', {})


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
        facture_id = request.POST.get('facture_id')  
        try:
            fact = get_object_or_404(facture, pk=facture_id)  
            fact.delete()  
            return redirect('get_all_factures')  
        except facture.DoesNotExist:
            return render(request, 'deletefacture.html', {'error': 'Facture ID does not exist'})  
    return render(request, 'deletefacture.html')  
   
   









def update_facture(request, facture_id):
    # Retrieve the facture object from the database
    fact = get_object_or_404(facture, pk=facture_id)
    # Get the current stock for the item and variant
    current_stock = Stock.objects.get(item=fact.product, item_variant=fact.variant)
    
    # Print the current stock level for debugging
    print(f"Current Stock: {current_stock.quantity_available}")

    # Store the old quantity before any changes
    old_quantity = fact.qte_facture

    if request.method == 'POST':
        form = FactureForm(request.POST, instance=fact)

        if form.is_valid():
            # Get the new quantity from the form data
            new_quantity = form.cleaned_data['qte_facture']

            # Calculate the difference between the new and old quantities
            quantity_difference = new_quantity - old_quantity

            # Print debugging information
            print(f"Old Quantity: {old_quantity}, New Quantity: {new_quantity}")
            print(f"Quantity Difference: {quantity_difference}")

            if quantity_difference > 0:
                # Reducing stock since more quantity is being invoiced
                if current_stock.quantity_available < quantity_difference:
                    print("Not enough stock available")
                    return render(request, 'updatefacture.html', {
                        'form': form,
                        'error': 'Not enough stock available for the updated quantity.'
                    })
                current_stock.quantity_available -= quantity_difference
            elif quantity_difference < 0:
                # Returning stock since less quantity is being invoiced
                current_stock.quantity_available += abs(quantity_difference)

            # Print the updated stock level for debugging
            print(f"New Stock Level: {current_stock.quantity_available}")
            
            # Save the updated stock level
            current_stock.save()
            # Save the updated facture data
            form.save()

            # Redirect to the list of all factures after successful update
            return redirect('get_all_factures')
        else:
            # Print form errors for debugging
            print(form.errors)
    else:
        form = FactureForm(instance=fact)

    # Fetch all necessary data for dropdown lists
    products = item.objects.all()
    variants = itemvariant.objects.all()
    customers = customer.objects.all()
    commands = Command.objects.all()

    return render(request, 'updatefacture.html', {
        'form': form,
        'products': products,
        'variants': variants,
        'current_stock': current_stock,
        'commands': commands,
        'customers': customers
    })























def get_all_factures(request):
    factures = facture.objects.all()
    return render(request, 'allfacture.html', {'factures': factures})



def search_facture(request):
    if request.method == 'GET':
        searched = request.GET.get('searched', '')
        if searched:
            factures = facture.objects.filter(
                Q(datef__icontains=searched) |
                Q(addressf__icontains=searched) |
                Q(tax__icontains=searched) |
                Q(discount__icontains=searched) |
                Q(payment_method__icontains=searched) |
                Q(qte_facture__icontains=searched) |
                Q(ttc__icontains=searched) |
                Q(product__product_name__icontains=searched) |
                Q(price__icontains=searched) |
                Q(variant__variant_name__icontains=searched) |
                Q(customer__customer_name__icontains=searched)
            )
        else:
            factures = facture.objects.all()
        return render(request, 'search_facture.html', {'factures': factures, 'searched': searched})
    else:
        return render(request, 'search_facture.html', {})
        
    
    
def add_facture(request):
    if request.method == 'POST':
        print("POST Data:", request.POST)  
        datef = request.POST.get('datef')
        customer_id = request.POST.get('customer_id')
        command = request.POST.get('command')
        addressf = request.POST.get('addressf')
        product = request.POST.get('item')
        tax = request.POST.get('tax')
        discount = request.POST.get('discount')
        payment_method = request.POST.get('Payment_Method')
        variant = request.POST.get('variant')
        qte_facture = request.POST.get('qte_facture')
        ttc = request.POST.get('TTC')
        price = request.POST.get('price')

        try:
            customer_obj = customer.objects.get(pk=customer_id)
            product_obj = item.objects.get(pk=product)
            variant_obj = itemvariant.objects.get(pk=variant)
            command_obj = Command.objects.get(pk=command)
        except (customer.DoesNotExist, item.DoesNotExist, itemvariant.DoesNotExist, Command.DoesNotExist):
            return render(request, 'addfacture.html', {
                'error': 'Invalid customer, product, variant, or command provided.'
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
            command=command_obj,
        )
        facture_obj.save()
        stock, created = Stock.objects.get_or_create(item=product_obj, item_variant=variant_obj)
        if created:
            stock.quantity_available = 0  
        if stock.quantity_available < decimal.Decimal(qte_facture):
            return render(request, 'addfacture.html', {
                'error': 'Not enough stock available for this quantity.'
            })
        else:
            stock.quantity_available -= decimal.Decimal(qte_facture)
            stock.save()

        return redirect('get_all_factures')  
    else:
        customers = customer.objects.all()
        commands = Command.objects.all()
        products = item.objects.all()
        variants = itemvariant.objects.all()

        return render(request, 'addfacture.html', {'customers': customers,'commands': commands,'products': products,'variants': variants,})


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

def search_leaddata(request):
    if request.method == 'GET':
        searched = request.GET.get('searched', '')
        if searched:
            results = leaddata.objects.filter(
                Q(lead__icontains=searched) |
                Q(owner__icontains=searched) |
                Q(nextdate__icontains=searched) |
                Q(revenue__icontains=searched) |
                Q(size__icontains=searched) |
                Q(number__icontains=searched) |
                Q(score__icontains=searched) |
                Q(worker__icontains=searched) |
                Q(leadsrc__icontains=searched) |
                Q(sector__icontains=searched) |
                Q(status__icontains=searched) |
                Q(note__icontains=searched)
            )
        else:
            results = leaddata.objects.all()
        return render(request, 'searchleaddata.html', {'results': results, 'searched': searched})
    else:
        return render(request, 'searchleaddata.html', {})


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
        contract_file = request.FILES.get('contract_file')
        revenue = request.POST.get('revenue', '0')
        owner = request.POST.get('owner')
        nextdate = request.POST.get('nextdate')
        size = request.POST.get('size')
        number = request.POST.get('number')
        worker = request.POST.get('worker')
        leadsrc = request.POST.get('leadsrc')
        sector = request.POST.get('sector')

        if not lead_id or not score or not status:
            print("Missing required fields")
            return render(request, 'addleaddata.html', {'error': 'Lead ID, Score, and Status are required'})

        try:
            lead_instance = lead.objects.get(pk=lead_id)
            print("Lead found:", lead_instance)
        except lead.DoesNotExist:
            print("Lead ID does not exist")
            return render(request, 'addleaddata.html', {'error': 'Invalid lead ID'})

        try:
            revenue = Decimal(revenue)
            if revenue < 0:
                print("Revenue is negative")
                return render(request, 'addleaddata.html', {'error': 'Revenue must be greater than or equal to 0'})
        except InvalidOperation:
            print("Invalid revenue format")
            return render(request, 'addleaddata.html', {'error': 'Invalid revenue format'})

        # Validate size
        try:
            size = Decimal(size) if size else Decimal('0')
        except InvalidOperation:
            print("Invalid size format")
            return render(request, 'addleaddata.html', {'error': 'Invalid size format'})

        # Validate number
        try:
            number = Decimal(number) if number else Decimal('0')
        except InvalidOperation:
            print("Invalid number format")
            return render(request, 'addleaddata.html', {'error': 'Invalid number format'})

        try:
            new_data = leaddata.objects.create(
                lead=lead_instance,
                score=score,
                status=status,
                contract_file=contract_file,
                revenue=revenue,
                owner=owner,
                nextdate=nextdate,
                size=size,
                number=number,
                worker=worker,
                leadsrc=leadsrc,
                sector=sector
            )
            print("Data created successfully:", new_data)
        except Exception as e:
            print("Error saving data:", e)
            return render(request, 'addleaddata.html', {'error': 'An error occurred while saving data'})

        return redirect('all_Details')
    
    
    customusers = customuser.objects.filter(user_type='customuser')
    return render(request, 'addleaddata.html', {'customusers': customusers})



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
    
    items = item.objects.all()  

    return render(request, 'addvariant.html', {'items': items,})






def doc(request):
    return render(request,"doc.html")

def invoice(request):
    return render(request,"invoice.html")

def returne(request):
    return render(request,"returne.html")

def reception(request):
    return render(request,"reception.html")

def home(request):
    unread_count = Notification.objects.filter(is_read=False).count()
    unread_notifications = Notification.objects.filter(is_read=False)
    print(f"Unread Count: {unread_count}")  # Debugging line
    print(f"Unread Notifications: {unread_notifications}")  # Debugging line
    context = {'unread_count': unread_count,'unread_notifications': unread_notifications,}
    
    return render(request,"home.html", context)

def livreur(request):
    return render(request,"livreur.html")

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
    item_instance = get_object_or_404(item, pk=item_id)
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
        form = UpdateitemForm(request.POST, instance=item_instance)
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

def add_delivery(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        contact_info = request.POST.get('contact_info')
        delivery_person_id = request.POST.get('delivery_person')  
        
        if not delivery_person_id:
            return render(request, 'add_delivery.html', {
                'error': 'You must select a delivery person.',
                'Livreurss': Livreurs.objects.all()
            })
        
        try:
            delivery_person_instance = Livreurs.objects.get(id=delivery_person_id)
        except Livreurs.DoesNotExist:
            return render(request, 'add_delivery.html', {
                'error': 'Selected delivery person does not exist',
                'Livreurss': Livreurs.objects.all()
            })
        
        delivery_person_number = request.POST.get('delivery_person_number')

        delivery = Delivery(
            company_name=company_name,
            contact_info=contact_info,
            delivery_person=delivery_person_instance,
            delivery_person_number=delivery_person_number
        )
        delivery.save()
        return redirect('get_delivery')  

    Livreurss = Livreurs.objects.all()
    return render(request, 'add_delivery.html', {'Livreurss': Livreurss})


def delete_delivery(request, delivery_id):
    try:
        delivery = Delivery.objects.get(delivery_id=delivery_id)
        delivery.delete()
        return redirect('get_delivery')
    except Delivery.DoesNotExist:
        return render(request, 'delivery_not_found.html', {'delivery_id': delivery_id})



def delete_command(request, Command_id):
    try:
        command = Command.objects.get(Command_id=Command_id)
        command.delete()
        return redirect('get_command')
    except Command.DoesNotExist:
        return redirect(request,'get_command', {'Command_id': Command_id})


def update_delivery(request, delivery_id):
    delivery = Delivery.objects.get(delivery_id=delivery_id)
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        contact_info = request.POST.get('contact_info')
        delivery_person = request.POST.get('delivery_person')
        delivery_person_number = request.POST.get('delivery_person_number')

        delivery.company_name = company_name
        delivery.contact_info = contact_info
        delivery.delivery_person = delivery_person
        delivery.delivery_person_number = delivery_person_number
        delivery.save()
        return redirect('get_delivery')  
    return render(request, 'update_delivery.html', {'delivery': delivery})


def search_delivery(request):
    if request.method == 'GET':
        searched = request.GET.get('searched', '')
        if searched:
            deliveries = Delivery.objects.filter(
                Q(company_name__icontains=searched) |
                Q(contact_info__icontains=searched) |
                Q(delivery_person__icontains=searched) |
                Q(delivery_person_number__icontains=searched)
            )
        else:
            deliveries = Delivery.objects.all()
        return render(request, 'search_delivery.html', {'deliveries': deliveries, 'searched': searched})
    else:
        return render(request, 'search_delivery.html', {})


def add_command(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')  
        delivery_id = request.POST.get('delivery_id')
        print(f"Customer ID: {customer_id}, Delivery ID: {delivery_id}") 

        order_date = request.POST.get('order_date')
        total_amount = request.POST.get('total_amount')
        statu = request.POST.get('statu')
        shipping_address = request.POST.get('shipping_address')

        try:
            customer_instance = customer.objects.get(customer=customer_id)  
            delivery_instance = Delivery.objects.get(delivery_id=delivery_id)

            command = Command(
                customer=customer_instance,  
                order_date=order_date,
                total_amount=total_amount,
                statu=statu,
                shipping_address=shipping_address,
                delivery_id=delivery_instance.delivery_id
            )
            command.save()
            return redirect('get_command')

        except customer.DoesNotExist:
            print("Customer does not exist")
            return render(request, 'add_command.html', {
                'error_message': "Customer does not exist", 
                'customers': customer.objects.all(),
                'deliveries': Delivery.objects.all()
            })
            
        except Delivery.DoesNotExist:
            print("Delivery person does not exist")
            return render(request, 'add_command.html', {
                'error_message': "Delivery person does not exist", 
                'customers': customer.objects.all(),
                'deliveries': Delivery.objects.all()
            })

        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return render(request, 'add_command.html', {
                'error_message': "Failed to add command", 
                'customers': customer.objects.all(),
                'deliveries': Delivery.objects.all()
            })

    else:
        customers = customer.objects.all()  
        deliveries = Delivery.objects.all()
    return render(request, 'add_command.html', {'customers': customers , 'deliveries': deliveries })


def get_command(request):
    commands = Command.objects.all()
    return render(request, 'command_detail.html', {'commands': commands})


def get_delivery(request):
    deliveris = Delivery.objects.all()
    return render(request, 'delivery_detail.html', {'deliveris': deliveris})


def update_command(request, pk):
    command = get_object_or_404(Command, pk=pk)  
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        order_date = request.POST.get('order_date')
        total_amount = request.POST.get('total_amount')
        statu = request.POST.get('statu')
        shipping_address = request.POST.get('shipping_address')
        delivery_id = request.POST.get('delivery_id')

        try:
            command.customer = customer.objects.get(customer=customer_id) 
            command.order_date = order_date
            command.total_amount = total_amount
            command.statu = statu
            command.shipping_address = shipping_address
            command.delivery_id = Delivery.objects.get(delivery_id=delivery_id).delivery_id 

            command.save()  
            return redirect('get_command')

        except customer.DoesNotExist:
            print("Customer does not exist")
            return render(request, 'update_command.html', {
                'command': command,
                'error_message': "Customer does not exist"
            })

        except Delivery.DoesNotExist:
            print("Delivery person does not exist")
            return render(request, 'update_command.html', {
                'command': command,
                'error_message': "Delivery person does not exist"
            })

        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return render(request, 'update_command.html', {
                'command': command,
                'error_message': "Failed to update command"
            })

    return render(request, 'update_command.html', { 'command': command, 'customers': customer.objects.all(),'deliveries': Delivery.objects.all()})


def search_command(request):
    if request.method == 'GET':
        searched = request.GET.get('searched', '')
        if searched:
            commands = Command.objects.filter(
                Q(customer__customer_name__icontains=searched) |
                Q(order_date__icontains=searched) |
                Q(total_amount__icontains=searched) |
                Q(statu__icontains=searched) |
                Q(shipping_address__icontains=searched) |
                Q(delivery__company_name__icontains=searched)
            )
        else:
            commands = Command.objects.all()
        return render(request, 'search_command.html', {'commands': commands, 'searched': searched})
    else:
        return render(request, 'search_command.html', {})








def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                print(f"Authenticated user: {user.username}, user type: {user.user_type}")
                login(request, user)
                
                if user.user_type == 'livreur':
                    print("Redirecting to livreur page")
                    return redirect('livreur')  # Redirect to Livreurs page
                elif user.user_type == 'admin':
                    print("Redirecting to admin page")
                    return redirect('admin')  # Redirect to Admin page
                else:
                    print("Redirecting to home page")
                    return redirect('home')  # Default for CustomUser
            else:
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
    print(f"User: {request.user}, Is Admin: {is_admin(request.user)}") 
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
            user.user_type = 'customuser'
            user.set_password(form.cleaned_data['password1'])  
            user.save() 
            messages.success(request, "User  created successfully!")
            return redirect('user_list')  
    else:
        form = customuserCreationForm()

    return render(request, 'createuser.html', {'form': form})



@user_passes_test(is_admin)
def admin_user_create(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            admin_user = form.save(commit=False)
            admin_user.user_type = 'admin'
            admin_user.set_password(form.cleaned_data['password1'])
            admin_user.save()
            messages.success(request, "Admin user created successfully.")
            return redirect('admin_user_list') 
    else:
        form = AdminUserCreationForm()
    return render(request, 'createadmin.html', {'form': form})



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


@user_passes_test(is_admin)
def livreur_create_view(request):
    if request.method == 'POST':
        form = LivreurCreationForm(request.POST)
        if form.is_valid():
            livreur = form.save(commit=False)
            livreur.user_type = 'livreur' 
            livreur.set_password(form.cleaned_data['password1'])
            livreur.save()
            messages.success(request, "Livreur created successfully!")
            return redirect('user_list')  
    else:
        form = LivreurCreationForm()

    return render(request, 'create_livreur.html', {'form': form})


        
def add_note(request):
    customers = customer.objects.all()
    commands = Command.objects.all()

    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        command_id = request.POST.get('command')
        note_text = request.POST.get('note')

        customer_instance = get_object_or_404(customer, pk=customer_id)
        command_instance = get_object_or_404(Command, pk=command_id)

        Note.objects.create(customer=customer_instance, command=command_instance, note=note_text)

        return redirect('all_notes')  

    return render(request, 'addnote.html', {'customers': customers, 'commands': commands})

def all_notes(request):
    notes = Note.objects.all()
    return render(request, 'all_notes.html', {'notes': notes})


def edit_note(request, note_id):
    note = get_object_or_404(Note, pk=note_id) 
    customers = customer.objects.all()
    commands = Command.objects.all()

    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        command_id = request.POST.get('command')
        note_text = request.POST.get('note')

        customer = get_object_or_404(customer, pk=customer_id)
        command = get_object_or_404(Command, pk=command_id)

        note.customer = customer
        note.command = command
        note.note = note_text
        note.save()

        return redirect('all_notes') 

    return render(request, 'edit_note.html', {'note': note,'customers': customers,'commands': commands,})
    
    
def delete_note(request, note_id):
    try:
        note = Note.objects.get(id=note_id) 
        note.delete()
        return redirect('all_notes')  
    except Note.DoesNotExist:
        return redirect(request,'all_notes', {'note_id': note_id})
            



def search_note(request):
    if request.method == "GET":
        search_query = request.GET.get('search_query', '')
        if search_query:
            query = Q(customer__customer_name__icontains=search_query) | \
                    Q(command__pk__icontains=search_query) | \
                    Q(note__icontains=search_query)
            notes = Note.objects.filter(query)
        else:
            notes = Note.objects.all()
        return render(request, 'search_note.html', {'notes': notes, 'search_query': search_query})
    else:
        return render(request, 'search_note.html', {})
    
    
    

@login_required
def notification_list(request):
    notifications = request.user.notifications.filter(is_read=False)
    unread_count = notifications.count()  
    return render(request, 'home.html', {'unread_count': unread_count,'unread_notifications': notifications})

def notification_view(request):
    notifications = Notification.objects.all()
    return render(request, 'notification_page.html', {'notifications': notifications})


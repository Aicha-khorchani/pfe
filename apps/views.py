import decimal
import json
from django.http import JsonResponse
from django.db import transaction 
import logging
from django.db import IntegrityError 
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.decorators import api_view
from .models import  Livreurs, Note, Stock, customuser,CommandLine, facture, leaddata, lead, customer, itemvariant, item, supplier,Notification , retour,bonreception ,AdminUser,Delivery,Command
from .forms import CommandForm,CommandLineFormSet, CustomUserChangeForm, DeleteSupplierForm, FactureForm, LivreurCreationForm, UpdateSupplierForm, customerDeleteForm, ItemDeleteForm, LoginForm, UpdatecustomerForm,DeleteLeadForm, UpdateLeadForm, itemForm
from .forms import  UpdateitemForm, UpdateItemVariant, VariantDeleteForm, customuserCreationForm ,RetourForm,RetourDeleteForm,BonReceptionForm,AdminUserCreationForm , BonReceptionLineFormSet  
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import user_passes_test ,login_required
from django.db.models import Prefetch
import traceback
import re








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
        print("POST Data:", request.POST)
        form = BonReceptionForm(request.POST)
        formset = BonReceptionLineFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():  # Ensure atomicity
                    bon_reception = form.save()
                    print("Form is valid, bon_reception saved:", bon_reception)

                    for form_line in formset:
                        if form_line.cleaned_data:
                            line = form_line.save(commit=False)

                            # Parse `variant_combination` from JSON string
                            variant_combination_str = form_line.cleaned_data.get('variant_combination', '{}')
                            variants = json.loads(variant_combination_str) if isinstance(variant_combination_str, str) else variant_combination_str

                            # Validate the variant combination against itemvariant
                            item_instance = line.item
                            for variant_name, variant_value in variants.items():
                                try:
                                    variant = itemvariant.objects.get(
                                        item=item_instance,
                                        variant_name=variant_name,
                                        variant_values__contains=[variant_value]
                                    )
                                except itemvariant.DoesNotExist:
                                    raise ValueError(f"Invalid variant combination: {variant_name} = {variant_value} for item {item_instance.product_name}")

                            # Save the line with bon_reception reference
                            line.bon_reception = bon_reception
                            line.variant_combination = variants
                            line.save()

                            # Update or create stock for this item-variant combination
                            stock, created = Stock.objects.get_or_create(
                                item=line.item,
                                item_variant=variant,  # The validated variant from itemvariant
                                variant_combination=variants,
                                defaults={'quantity_available': 0}
                            )

                            # Add the line's quantity to the stock
                            line_quantity = form_line.cleaned_data.get('quantity')  # Now this is an integer
                            stock.quantity_available += line_quantity
                            stock.save()

                    print("All lines and stock updated successfully.")
                    return redirect('all_bonreception')

            except Exception as e:
                print(f"An error occurred: {e}")
                form.add_error(None, "An unexpected error occurred. Please try again.")
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)
    else:
        form = BonReceptionForm()
        formset = BonReceptionLineFormSet()

    suppliers = supplier.objects.all()
    items_queryset = item.objects.prefetch_related(
        Prefetch(
            'itemvariant_set',
            queryset=itemvariant.objects.all()
        )
    )

    # Prepare dynamic variant data for the frontend
    variant_data = {}
    for item_obj in items_queryset:
        variant_data[item_obj.pk] = {
            variant.variant_name: variant.variant_values
            for variant in item_obj.itemvariant_set.all()
        }

    return render(request, 'addreception.html', {
        'form': form,
        'formset': formset,
        'suppliers': suppliers,
        'items': items_queryset,
        'variant_data': json.dumps(variant_data),
    })









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

    return render(request, 'updatereception.html', {'form': form,'suppliers': suppliers,'products': products,'variants': variants})


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




from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
import json

def add_retour(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Debug incoming POST data
                print("===== POST DATA =====")
                print(request.POST)
                print("=====================")

                # Extract data from POST request
                facture_id = request.POST.get('facture')
                selected_commands = request.POST.get('selected_commands', '[]')
                supplier_id = request.POST.get('supplier')
                raison_retour = request.POST.get('raison_retour')
                date_retour = request.POST.get('date_retour')
                livreur_id = request.POST.get('livreur')
                informations_supp = request.POST.get('informations_supp')

                # Ensure selected_commands is parsed correctly
                try:
                    selected_commands = json.loads(selected_commands)
                    if isinstance(selected_commands, int):  # Single command case
                        selected_commands = [selected_commands]
                    elif not isinstance(selected_commands, list):  # Invalid data
                        raise ValueError("Invalid selected_commands format")
                except json.JSONDecodeError:
                    raise ValueError("Failed to parse selected_commands")

                # Debug extracted data
                print(f"Facture ID: {facture_id}")
                print(f"Selected Commands: {selected_commands}")
                print(f"Supplier ID: {supplier_id}")
                print(f"Reason for Return: {raison_retour}")
                print(f"Return Date: {date_retour}")
                print(f"Livreur ID: {livreur_id}")
                print(f"Additional Information: {informations_supp}")

                # Validate and retrieve associated objects
                facture_instance = get_object_or_404(facture, pk=facture_id)
                supplier_instance = get_object_or_404(supplier, pk=supplier_id)
                livreur_instance = get_object_or_404(Livreurs, pk=livreur_id)

                # Debug validated objects
                print(f"Facture Instance: {facture_instance}")
                print(f"Supplier Instance: {supplier_instance}")
                print(f"Livreur Instance: {livreur_instance}")

                # Create the Retour instance
                retour_instance = retour.objects.create(
                    facture=facture_instance,
                    supplier=supplier_instance,
                    raison_retour=raison_retour,
                    date_retour=date_retour,
                    livreur=livreur_instance,
                    informations_supp=informations_supp,
                )
                print(f"Retour Instance Created: {retour_instance}")

                # Loop through selected commands to process stock updates
                for command_id in selected_commands:
                    print(f"Processing Command ID: {command_id}")
                    command = get_object_or_404(Command, pk=command_id)

                    for line in command.lines.all():
                        product = line.product
                        variant_combination = line.variant_combination
                        quantity = line.quantity

                        # Debug command line details
                        print(f"Command Line - Product: {product}, Variant Combination: {variant_combination}, Quantity: {quantity}")

                        # Update stock
                        stock, created = Stock.objects.get_or_create(
                            item=product,
                            variant_combination=variant_combination
                        )
                        if created:
                            stock.quantity_available = quantity
                            print(f"New Stock Created: {stock}")
                        else:
                            stock.quantity_available += quantity
                            print(f"Updated Stock: {stock}")

                        stock.save()
                        print(f"Stock Saved: {stock}")

                print("Retour Process Completed Successfully")
                return redirect('all_retour')  # Redirect to the page listing all returns

        except ValueError as e:
            print(f"Validation Error: {str(e)}")
            return JsonResponse({"success": False, "message": str(e)}, status=400)

        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    # For GET request, prepare data for the form
    factures = facture.objects.all()  # Fetch all factures
    livreurs = Livreurs.objects.filter(user_type='livreur')  # Fetch only delivery persons
    suppliers = supplier.objects.all()  # Fetch all suppliers

    # Debug data being sent to the template
    print("Rendering Add Retour Form")
    print(f"Factures: {factures}")
    print(f"Livreurs: {livreurs}")
    print(f"Suppliers: {suppliers}")

    return render(request, 'addretour.html', {
        'factures': factures,
        'livreurs': livreurs,
        'suppliers': suppliers,
    })





def get_commands(request, facture_id):
    try:
        # Get the facture and its associated commands
        selected_facture = facture.objects.get(pk=facture_id)
        commands = selected_facture.commands.all()
        
        # Prepare the data for the response
        command_data = [
            {"id": command.id, "description": f"Command {command.id} - {command.shipping_address}"}
            for command in commands
        ]
        
        return JsonResponse({"success": True, "commands": command_data})
    except facture.DoesNotExist:
        return JsonResponse({"success": False, "message": "Facture not found."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)










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
    stocks = Stock.objects.select_related('item', 'item_variant').all()
    stock_data = []

    for stock in stocks:
        item_name = stock.item.product_name
        variant_combination = stock.variant_combination  # This is already a dictionary
        quantity = stock.quantity_available  # This is now an integer

        # Prepare the stock entry
        stock_entry = {
            "item": item_name,
            "variant_combination": variant_combination,
            "quantity": quantity,
        }
        stock_data.append(stock_entry)

    return render(request, 'allstock.html', {'stocks': stock_data})





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
                    Q(variant_values__icontains=search2) | \
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
    if request.method == "GET":
        try:
            # Fetch the facture instance
            facture_instance = get_object_or_404(facture, pk=facture_id)

            # Fetch all customers
            customers = customer.objects.all()
            print("Customers Fetched:", customers)  # Debugging

            # Fetch related commands for the facture's customer
            commands = Command.objects.filter(customer=facture_instance.customer)
            print("Commands Fetched for Customer:", commands)  # Debugging

            # Fetch selected commands associated with this facture
            selected_command_ids = list(facture_instance.commands.values_list('id', flat=True))
            print("Selected Commands for Facture:", selected_command_ids)  # Debugging

            # Pass the data to the response
            return JsonResponse({
                "success": True,
                "facture": {
                    "id": facture_instance.facture_id,
                    "customer": facture_instance.customer.customer,  # Selected customer ID
                    "selected_commands": selected_command_ids,  # Pre-selected commands
                },
                "customers": list(customers.values("customer", "customer_name")),  # Include customer data
                "commands": [{"id": cmd.id, "label": str(cmd)} for cmd in commands],  # Use __str__() for label
            })
        except Exception as e:
            print("Error rendering update facture form:", e)
            return JsonResponse({"success": False, "message": "An unexpected error occurred while rendering the form."})




    
    
    
def get_variants(request, item):
    variants = itemvariant.objects.filter(item_id=item).values('id', 'variant_values')
    return JsonResponse({"variants": list(variants)})























def get_all_factures(request):
    factures = facture.objects.prefetch_related(
        'commands__lines'  
    ).all()
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
        
    
    
    
def process_commands_and_calculate_total(commands, customer_type):
    """
    Process selected commands, validate stock, deduct quantities, 
    and calculate the total amount for the facture.
    """
    total_amount = Decimal(0)
    processed_commands = []

    for command in commands:
        # Validate the command object
        if not isinstance(command.variant_combination, list):
            raise ValueError(f"Invalid variant_combination format for command {command.pk}")

        # Process variant combinations for the command
        for variant_data in command.variant_combination:
            variants = variant_data.get("variant_combination")
            quantity = variant_data.get("quantity")

            if not variants or not quantity:
                raise ValueError(f"Missing data in variant_combination for command {command.pk}")

            # Find matching stock
            stock = Stock.objects.filter(
                item_id=command.item_id,
                variant_combination=variants
            ).first()

            if not stock or stock.quantity_available < quantity:
                raise ValueError(f"Insufficient stock for {variants} in command {command.pk}")

            # Deduct stock
            stock.quantity_available -= quantity
            stock.save()

        # Calculate price based on customer type
        price = command.item.volume_price if customer_type == "volume" else command.item.unit_price
        total_amount += quantity * price

        # Add the processed command to the list
        processed_commands.append(command)

    return total_amount, processed_commands
    
    
    
    
def add_facture(request):
    if request.method == "POST":
        try:
            # Extract data from the POST request
            data = request.POST.copy()
            customer_id = data.get("customer_id")
            selected_command_ids = data.getlist("command")

            # Validate required fields
            if not customer_id or not selected_command_ids:
                return JsonResponse({"success": False, "message": "Customer and commands are required."})

            # Get the customer instance
            customer_instance = get_object_or_404(customer, pk=customer_id)

            # Fetch the selected commands
            selected_commands = Command.objects.filter(pk__in=selected_command_ids)

            # Create a new facture
            with transaction.atomic():
                new_facture = facture.objects.create(
                    datef=data.get("datef"),
                    addressf=data.get("addressf"),
                    payment_method=data.get("Payment_Method"),
                    tax=data.get("tax", 0),
                    discount=data.get("discount", 0),
                    ttc=data.get("TTC", 0),
                    customer=customer_instance,
                )

                # Associate commands with the facture
                new_facture.commands.set(selected_commands)

            return redirect("get_all_factures")

        except Exception as e:
            print("Error creating facture:", e)
            return JsonResponse({"success": False, "message": "An unexpected error occurred."})

    elif request.method == "GET" and "customer_id" in request.GET:
        # Fetch commands dynamically for a specific customer
        customer_id = request.GET.get("customer_id")
        try:
            commands = Command.objects.filter(customer_id=customer_id)
            commands_data = [{"id": cmd.pk, "label": f"Command {cmd.pk}"} for cmd in commands]
            return JsonResponse({"success": True, "commands": commands_data})
        except Exception as e:
            print("Error fetching commands:", e)
            return JsonResponse({"success": False, "message": str(e)})

    else:
        # Render the form for adding a facture
        customers = customer.objects.all()
        return render(request, "add_facture.html", {
            "form": FactureForm(),
            "customers": customers,
        })





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
        variant_values_raw = request.POST.get('variant_values')
        variant_values = [value.strip() for value in variant_values_raw.split(',') if value.strip()]
        itemvariant.objects.create(
            item =item_instance,
            variant_name=variant_name,
            variant_values=variant_values,
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






from django.http import JsonResponse

def add_command(request):
    if request.method == "POST":
        try:
            data = request.POST.copy()
            variant_combinations = json.loads(data.get("variant_combinations", "[]"))

            # Create Command
            command = Command.objects.create(
                customer_id=data["customer_id"],
                delivery_id=data["delivery_id"],
                order_date=data["order_date"],
                shipping_address=data["shipping_address"],
                total_amount=0
            )

            # Add Command Lines
            total_amount = 0
            for combination in variant_combinations:
                product = item.objects.get(pk=combination["product"])
                quantity = combination["quantity"]
                variants = combination["variant_combination"]

                # Validate stock availability
                stock = Stock.objects.filter(item=product, variant_combination=variants).first()
                if not stock or stock.quantity_available < quantity:
                    return JsonResponse({"success": False, "message": "Insufficient stock for product."})

                # Deduct stock and save CommandLine
                stock.quantity_available -= quantity
                stock.save()

                CommandLine.objects.create(
                    command=command,
                    product=product,
                    quantity=quantity,
                    variant_combination=variants
                )

                total_amount += product.unit_price * quantity

            # Update total amount
            command.total_amount = total_amount
            command.save()

            return redirect("get_command")

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    # For GET request
    return render(request, "add_command.html", {
        "customers": customer.objects.all(),
        "deliveries": Delivery.objects.all(),
        "items": item.objects.all(),
        "variant_data": json.dumps(_get_variant_data()),
    })



def _get_variant_data():
    """
    Fetch variant data dynamically from the database to render in the frontend.
    """
    items_queryset = item.objects.prefetch_related("itemvariant_set")
    variant_data = {
        item_obj.pk: {
            variant.variant_name: variant.variant_values
            for variant in item_obj.itemvariant_set.all()
        }
        for item_obj in items_queryset
    }
    return variant_data












def get_command(request):
    commands = Command.objects.prefetch_related("lines").all()
    return render(request, "command_detail.html", {"commands": commands})




def get_delivery(request):
    deliveris = Delivery.objects.all()
    return render(request, 'delivery_detail.html', {'deliveris': deliveris})


def update_command(request, pk):
    command = get_object_or_404(Command, pk=pk)
    customers = customer.objects.all()
    deliveries = Delivery.objects.all()
    products_queryset = item.objects.prefetch_related("itemvariant_set")

    # Prepare variant data for frontend
    variant_data = {
        str(product.pk): {
            variant.variant_name: variant.variant_values
            for variant in product.itemvariant_set.all()
        }
        for product in products_queryset
    }

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Debugging the incoming POST data
                print("===== POST DATA =====")
                print(request.POST)
                print("=====================")

                # Extracting form data
                customer_id = request.POST.get("customer_id")
                delivery_id = request.POST.get("delivery_id")
                order_date = request.POST.get("order_date")
                shipping_address = request.POST.get("shipping_address")
                variant_combinations = json.loads(request.POST.get("variant_combinations", "[]"))

                # Validate mandatory fields
                if not customer_id or not delivery_id or not order_date:
                    return JsonResponse(
                        {"success": False, "message": "Missing required fields."},
                        status=400,
                    )

                # Update Command
                command.customer = get_object_or_404(customer, pk=customer_id)
                command.delivery = get_object_or_404(Delivery, pk=delivery_id)
                command.order_date = order_date
                command.shipping_address = shipping_address
                command.total_amount = 0
                command.save()

                # Delete existing command lines
                command.lines.all().delete()

                total_quantity = 0

                # Process each variant combination
                for combination in variant_combinations:
                    product_id = combination.get("product")
                    quantity = combination.get("quantity")
                    variant_combination = combination.get("variant_combination", {})

                    if not product_id or not quantity:
                        continue

                    product = get_object_or_404(item, pk=product_id)

                    # Check stock
                    stock = Stock.objects.filter(
                        item=product, variant_combination=variant_combination
                    ).first()

                    if not stock or stock.quantity_available < quantity:
                        raise ValueError(
                            f"Insufficient stock for {product.product_name} with variants {variant_combination}."
                        )

                    stock.quantity_available -= quantity
                    stock.save()

                    # Create CommandLine
                    CommandLine.objects.create(
                        command=command,
                        product=product,
                        quantity=quantity,
                        variant_combination=variant_combination,
                    )

                    command.total_amount += product.unit_price * quantity
                    total_quantity += quantity

                command.save()

                return redirect("get_command")
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return render(
        request,
        "update_command.html",
        {
            "command": command,
            "customers": customers,
            "deliveries": deliveries,
            "products": products_queryset,
            "variant_data": json.dumps(variant_data),
        },
    )




















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


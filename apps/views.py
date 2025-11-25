from django.contrib.messages import get_messages
import json
from django.db.models.functions import TruncMonth
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date, datetime, timedelta
from django.utils import timezone as django_timezone
from django.utils.timezone import make_aware, now 
from django.db.models import Sum , Count , F, FloatField
from django.http import JsonResponse
from django.db import transaction 
import logging
from django.db import IntegrityError 
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.decorators import api_view
from .models import  Livreurs, Note, Stock, customuser,CommandLine, facture, leaddata, lead, customer, itemvariant, item, supplier,Notification,BonReceptionLine , retour,bonreception ,AdminUser,Delivery,Command
from .forms import CommandForm,CommandLineFormSet, CustomUserChangeForm, DeleteSupplierForm, FactureForm, LivreurCreationForm, UpdateSupplierForm, customerDeleteForm,  LoginForm, UpdatecustomerForm,DeleteLeadForm, UpdateLeadForm, itemForm
from .forms import  UpdateitemForm, UpdateItemVariant, customuserCreationForm ,RetourForm,BonReceptionForm,AdminUserCreationForm , BonReceptionLineFormSet  
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import user_passes_test ,login_required
from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import re





@api_view(['GET', 'POST', 'PUT', 'DELETE'])



def registration_view(request):
    if request.method == 'POST':
        form = customuserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = customuserCreationForm()
    return render(request, 'register.html', {'form': form})



def get_variants(request, item):
    try:
        variants = itemvariant.objects.filter(item_id=item).values('variant_name', 'variant_values')
        return JsonResponse({"success": True, "variants": list(variants)})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)




# dashboard function men hna ibdou 


def get_low_stock_items():
    return Stock.objects.filter(quantity_available__lt=10).values(
        'item__product_name', 'quantity_available'
    ).order_by('quantity_available')

def get_out_of_stock_items():
    return Stock.objects.filter(quantity_available=0).values('item__product_name')

def get_most_replenished_items():
    return BonReceptionLine.objects.values(
        'item__product_name'
    ).annotate(total_replenished=Sum('quantity')).order_by('-total_replenished')[:5]

def get_top_customers():
    return Command.objects.values(
        'customer__customer_name'
    ).annotate(total_spent=Sum('total_amount'), total_orders=Count('id')).order_by('-total_spent')[:5]

def get_inactive_customers():
    six_months_ago = date.today() - timedelta(days=180)
    return customer.objects.exclude(
        command__order_date__gte=six_months_ago
    ).values('customer_name')

def get_customer_retention_rate():
    total_customers = customer.objects.count()
    repeat_customers = Command.objects.values('customer').annotate(order_count=Count('id')).filter(order_count__gt=1).count()
    return (repeat_customers / total_customers) * 100 if total_customers > 0 else 0

def get_best_selling_product_all_time():
    return CommandLine.objects.values(
        'product__product_name'
    ).annotate(
        total_quantity_sold=Sum('quantity')
    ).order_by('-total_quantity_sold').first()

def get_livreur_with_most_deliveries():
    livreur = Livreurs.objects.annotate(
        total_deliveries=Count('deliveries')
    ).order_by('-total_deliveries').values('username', 'total_deliveries').first()
    
    if livreur:
        return {
            'livreur_name': livreur['username'], 
            'total_deliveries': livreur['total_deliveries'] 
        }
    return None  


def get_item_with_most_returns():
    return retour.objects.values(
        'facture__commands__lines__product__product_name'  
    ).annotate(
        return_count=Count('retour')  
    ).order_by('-return_count').first()
    
    
def get_least_selling_product_all_time():
    unsold_products = item.objects.exclude(
        commandline__isnull=False
    ).first()

    if unsold_products:
        return {
            'product_name': unsold_products.product_name,
            'total_quantity_sold': 0
        }

    least_selling_product = CommandLine.objects.values(
        'product__product_name'
    ).annotate(
        total_quantity_sold=Sum('quantity')
    ).order_by('total_quantity_sold').first()

    if least_selling_product:
        return {
            'product_name': least_selling_product['product__product_name'],
            'total_quantity_sold': least_selling_product['total_quantity_sold']
        }

    return {}

    
    
def get_unsold_products():
    unsold_products = item.objects.exclude(
        commandline__isnull=False  
    ).annotate(
        total_quantity_sold=Sum('commandline__quantity') 
    ).values('product_name', 'total_quantity_sold')  # Ensure it's a list of dictionaries

    return list(unsold_products)


def get_most_active_customer():
    return Command.objects.values(
        'customer__customer_name'
    ).annotate(
        total_commands=Count('id')
    ).order_by('-total_commands').first()
    

def get_monthly_least_selling_product():
    current_month = now().month

    unsold_product = item.objects.exclude(
        commandline__command__order_date__month=current_month  
    ).first()

    if unsold_product:
        return {
            'product_name': unsold_product.product_name,
            'total_quantity_sold': 0
        }

    return CommandLine.objects.filter(
        command__order_date__month=current_month
    ).values(
        'product__product_name'
    ).annotate(
        total_quantity_sold=Sum('quantity')
    ).order_by('total_quantity_sold').first()


def get_livreur_with_least_deliveries():
    livreur = Livreurs.objects.annotate(
        total_deliveries=Count('deliveries')
    ).order_by('total_deliveries').values('username', 'total_deliveries').first()
    
    if livreur:
        return {
            'livreur_name': livreur['username'],  
            'total_deliveries': livreur['total_deliveries'] 
        }
    return None 
    

def get_monthly_best_selling_product():
    current_month = now().month
    best_selling_product = CommandLine.objects.filter(
        command__order_date__month=current_month
    ).values(
        'product__product_name'
    ).annotate(
        total_quantity_sold=Sum('quantity')
    ).order_by('-total_quantity_sold').first()

    if best_selling_product:
        return {
            'product_name': best_selling_product['product__product_name'],
            'total_quantity_sold': best_selling_product['total_quantity_sold']
        }

    return {}

    

def get_supplier_with_most_returns():
    return retour.objects.values(
        'supplier__supplier_name'
    ).annotate(
        return_count=Count('retour')
    ).order_by('-return_count').first()
    
def get_livreur_with_most_returns():
    return retour.objects.values(
        'livreur__username'
    ).annotate(
        return_count=Count('retour')
    ).order_by('-return_count').first()

def get_customer_with_most_returns():
    return retour.objects.values(
        'facture__customer__customer_name'
    ).annotate(
        return_count=Count('retour')
    ).order_by('-return_count').first()
    
    
def get_best_customer_by_spent_amount():
    return Command.objects.values(
        'customer__customer_name'
    ).annotate(
        total_spent=Sum('total_amount')  
    ).order_by('-total_spent').first()




def get_monthly_sales_trends():
    current_month = now().month
    return Command.objects.filter(
        order_date__month=current_month
    ).values(
        'order_date'
    ).annotate(
        daily_sales=Sum('total_amount')
    ).order_by('order_date')



def get_monthly_revenue():
    current_month = now().month
    return Command.objects.filter(
        order_date__month=current_month
    ).aggregate(
        total_revenue=Sum('total_amount')  
    )['total_revenue'] or 0 



def get_best_supplier_by_weighted_score():
    return BonReceptionLine.objects.values(
        'bon_reception__supplier__supplier_name',  
        'bon_reception__supplier__product_quality',
        'bon_reception__supplier__interaction_quality',
        'bon_reception__supplier__cost'
    ).annotate(
        total_quantity_supplied=Sum('quantity'), 
        weighted_score=(
            (F('bon_reception__supplier__product_quality') * 0.5) +  
            (F('bon_reception__supplier__interaction_quality') * 0.3) -
            (F('bon_reception__supplier__cost') * 0.2)  
        )
    ).order_by('-weighted_score', '-total_quantity_supplied').first()
    
    
    

def get_worst_supplier_by_weighted_score():
    return BonReceptionLine.objects.values(
        'bon_reception__supplier__supplier_name',  
        'bon_reception__supplier__product_quality',
        'bon_reception__supplier__interaction_quality',
        'bon_reception__supplier__cost'
    ).annotate(
        total_quantity_supplied=Sum('quantity'), 
        weighted_score=( 
            (F('bon_reception__supplier__product_quality') * 0.5) +  
            (F('bon_reception__supplier__interaction_quality') * 0.3) - 
            (F('bon_reception__supplier__cost') * 0.2)  
        )
    ).order_by('weighted_score', 'total_quantity_supplied').first()
  

def get_monthly_highest_value_command():
    current_month = now().month

    highest_value_command = Command.objects.filter(
        order_date__month=current_month
    ).order_by('-total_amount').values(
        'id',
        'total_amount',
        'customer__customer_name', 
        'lines__product__product_name',
        'lines__variant_combination'  
    ).first()

    return highest_value_command

def get_day_with_best_sales():
    current_month = now().month
    return Command.objects.filter(
        order_date__month=current_month
    ).values(
        'order_date'
    ).annotate(
        total_sales=Sum('total_amount')
    ).order_by('-total_sales').first()

def monthly_returns():
    current_month = django_timezone.now().month
    current_year = django_timezone.now().year
    returns_this_month = retour.objects.filter(
        date_retour__year=current_year,
        date_retour__month=current_month
    ).values('date_retour').annotate(total_returns=Count('retour'))

    return returns_this_month




def monthly_returns_by_supplier():
    current_month = now().month
    current_year = now().year
    naive_date = datetime(current_year, current_month, 1)
    aware_date = make_aware(naive_date)    
    returns_by_supplier = retour.objects.filter(
        date_retour__gte=aware_date,
        date_retour__lt=now()
    ).values('supplier__supplier_name').annotate(total_returns=Count('retour'))

    return returns_by_supplier


def sales_dashboard_data(request):
    monthly_sales_trends = Command.objects.filter(
        order_date__month=date.today().month
    ).values('order_date').annotate(daily_sales=Sum('total_amount')).order_by('order_date')

    monthly_sales_trends = [
        {'order_date': entry['order_date'].strftime('%Y-%m-%d'), 'daily_sales': entry['daily_sales']}
        for entry in monthly_sales_trends
    ]
    best_selling_products = Command.objects.values(
        'lines__product__product_name'
    ).annotate(total_quantity_sold=Sum('lines__quantity')).order_by('-total_quantity_sold')[:5]
    best_selling_products = [
        {'product_name': entry['lines__product__product_name'], 'total_quantity_sold': entry['total_quantity_sold']}
        for entry in best_selling_products
    ]
    monthly_revenue = Command.objects.filter(order_date__month=date.today().month).aggregate(
        total_revenue=Sum('total_amount')
    )['total_revenue'] or 0

    day_with_best_sales = (
        max(monthly_sales_trends, key=lambda x: x['daily_sales'])
        if monthly_sales_trends else None
    )

    response_data = {
        'sales_labels': [entry['order_date'] for entry in monthly_sales_trends],
        'sales_values': [entry['daily_sales'] for entry in monthly_sales_trends],
        'best_seller_labels': [entry['product_name'] for entry in best_selling_products],
        'best_seller_values': [entry['total_quantity_sold'] for entry in best_selling_products],
        'monthly_revenue': monthly_revenue,
        'day_with_best_sales': day_with_best_sales,
        'get_monthly_highest_value_command':get_monthly_highest_value_command(),
        'least_seller': get_least_selling_product_all_time(), # hethy 1 get_monthly_least_selling_product
        'monthly_best_seller': get_monthly_best_selling_product(),   #hethy 2 lazem nzid get_best_selling_product_all_time
        'unsold_products': get_unsold_products(),     #hethy 3
    }
    return JsonResponse(response_data, encoder=DjangoJSONEncoder)



def sales_dashboard_page(request):
    return render(request, 'sales_dashboard.html')





from django.db.models import QuerySet


def stock_dashboard_page(request):
    context = {
        'low_stock_items': get_low_stock_items(),
        'out_of_stock_items': get_out_of_stock_items(),
        'most_replenished_items': get_most_replenished_items(),
        'unsold_products': get_unsold_products(),
    }
    return render(request, 'stock_dashboard.html', context)





def monthly_returns_by_item_view(request):
    data = (
        retour.objects.annotate(month=TruncMonth('date_retour'))
        .values('month', 'facture__commands__lines__product__product_name')
        .annotate(total_returns=Count('id'))
        .order_by('month', 'facture__commands__lines__product__product_name')
    )

    result = [
        {
            'month': item['month'].strftime('%Y-%m'),
            'product_name': item['facture__commands__lines__product__product_name'],
            'total_returns': item['total_returns']
        }
        for item in data
    ]

    return JsonResponse(result, safe=False)


def monthly_returns_by_customer_view(request):
    data = (
        retour.objects.annotate(month=TruncMonth('date_retour'))
        .values('month', 'customer__customer_name')
        .annotate(total_returns=Count('id'))
        .order_by('month', 'customer__customer_name')
    )

    result = [
        {
            'month': item['month'].strftime('%Y-%m'),
            'customer_name': item['customer__customer_name'],
            'total_returns': item['total_returns']
        }
        for item in data
    ]

    return JsonResponse(result, safe=False)


def monthly_returns_by_livreur_view(request):
    data = (
        retour.objects.annotate(month=TruncMonth('date_retour'))
        .values('month', 'livreur__username')
        .annotate(total_returns=Count('id'))
        .order_by('month', 'livreur__username')
    )

    result = [
        {
            'month': item['month'].strftime('%Y-%m'),
            'livreur_username': item['livreur__username'],
            'total_returns': item['total_returns']
        }
        for item in data
    ]

    return JsonResponse(result, safe=False)




logger = logging.getLogger(__name__)


def serialize_queryset(queryset, fields=None):
    """Helper function to serialize QuerySet objects."""
    if isinstance(queryset, QuerySet):
        return list(queryset) if not fields else [
            {field: item.get(field) for field in fields} for item in queryset
        ]
    return queryset




def returns_and_losses_dashboard(request):
    logger.info('Dashboard view called')

    most_returned_item = get_item_with_most_returns()
    supplier_with_most_returns = get_supplier_with_most_returns()
    livreur_with_most_returns = get_livreur_with_most_returns()
    customer_with_most_returns = get_customer_with_most_returns()
    least_seller = get_least_selling_product_all_time()
    
    monthly_returns_data = retour.objects.annotate(
        month=TruncMonth('date_retour')
    ).values('month').annotate(total_returns=Count('retour')).order_by('month')

    monthly_returns_by_supplier_data = retour.objects.annotate(
        month=TruncMonth('date_retour')
    ).values('month', 'supplier__supplier_name').annotate(
        total_returns=Count('retour')
    ).order_by('month', 'supplier__supplier_name')

    monthly_returns_by_item_data = retour.objects.annotate(
        month=TruncMonth('date_retour')
    ).values('month', 'facture__commands__lines__product__product_name').annotate(
        total_returns=Count('retour')
    ).order_by('month', 'facture__commands__lines__product__product_name')

    monthly_returns_by_customer_data = retour.objects.annotate(
        month=TruncMonth('date_retour')
    ).values('month', 'facture__customer__customer_name').annotate(
        total_returns=Count('retour')
    ).order_by('month', 'facture__customer__customer_name')

    monthly_returns_by_livreur_data = retour.objects.annotate(
        month=TruncMonth('date_retour')
    ).values('month', 'livreur__username').annotate(
        total_returns=Count('retour')
    ).order_by('month', 'livreur__username')

    data = {
        'most_returned_item': serialize_queryset(
            most_returned_item, fields=['facture__commands__lines__product__product_name', 'return_count']
        ),
        'supplier_with_most_returns': serialize_queryset(
            supplier_with_most_returns, fields=['supplier__supplier_name', 'return_count']
        ),
        'livreur_with_most_returns': serialize_queryset(
            livreur_with_most_returns, fields=['livreur__username', 'return_count']
        ),
        'customer_with_most_returns': serialize_queryset(
            customer_with_most_returns, fields=['facture__customer__customer_name', 'return_count']
        ),
        'least_seller': serialize_queryset(
            least_seller, fields=['product__product_name', 'total_quantity_sold']
        ),
        'monthly_returns': serialize_queryset(
            monthly_returns_data, fields=['month', 'total_returns']
        ),
        'monthly_returns_by_supplier': serialize_queryset(
            monthly_returns_by_supplier_data, fields=['month', 'supplier__supplier_name', 'total_returns']
        ),
        'monthly_returns_by_item': serialize_queryset(
            monthly_returns_by_item_data, fields=['month', 'facture__commands__lines__product__product_name', 'total_returns']
        ),
        'monthly_returns_by_customer': serialize_queryset(
            monthly_returns_by_customer_data, fields=['month', 'facture__customer__customer_name', 'total_returns']
        ),
        'monthly_returns_by_livreur': serialize_queryset(
            monthly_returns_by_livreur_data, fields=['month', 'livreur__username', 'total_returns']
        ),
    }

    return JsonResponse(data)


def returns_and_losses_page(request):
    return render(request, 'returns_losses_dashboard.html')


def page(request):
    return render(request,'page.html')



 
def get_livreur_performance():
    livreur_performance = Livreurs.objects.annotate(
        total_deliveries=Count('deliveries'),  
        total_returns=Count('retour')  
    ).values('username', 'total_deliveries', 'total_returns')
    livreur_data = [
        {'livreur_name': entry['username'], 'total_deliveries': entry['total_deliveries'], 'total_returns': entry['total_returns']}
        for entry in livreur_performance
    ]
    return livreur_data



def get_customer_retention_rate(request):
    total_customers = customer.objects.count()  
    repeat_customers = Command.objects.values('customer').annotate(order_count=Count('id')).filter(order_count__gt=1).count()
    retention_rate = (repeat_customers / total_customers) * 100 if total_customers > 0 else 0
    return {'retention_rate': retention_rate}


def get_supplier_performance(request):
    supplier_performance = BonReceptionLine.objects.values(
        'bon_reception__supplier__supplier_name'
    ).annotate(
        total_supplied=Sum('quantity')
    ).order_by('-total_supplied')


    returns_per_supplier = retour.objects.values('supplier').annotate(
        total_returns=Count('retour')
    )

    returns_dict = {entry['supplier']: entry['total_returns'] for entry in returns_per_supplier}

    supplier_data = []
    for entry in supplier_performance:
        supplier_name = entry['bon_reception__supplier__supplier_name']
        total_supplied = entry['total_supplied']
        total_returns = returns_dict.get(supplier_name, 0)  

        supplier_data.append({
            'supplier_name': supplier_name,
            'total_supplied': total_supplied,
            'total_returns': total_returns
        })

    return supplier_data


def productivity_dashboard_data(request):
    top_customers = get_top_customers()
    serialized_top_customers = [
        {
            'customer_name': customer['customer__customer_name'],
            'total_spent': customer['total_spent'],
            'total_orders': customer['total_orders']
        }
        for customer in top_customers
    ]
    return JsonResponse({
        'livreur_performance': get_livreur_performance(),
        'customer_retention_rate': get_customer_retention_rate(request),
        'supplier_performance': get_supplier_performance(request),
        'top_livreur': get_livreur_with_most_deliveries(),
        'least_active_livreur': get_livreur_with_least_deliveries(),
        'best_supplier': get_best_supplier_by_weighted_score(),
        'most_active_customer': get_most_active_customer(),
        'inactive_customers': list(get_inactive_customers().values('customer_name')),
        'get_best_customer_by_spent_amount':get_best_customer_by_spent_amount(),
        'get_monthly_highest_value_command':get_monthly_highest_value_command(),
        'top_customers': serialized_top_customers,
        'worst_supplier' : get_worst_supplier_by_weighted_score(),
    })



def productivity_dashboard_page(request):
    context = {
        'top_livreur': get_livreur_with_most_deliveries(),
        'least_active_livreur': get_livreur_with_least_deliveries(),
        'best_supplier': get_best_supplier_by_weighted_score(),
        'most_active_customer': get_most_active_customer(),
        'inactive_customers': get_inactive_customers(),
    }
    return render(request, 'productivity_dashboard.html', context)


# =========================================dashboard function men hna =================================================



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
                            stock = Stock.objects.filter(
                                item=line.item,
                                variant_combination=variants
                            ).first()

                            if stock:
                                # If stock exists, update the quantity
                                print(f"Existing stock found for {line.item.product_name} with variants {variants}. Updating quantity.")
                                stock.quantity_available += line.quantity
                            else:
                                # If no stock exists, create a new entry
                                print(f"No existing stock for {line.item.product_name} with variants {variants}. Creating new stock.")
                                stock = Stock.objects.create(
                                    item=line.item,
                                    item_variant=variant,
                                    variant_combination=variants,
                                    quantity_available=line.quantity
                                )
                            stock.save()  # Save the updated/new stock entry
                            print(f"Stock updated: {stock}")

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
        'variant_data': json.dumps(variant_data),  # Preload dynamic variant data
    })











def update_bonreception(request, delivery_id):
    try:
        # Fetch the existing bon_reception (still required for referencing and updating)
        bon_reception = get_object_or_404(bonreception, pk=delivery_id)
        print(f"Fetched bon_reception: {bon_reception}")

        if request.method == 'POST':
            print("Processing POST request...")
            # Bind the form and formset to the request data without preloading instance data
            form = BonReceptionForm(request.POST)  # No instance
            formset = BonReceptionLineFormSet(request.POST)  # No instance

            # Debugging form validation
            print(f"Form valid: {form.is_valid()}, Formset valid: {formset.is_valid()}")
            print(f"Form errors: {form.errors}")
            print(f"Formset errors: {formset.errors}")

            if form.is_valid() and formset.is_valid():
                try:
                    with transaction.atomic():
                        # Save changes to bon_reception itself (using the existing object)
                        bon_reception.delivery_address = form.cleaned_data['delivery_address']
                        bon_reception.delivery_date = form.cleaned_data['delivery_date']
                        bon_reception.supplier = form.cleaned_data['supplier']
                        bon_reception.save()
                        print(f"Updated bon_reception: {bon_reception}")

                        # Adjust stock for removed lines
                        existing_lines = list(bon_reception.lines.all())
                        updated_lines = []
                        print(f"Existing lines: {existing_lines}")

                        for form_line in formset:
                            print(f"Form Errors for {form_line.prefix}: {form_line.errors}")
                            if form_line.cleaned_data and not form_line.cleaned_data.get('DELETE', False):
                                line = form_line.save(commit=False)
                                updated_lines.append(line)

                                # Adjust stock for updated lines
                                product = line.item
                                variant_combination = line.variant_combination
                                quantity = line.quantity
                                print(f"Updating line: Product={product}, VariantCombination={variant_combination}, Quantity={quantity}")

                                stock, created = Stock.objects.get_or_create(
                                    item=product,
                                    variant_combination=variant_combination,
                                    defaults={'quantity_available': 0}
                                )
                                print(f"Stock before update: {stock.quantity_available}, Created: {created}")
                                stock.quantity_available += quantity - line.quantity
                                stock.save()
                                print(f"Stock after update: {stock.quantity_available}")

                                line.bon_reception = bon_reception
                                line.save()
                                print(f"Line saved: {line}")

                        # Handle removed lines
                        removed_lines = [line for line in existing_lines if line not in updated_lines]
                        print(f"Removed lines: {removed_lines}")
                        for line in removed_lines:
                            product = line.item
                            variant_combination = line.variant_combination
                            quantity = line.quantity
                            print(f"Removing line: Product={product}, VariantCombination={variant_combination}, Quantity={quantity}")

                            stock = Stock.objects.filter(item=product, variant_combination=variant_combination).first()
                            if stock:
                                stock.quantity_available -= quantity
                                stock.save()
                                print(f"Adjusted stock for removed line: {stock.quantity_available}")
                            line.delete()
                            print(f"Line deleted: {line}")

                        # Success message
                        messages.success(request, f"Reception note {delivery_id} updated successfully.")
                        return redirect('all_bonreception')

                except Exception as e:
                    # Rollback on failure
                    print(f"Transaction failed: {e}")
                    messages.error(request, f"An unexpected error occurred: {str(e)}")
            else:
                # Handle invalid form or formset
                messages.error(request, "Invalid form data. Please review and try again.")
        else:
            print("Rendering GET request...")
            # Initialize empty forms for GET requests (no preloading)
            form = BonReceptionForm()
            formset = BonReceptionLineFormSet()

        # Fetch suppliers and items for rendering the page
        suppliers = supplier.objects.all()
        print(f"Suppliers fetched: {suppliers}")
        items_queryset = item.objects.prefetch_related(
            Prefetch(
                'itemvariant_set',
                queryset=itemvariant.objects.all()
            )
        )
        print(f"Items fetched: {items_queryset}")

        # Prepare dynamic variant data for the frontend
        variant_data = {
            f"{item_obj.pk}": {
                variant.variant_name: variant.variant_values
                for variant in item_obj.itemvariant_set.all()
            }
            for item_obj in items_queryset
        }
        print(f"Variant data prepared: {variant_data}")

        return render(request, 'updatereception.html', {
            'form': form,
            'formset': formset,
            'suppliers': suppliers,
            'items': items_queryset,
            'variant_data': json.dumps(variant_data),
        })

    except Exception as e:
        print(f"Unexpected error: {e}")
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('all_bonreception')
















def all_bonreception(request):
    storage = get_messages(request)
    for message in storage:
        print("Stored message:", message)
    bonreceptions = bonreception.objects.prefetch_related('lines__item').all()  
    return render(request, 'allreception.html', {'bonreceptions': bonreceptions})



def search_bonreception(request):
    if request.method == 'GET':
        searched = request.GET.get('searched', '')
        bonreceptions = bonreception.objects.all()
        bon_reception_lines = BonReceptionLine.objects.all()

        if searched:
            # Filter `bonreception` results
            bonreceptions = bonreception.objects.filter(
                Q(delivery_date__icontains=searched) |
                Q(delivery_address__icontains=searched) |
                Q(supplier__supplier_name__icontains=searched)
            )

            # Filter `BonReceptionLine` results
            bon_reception_lines = BonReceptionLine.objects.filter(
                Q(item__product_name__icontains=searched) |
                Q(variant_combination__icontains=searched) |
                Q(quantity__icontains=searched) |
                Q(bon_reception__supplier__supplier_name__icontains=searched)
            )

        return render(
            request, 
            'search_bonreception.html', 
            {'bonreceptions': bonreceptions, 'bon_reception_lines': bon_reception_lines, 'searched': searched}
        )
    else:
        return render(request, 'search_bonreception.html', {})




def allcustomers(request):
    customers = customer.objects.all()
    return render(request, 'allcustomers.html', {'customers': customers})

def all_leads(request):
    leads = lead.objects.all()
    return render(request, 'all_leads.html', {'leads': leads})

def all_retour(request):
    retours = retour.objects.select_related("supplier", "livreur", "facture__customer").all()  
    return render(request, 'allretour.html', {'retours': retours})







def add_retour(request):
    if request.method == 'POST':
        try:
            # Récupérer les données envoyées en JSON
            data = json.loads(request.body)

            facture_id = data.get('facture')
            selected_commands = data.get('selected_commands', [])
            supplier_id = data.get('supplier')
            raison_retour = data.get('raison_retour')
            date_retour = data.get('date_retour')
            livreur_id = data.get('livreur')
            informations_supp = data.get('informations_supp')

            # Debug : Affichage des données reçues
            print(f"Facture ID: {facture_id}")
            print(f"Selected Commands: {selected_commands}")
            print(f"Supplier ID: {supplier_id}")
            print(f"Reason for Return: {raison_retour}")
            print(f"Return Date: {date_retour}")
            print(f"Livreur ID: {livreur_id}")
            print(f"Additional Information: {informations_supp}")

            # Valider et récupérer les objets associés
            facture_instance = get_object_or_404(facture, pk=facture_id)
            supplier_instance = get_object_or_404(supplier, pk=supplier_id)
            livreur_instance = get_object_or_404(Livreurs, pk=livreur_id)

            # Debug : Affichage des objets récupérés
            print(f"Facture Instance: {facture_instance}")
            print(f"Supplier Instance: {supplier_instance}")
            print(f"Livreur Instance: {livreur_instance}")

            # Créer l'instance Retour
            retour_instance = retour.objects.create(
                facture=facture_instance,
                supplier=supplier_instance,
                raison_retour=raison_retour,
                date_retour=date_retour,
                livreur=livreur_instance,
                informations_supp=informations_supp,
            )
            print(f"Retour Instance Created: {retour_instance}")

            # Boucle à travers les commandes sélectionnées pour mettre à jour les stocks
            for command_id in selected_commands:
                print(f"Processing Command ID: {command_id}")
                command = get_object_or_404(Command, pk=command_id)

                for line in command.lines.all():
                    product = line.product
                    variant_combination = line.variant_combination
                    quantity = line.quantity

                    # Debug : Affichage des lignes de commande
                    print(f"Command Line - Product: {product}, Variant Combination: {variant_combination}, Quantity: {quantity}")

                    # Mise à jour du stock
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
            return redirect('all_retour')  # Redirection vers la vue all_retour après le traitement réussi

        except ValueError as e:
            print(f"Validation Error: {str(e)}")
            return JsonResponse({"success": False, "message": str(e)}, status=400)

        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    # Pour une requête GET, préparer les données pour le formulaire
    factures = facture.objects.all()  # Récupérer toutes les factures
    livreurs = Livreurs.objects.filter(user_type='livreur')  # Récupérer uniquement les livreurs
    suppliers = supplier.objects.all()  # Récupérer tous les fournisseurs

    # Debug : Affichage des données envoyées au template
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
        selected_facture = facture.objects.get(pk=facture_id)
        commands = selected_facture.commands.all()
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
    try:
        # Fetch the existing retour instance
        retour_instance = get_object_or_404(retour, pk=retour_id)
        facture_instance = retour_instance.facture

        if request.method == 'POST':
            with transaction.atomic():
                # Extract updated data from the form
                selected_commands = request.POST.get('selected_commands', '[]')
                supplier_id = request.POST.get('supplier')
                raison_retour = request.POST.get('raison_retour')
                date_retour = request.POST.get('date_retour')
                livreur_id = request.POST.get('livreur')
                informations_supp = request.POST.get('informations_supp')

                # Parse selected commands
                try:
                    selected_commands = json.loads(selected_commands)
                    if isinstance(selected_commands, int):  # Handle single command case
                        selected_commands = [selected_commands]
                    elif not isinstance(selected_commands, list):
                        raise ValueError("Invalid selected_commands format")
                except json.JSONDecodeError:
                    raise ValueError("Failed to parse selected_commands")

                # Debugging the updated data
                print(f"Updated Selected Commands: {selected_commands}")
                print(f"Updated Supplier: {supplier_id}")
                print(f"Updated Raison Retour: {raison_retour}")
                print(f"Updated Date Retour: {date_retour}")
                print(f"Updated Livreur: {livreur_id}")
                print(f"Updated Informations Supp: {informations_supp}")

                # Update the retour instance
                retour_instance.supplier = get_object_or_404(supplier, pk=supplier_id)
                retour_instance.raison_retour = raison_retour
                retour_instance.date_retour = date_retour
                retour_instance.livreur = get_object_or_404(Livreurs, pk=livreur_id)
                retour_instance.informations_supp = informations_supp
                retour_instance.save()

                # Adjust stock for previous commands
                previous_commands = facture_instance.commands.all()
                for command in previous_commands:
                    for line in command.lines.all():
                        product = line.product
                        variant_combination = line.variant_combination
                        quantity = line.quantity

                        stock = Stock.objects.filter(item=product, variant_combination=variant_combination).first()
                        if stock:
                            stock.quantity_available -= quantity
                            if stock.quantity_available < 0:
                                stock.quantity_available = 0  # Ensure no negative stock
                            stock.save()

                # Process new selected commands
                for command_id in selected_commands:
                    command = get_object_or_404(Command, pk=command_id)

                    for line in command.lines.all():
                        product = line.product
                        variant_combination = line.variant_combination
                        quantity = line.quantity

                        stock, created = Stock.objects.get_or_create(
                            item=product,
                            variant_combination=variant_combination,
                            defaults={"quantity_available": 0}
                        )
                        stock.quantity_available += quantity
                        stock.save()

                print("Retour updated successfully!")
                return redirect('all_retour')


        # For GET request, prepare data for the form
        factures = facture.objects.all()
        livreurs = Livreurs.objects.filter(user_type='livreur')
        suppliers = supplier.objects.all()
        commands = facture_instance.commands.all()

        # Prepare the current selected commands
        selected_commands = [{"id": command.id, "description": f"Command {command.id} - {command.shipping_address}"} for command in commands]

        # Debug the data sent to the template
        print(f"Rendering Update Retour Form for Retour ID: {retour_id}")
        print(f"Factures: {factures}")
        print(f"Livreurs: {livreurs}")
        print(f"Suppliers: {suppliers}")
        print(f"Selected Commands: {selected_commands}")

        return render(request, 'updateretour.html', {
            'retour': retour_instance,
            'factures': factures,
            'livreurs': livreurs,
            'suppliers': suppliers,
            'commands': json.dumps(selected_commands),
        })

    except Exception as e:
        print(f"Error updating retour: {str(e)}")
        return JsonResponse({"success": False, "message": str(e)}, status=500)







def delete_bonreception(request, delivery_id):
    try:
        with transaction.atomic():
            # Fetch the bonreception instance
            bon_reception = get_object_or_404(bonreception, pk=delivery_id)

            # Iterate over related BonReceptionLine entries
            for line in bon_reception.lines.all():
                product = line.item
                variant_combination = line.variant_combination
                quantity = line.quantity

                # Check if the product and variant combination have been sold
                sold_command_lines = CommandLine.objects.filter(
                    product=product,
                    variant_combination=variant_combination
                )
                if sold_command_lines.exists():
                    error_message = (
                        f"Cannot delete reception note {delivery_id}. "
                        f"Product '{product.product_name}' with variant combination "
                        f"{variant_combination} has been sold."
                    )
                    messages.error(request, error_message)  # Send red alert message
                    return redirect('all_bonreception')

                # Adjust stock for this item-variant combination
                stock = Stock.objects.filter(item=product, variant_combination=variant_combination).first()
                if stock:
                    stock.quantity_available -= quantity
                    if stock.quantity_available < 0:
                        stock.quantity_available = 0  # Ensure no negative stock
                    stock.save()

            # Delete all BonReceptionLine entries and the bonreception instance
            bon_reception.delete()
            success_message = f"Reception note {delivery_id} deleted successfully."
            messages.success(request, success_message)  # Send green alert message
            return redirect('all_bonreception')

    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('all_bonreception')



def delete_retour(request, pk):
    print(f"Received pk: {pk}")
    try:
        with transaction.atomic():
            # Fetch the retour instance
            retour_instance = get_object_or_404(retour, pk=pk)
            facture_instance = retour_instance.facture  # Get associated facture

            # Fetch commands linked to the facture
            commands = facture_instance.commands.all()  # Use the many-to-many relationship

            for command in commands:
                # Iterate through command lines
                for line in command.lines.all():
                    product = line.product
                    variant_combination = line.variant_combination
                    quantity = line.quantity

                    # Adjust stock for each command line
                    stock = Stock.objects.filter(item=product, variant_combination=variant_combination).first()
                    if stock:
                        stock.quantity_available -= quantity
                        stock.save()

            # Delete the retour instance
            retour_instance.delete()
            return redirect('all_retour')

    except retour.DoesNotExist:
        print(f"Retour with ID {pk} does not exist.")
        retours = retour.objects.select_related("supplier", "livreur", "facture__customer").all()
        return render(
            request,
            'allretour.html',
            {'retours': retours, 'error_message': f"Retour with ID {pk} does not exist."},
        )


           





def search_return(request):
    if request.method == 'GET':
        searched = request.GET.get('searched', '')

        # If there is a search term, filter the 'retour' objects based on the fields
        if searched:
            retours = retour.objects.filter(
                Q(supplier__supplier_name__icontains=searched) |  # Search by supplier name (adjust supplier_name field as per model)
                Q(raison_retour__icontains=searched) |  # Search by return reason
                Q(date_retour__icontains=searched) |  # Search by return date (as string)
                Q(livreur__full_name__icontains=searched) |  # Search by livreur name (adjust livreur_name field as per model)
                Q(informations_supp__icontains=searched) |  # Search by additional info
                Q(facture__facture_id__icontains=searched) |  # Search by facture id (facture_id in facture model)
                Q(facture__datef__icontains=searched) |  # Search by facture date (adjust datef field as per model)
                Q(facture__addressf__icontains=searched) |  # Search by facture address (adjust addressf field as per model)
                Q(facture__customer__customer_name__icontains=searched)  # Search by customer's name in facture (adjust customer_name field as per model)
            )
        else:
            # If no search term, return all 'retour' objects
            retours = retour.objects.all()

        # Render the search results page with the search term and results
        return render(request, 'search_return.html', {'retours': retours, 'searched': searched})

    else:
        # If the request is not GET, render the empty search page
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
    for product in items:  
        product.rowspan = product.itemvariant_set.count() + 1  
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
        customer_type= request.POST.get('customer_type')
        customer.objects.create(
            customer_name=customer_name,
            contact_person=contact_person,
            email=email,
            phone_number=phone_number,
            customer_type=customer_type
        )
        return redirect('allcustomers')
    return render(request, 'addcustomer.html')



logger = logging.getLogger(__name__)


def get_stock_levels(request):
    stocks = Stock.objects.select_related('item', 'item_variant').all()
    stock_data = []
    for stock in stocks:
        item_name = stock.item.product_name
        variant_combination = stock.variant_combination  
        quantity = stock.quantity_available  

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

    
    
def delete_facture(request, facture_id):
    try:
        with transaction.atomic():
            # Fetch the facture instance
            facture_instance = get_object_or_404(facture, pk=facture_id)

            # Delete the facture
            facture_instance.delete()
            print(f"Facture {facture_id} deleted successfully.")

            return redirect('get_all_factures')
    except facture.DoesNotExist:
        print(f"Facture with ID {facture_id} does not exist.")
        factures = facture.objects.all()
        return render(request, 'allfactures.html', {
            'factures': factures,
            'error_message': f"Facture with ID {facture_id} does not exist."
        })
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return render(request, 'allfactures.html', {
            'factures': facture.objects.all(),
            'error_message': f"Unexpected error: {str(e)}"
        })
   
   








def update_facture(request, facture_id):
    facture_instance = get_object_or_404(facture, pk=facture_id)
    customers = customer.objects.all()
    print("Customers:", customers)

    if request.method == "POST":
        try:
            data = request.POST.copy()
            customer_id = data.get("customer_id")
            selected_command_ids = data.getlist("command")

            if not customer_id or not selected_command_ids:
                return render(request, "updatefacture.html", {
                    "facture": facture_instance,
                    "customers": customers,
                    "error_message": "Customer and commands are required."
                })
            customer_instance = get_object_or_404(customer, pk=customer_id)

            with transaction.atomic():
                facture_instance.datef = data.get("datef")
                facture_instance.addressf = data.get("addressf")
                facture_instance.payment_method = data.get("Payment_Method")
                facture_instance.tax = data.get("tax", 0)
                facture_instance.discount = data.get("discount", 0)
                facture_instance.ttc = data.get("TTC", 0)
                facture_instance.customer = customer_instance
                facture_instance.save()

                selected_commands = Command.objects.filter(pk__in=selected_command_ids)
                facture_instance.commands.set(selected_commands)

            return redirect("get_all_factures")

        except Exception as e:
            print("Error updating facture:", e)
            print("Error updating facture:", e)
            return render(request, "updatefacture.html", {
                "facture": facture_instance,
                "customers": customers,
                "error_message": "An unexpected error occurred. Please try again."
            })
            
    return render(request, "updatefacture.html", {
        "facture": facture_instance,
        "customers": customers,
    })




def get_commands_by_customer(request, customer_id):
    try:
        # Debug: Log customer ID from request
        print(f"Customer ID received by get command function: {customer_id}")
        
        # Get the customer instance
        customer_instance = get_object_or_404(customer, pk=customer_id)
        print(f"Customer instance fetched  by get command function: {customer_instance}")
        
        # Fetch commands for the given customer
        commands = Command.objects.filter(customer=customer_instance)
        print(f"Commands fetched for customer  by get command function {customer_id}: {commands}")
        
        # Serialize command data
        command_data = [
            {"id": command.id, "label": f"Command {command.id} - {command.shipping_address}"}
            for command in commands
        ]
        print(f"Serialized command data: by get command function {command_data}")
        
        # Return JSON response
        return JsonResponse({"success": True, "commands": command_data})
    
    except customer.DoesNotExist:
        print("Error  by get command function: Customer not found.")
        return JsonResponse({"success": False, "message": "Customer not found."}, status=404)
    
    except Exception as e:
        print(f"Error in get_commands_by_customer  : {e}")
        return JsonResponse({"success": False, "message": str(e)}, status=500)











    
    























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
                Q(facture_id__icontains=searched) |  # Search by facture ID
                Q(datef__icontains=searched) |  # Search by facture date
                Q(addressf__icontains=searched) |  # Search by address
                Q(tax__icontains=searched) |  # Search by tax
                Q(discount__icontains=searched) |  # Search by discount
                Q(calculated_total__icontains=searched) |  # Search by calculated total
                Q(ttc__icontains=searched) |  # Search by total TTC
                Q(payment_method__icontains=searched) |  # Search by payment method
                Q(customer__customer_name__icontains=searched) |  # Search by customer name
                Q(commands__id__icontains=searched)  # Search by related commands name
            ).distinct()  # Use distinct() to avoid duplicate results from ManyToMany relationships
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
            data = request.POST.copy()
            customer_id = data.get("customer_id")
            selected_command_ids = data.getlist("command")

            if not customer_id or not selected_command_ids:
                return JsonResponse({"success": False, "message": "Customer and commands are required."})

            print("POST Request - Customer ID:", customer_id)
            print("POST Request - Selected Commands:", selected_command_ids)

            customer_instance = get_object_or_404(customer, pk=customer_id)

            selected_commands = Command.objects.filter(pk__in=selected_command_ids)

            print("Fetched Commands for POST:", selected_commands)

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
            print("GET Request - Customer ID:", customer_id)

            # Fetch commands related to the customer
            commands = Command.objects.filter(customer_id=customer_id)

            print("Fetched Commands for GET:", commands)

            commands_data = [{"id": cmd.pk, "label": f"Command {cmd.pk}"} for cmd in commands]

            return JsonResponse({"success": True, "commands": commands_data})
        except Exception as e:
            print("Error fetching commands:", e)
            return JsonResponse({"success": False, "message": str(e)})

    else:
        customers = customer.objects.all()

        print("Rendering Form - Available Customers:", customers)

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

def variant_delete(request, variant_id):
    try:
        variant = itemvariant.objects.get(variant_id=variant_id)
        variant.delete()
        return redirect('all_items')
    except itemvariant.DoesNotExist:
        return redirect(request, 'variant_not_found.html', {'variant_id': variant_id})
    

def product_delete(request, item_id):
    try:
        product = item.objects.get(item=item_id)  
        product.delete() 
        return redirect('all_items')  
    except item.DoesNotExist:  
        return render(request, 'item_not_found.html', {'item_id': item_id})
 



def delete_delivery(request, delivery_id):
    try:
        delivery = Delivery.objects.get(delivery_id=delivery_id)
        delivery.delete()
        return redirect('get_delivery')
    except Delivery.DoesNotExist:
        return render(request, 'delivery_not_found.html', {'delivery_id': delivery_id})



def delete_command(request, pk):
    print(f"Received Command ID: {pk}")
    try:
        with transaction.atomic():
            # Fetch the command instance
            command_instance = get_object_or_404(Command, pk=pk)
            
            # Iterate over command lines to adjust stock
            for line in command_instance.lines.all():
                product = line.product
                variant_combination = line.variant_combination
                quantity = line.quantity

                # Adjust stock
                stock = Stock.objects.filter(item=product, variant_combination=variant_combination).first()
                if stock:
                    stock.quantity_available += quantity
                    stock.save()
                    print(f"Stock updated for product: {product.product_name} with combination {variant_combination}. New quantity: {stock.quantity_available}")
                else:
                    print(f"No stock found for product: {product.product_name} with combination {variant_combination}. Skipping adjustment.")

            # Delete all related command lines
            command_instance.lines.all().delete()
            print(f"Command lines for Command ID {pk} deleted.")

            # Delete the command itself
            command_instance.delete()
            print(f"Command ID {pk} deleted successfully.")

            return redirect('get_command')

    except Command.DoesNotExist:
        print(f"Command with ID {pk} does not exist.")
        return render(request, "commands.html", {
            "error_message": f"Command with ID {pk} does not exist.",
            "commands": Command.objects.all(),
        })
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return JsonResponse({"success": False, "message": str(e)})



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
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    unread_count = unread_notifications.count()
    print(f"Unread Count: {unread_count}")  # Debugging line
    print(f"Unread Notifications: {unread_notifications}")  # Debugging line
    context = {
        'unread_count': unread_count,
        'unread_notifications': unread_notifications,
    }
    return render(request, "home.html", context)

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
    commands = Command.objects.prefetch_related("lines").order_by('-id')
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
        commands = Command.objects.all()
        command_lines = CommandLine.objects.all()

        if searched:
            # Filter Commands
            commands = Command.objects.filter(
                Q(customer__customer_name__icontains=searched) |
                Q(order_date__icontains=searched) |
                Q(total_amount__icontains=searched) |
                Q(shipping_address__icontains=searched) |
                Q(delivery__company_name__icontains=searched)
            )

            # Filter CommandLines
            command_lines = CommandLine.objects.filter(
                Q(product__product_name__icontains=searched) |
                Q(variant_combination__icontains=searched) |
                Q(command__customer__customer_name__icontains=searched)
            )

        return render(
            request, 
            'search_command.html', 
            {'commands': commands, 'command_lines': command_lines, 'searched': searched}
        )
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
                    return redirect('livreur') 
                elif user.user_type == 'admin':
                    print("Redirecting to admin page")
                    return redirect('admin') 
                else:
                    print("Redirecting to home page")
                    return redirect('home') 
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

    # Si la requête est GET et qu'il y a un 'customer_id' dans l'URL, on renvoie les commandes pour ce client
    if request.method == 'GET' and request.GET.get('customer_id'):
        customer_id = request.GET.get('customer_id')
        try:
            print("GET Request - Customer ID:", customer_id)

            customer_instance = get_object_or_404(customer, pk=customer_id)

            commands_for_customer = Command.objects.filter(customer=customer_instance)

            print("Fetched Commands for GET:", commands_for_customer)

            command_list = [{"id": command.id, "label": f"Command {command.id}"} for command in commands_for_customer]

            return JsonResponse({"success": True, "commands": command_list})
        
        except Customer.DoesNotExist:
            return JsonResponse({"success": False, "message": "Customer not found"})

   
    elif request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        command_id = request.POST.get('command_id')
        note_text = request.POST.get('note')

       
        customer_instance = get_object_or_404(customer, pk=customer_id)
        command_instance = get_object_or_404(Command, pk=command_id)

        
        Note.objects.create(customer=customer_instance, command=command_instance, note=note_text)

        return redirect('all_notes')  

    return render(request, 'addnote.html', {'customers': customers, 'commands': commands})




def all_notes(request):
    notes = Note.objects.all()
    return render(request, 'all_notes.html', {'notes': notes})


def edit_note(request, note_id=None):
    customers = customer.objects.all()

    if request.method == 'GET' and request.GET.get('customer_id'):
        customer_id = request.GET.get('customer_id')
        try:
            customer_instance = get_object_or_404(customer, pk=customer_id)
            commands_for_customer = Command.objects.filter(customer=customer_instance)
            command_list = [{"id": command.id, "label": f"Commande {command.id}"} for command in commands_for_customer]

            # Retourner les commandes sous forme de JSON
            return JsonResponse({"success": True, "commands": command_list})

        except Customer.DoesNotExist:
            return JsonResponse({"success": False, "message": "Client non trouvé"})

    elif request.method == 'POST':
        # Récupérer les données envoyées
        customer_id = request.POST.get('customer_id')
        command_id = request.POST.get('command')
        note_text = request.POST.get('note')

        # Récupérer le client et la commande associés à partir des IDs
        customer_instance = get_object_or_404(Customer, pk=customer_id)
        command_instance = get_object_or_404(Command, pk=command_id)

        # Créer ou mettre à jour la note
        note = Note.objects.create(customer=customer_instance, command=command_instance, note=note_text)

        # Rediriger après l'édition
        return redirect('all_notes')  

    return render(request, 'edit_note.html', {
        'customers': customers,
    })



    
    
def delete_note(request, note_id):
    try:
        note = Note.objects.get(note_id=note_id) 
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
    
    
    
def check_stock_and_notify():
    low_stock_instances = Stock.objects.filter(quantity_available__lt=10)
    for low_stock in low_stock_instances:
        if low_stock.item_variant:
            variant_details = f"{low_stock.item_variant.variant_name}: {', '.join(low_stock.item_variant.variant_values)}"
        else:
            variant_details = "No variants specified"
        print(
            f"Processing Stock: {low_stock.item.product_name} - {variant_details}, Quantity: {low_stock.quantity_available}"
        )
    for low_stock in low_stock_instances:
        print(f"Processing Stock: {low_stock.item.product_name} - {low_stock.variant_combination}, Quantity: {low_stock.quantity_available}")
        users_to_notify = customuser.objects.filter(user_type__in=['admin', 'customuser'])
        for user in users_to_notify:
            notification, created = Notification.objects.get_or_create(
                user=user,
                stock=low_stock,  
                defaults={
                    "message": f"Stock low for {low_stock.item.product_name} - {low_stock.variant_combination}. Only {low_stock.quantity_available} left.",
                    "is_read": False,
                }
            )
            if not created:
                notification.stock = low_stock
                notification.save()
            print(f"Notification created or updated for user {user.username} with Stock ID: {low_stock.id}")




    

 
    
@csrf_exempt
@login_required
def mark_notifications_read(request):
    if request.method == 'POST':
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        unread_notifications.update(is_read=True)
        return JsonResponse({
            'success': True,
            'message': 'Notifications marked as read'
        })
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)



def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    stock = notification.stock  
    
    if not stock:
        return render(request, 'notification_detail.html', {
            'notification': notification,
            'stock': None,
            'error': 'Stock information is not available for this notification.'
        })

    if isinstance(stock.variant_combination, str):
        stock.variant_combination = json.loads(stock.variant_combination)
    
    print(type(stock.variant_combination), stock.variant_combination)  

    context = {
        'notification': notification,
        'stock': stock,
    }
    return render(request, 'notification_detail.html', context)


@login_required



def notification_list(request):
    notifications = Notification.objects.all()
    notification_data = []
    for notification in notifications:
        notification_data.append({
            "message": notification.message,
            "is_read": "Read" if notification.is_read else "Unread",
            "created_at": notification.created_at,
        })

    paginator = Paginator(notification_data, 10)
    page_number = request.GET.get('page', 1)
    paginated_notifications = paginator.get_page(page_number)

    return render(request, 'notification_page.html', {
        'notifications': paginated_notifications,
        'unread_count': Notification.objects.filter(is_read=False).count(),
    })








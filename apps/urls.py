from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import  add_itemvariant, add_orderitem, add_sales_order, allcustomers, customer_delete, home, add_customer, search_customers, search_orders, update_password
from .views import update_customer, update_order_item, update_sales_order, variant_delete, update_item_variant , leadsview
from .views import order_delete, logout_view, product_delete, products, sales_order_view,  login_view, search_product, registration_view, leads
from .views import add_centred_data,search_lead ,all_leads , delete_lead,updatelead,add_data,all_Details,add_supplier,supplier_list
urlpatterns = [
    path('',login_view, name='login'),
    path('home', home, name='home'),
    path('add_supplier', add_supplier, name='add_supplier'),
    path('all_suppliers.html',supplier_list, name='supplier_list'),
    path('all_leads/', all_leads, name='all_leads'),
    path('leads.html', leads, name='leads.html'),
    path('search_orders/', search_orders, name='search_orders'),
    path('search_product/', search_product, name='search_product'),
    path('allcustomers/', allcustomers, name='allcustomers'),
    path('orders.html/', sales_order_view, name='orders'),
    path('products.html/', products, name='products'),
    path('custemers.html/', add_customer, name='add_customer'),
    path('addorder.html/', add_sales_order, name='add_sales_order'),
    path('addproduct.html/', add_orderitem, name='addproduct'),
    path('addvariant.html/',add_itemvariant, name='addvariant'),
    path('customer/delete/', customer_delete, name='deletecustomer'),
    path('order/delete/', order_delete, name='deleteorder'),
    path('product/delete/', product_delete, name='deleteproduct'),
    path('variant/delete/', variant_delete, name='deletevariant'),
    path('allcustomers/updatecustomer.html/<customer_id>/',update_customer, name='updatecustomer'),
    path('search_customers/', search_customers, name='searchcustomers'),
    path('orders/updateorder/<int:order_id>/', update_sales_order, name='update_sales_order'),
    path('products/updateproduct/<int:item_id>/',update_order_item, name='update_orderitem'),
    path('products/updatevariant/<int:variant_id>/',update_item_variant, name='update_variant'),
    path('register/', registration_view, name='register'),
    path('updatepassword.html/', update_password, name='updatepassword'),
    path('logout.html/',logout_view, name='logout_view'),
    path('enterlead.html',add_centred_data, name='enterlead.html'),
    path('searchlead.html', search_lead, name='searchlead'),
    path('leadsview', leadsview, name='leadsview'),
    path('deletelead.html',delete_lead, name='delete_lead'),
    path('updatelead/<int:id>/',updatelead, name='updatelead'),
    path('leadsview/<int:id>/', add_data, name='add_data'),
    path('leaddetail.html', all_Details, name='all_Details'),


    
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
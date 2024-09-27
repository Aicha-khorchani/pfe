from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import  add_itemvariant, add_item, allcustomers, customer_delete, home, add_customer, search_customers, update_password
from .views import update_customer, update_item, variant_delete, update_item_variant,updatesupplier,delete_supplier,addfacture
from .views import logout_view, product_delete, all_items,  login_view, search_product, registration_view, leads,stock,partners
from .views import add_lead,search_lead ,all_leads , delete_lead,updatelead,add_data,all_Details,add_supplier,supplier_list
from .views import delete_retour,update_retour,add_retour,all_retour, doc, search_return ,add_bonreception,update_bonreception,all_bonreception,delete_bonreception,search_bonreception
from .views import invoice,returne,reception


urlpatterns = [
    path('',login_view, name='login'),
    path('home', home, name='home'),
    path('stock', stock, name='stock'),
    path('partners', partners, name='partners'),
    path('addfacture.html', addfacture, name='addfacture'),    
    path('doc', doc, name='doc'),    
    path('invoice', invoice, name='invoice'),    
    path('returne', returne, name='returne'),    
    path('reception', reception, name='reception'),    
    path('add_bonreception', add_bonreception, name='add_bonreception'),
    path('update_bonreception/<int:delivery>', update_bonreception, name='update_bonreception'),
    path('all_bonreception', all_bonreception, name='all_bonreception'),
    path('delete_bonreception', delete_bonreception, name='delete_bonreception'),
    path('search_bonreception', search_bonreception, name='search_bonreception'),   
    path('addretour', add_retour, name='add_retour'),
    path('search_return', search_return , name='search_return'),  
    path('update_retour/<int:retour_id>', update_retour, name='update_retour'),
    path('all_retour', all_retour, name='all_retour'),
    path('delete_retour', delete_retour, name='delete_retour'),
    path('add_supplier', add_supplier, name='add_supplier'),
    path('all_suppliers.html',supplier_list, name='supplier_list'),
    path('all_leads/', all_leads, name='all_leads'),
    path('leads.html', leads, name='leads.html'),
    path('search_product/', search_product, name='search_product'),
    path('allcustomers/', allcustomers, name='allcustomers'),
    path('allproducts.html', all_items, name='all_items'),
    path('custemers.html/', add_customer, name='add_customer'),
    path('addproduct.html/', add_item, name='addproduct'),
    path('addvariant.html/',add_itemvariant, name='addvariant'),
    path('customer/delete/', customer_delete, name='deletecustomer'),
    path('product/delete/', product_delete, name='deleteproduct'),
    path('supplier/delete/', delete_supplier, name='delete_supplier'),
    path('variant/delete/', variant_delete, name='deletevariant'),
    path('allcustomers/updatecustomer.html/<customer_id>/',update_customer, name='updatecustomer'),
    path('search_customers/', search_customers, name='searchcustomers'),
    path('products/update_item/<int:item_id>/',update_item, name='update_item'),
    path('suppliers/update_supplier/<int:supplier_id>/',updatesupplier, name='updatesupplier'),
    path('products/updatevariant/<int:variant_id>/',update_item_variant, name='update_item_variant'),
    path('register/', registration_view, name='register'),
    path('updatepassword.html/', update_password, name='updatepassword'),
    path('logout.html/',logout_view, name='logout_view'),
    path('enterlead.html',add_lead, name='enterlead.html'),
    path('searchlead.html', search_lead, name='searchlead'),
    path('deletelead.html',delete_lead, name='delete_lead'),
    path('updatelead/<int:id>/',updatelead, name='updatelead'),
    path('addleaddata.html', add_data, name='add_data'),
    path('leaddetail.html', all_Details, name='all_Details'),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
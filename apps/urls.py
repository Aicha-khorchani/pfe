from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import  add_itemvariant, add_item, allcustomers, customer_delete, home, add_customer, search_customers, update_password
from .views import update_customer, update_item, variant_delete, update_item_variant,updatesupplier,delete_supplier,admin,notification_view
from .views import logout_view, product_delete, all_items,  login_view, search_product, registration_view, leads,stock,partners
from .views import add_lead,search_lead ,all_leads , delete_lead,updatelead,add_data,all_Details,add_supplier,supplier_list,search_note
from .views import delete_retour,update_retour,add_retour,all_retour, doc, search_return ,add_bonreception,update_bonreception,all_bonreception,delete_bonreception
from .views import invoice,returne,reception,update_facture ,delete_facture,get_all_factures,search_facture,add_facture,get_stock_levels,admin_user_list
from .views import user_list,user_create,user_update,user_delete,admin_user_create,admin_user_delete,admin_user_create,admin_user_update,admin_user_delete
from .views import search_supplier,search_itemvariant,search_bonreception, search_leaddata,add_delivery,update_delivery,get_delivery,delete_delivery,search_delivery
from .views import update_command,search_command,get_command,add_command,delete_command ,livreur_create_view,livreur ,add_note,edit_note,all_notes,delete_note


urlpatterns = [
    path('',login_view, name='login'),
    path('admin',admin, name='admin'),
    path('livreur',livreur, name='livreur'),
    path('add_note',add_note, name='add_note'),
    path('all_notes/', all_notes, name='all_notes'),
    
    path('notification/', notification_view, name='notification_view'),

    path('edit_note/<int:note_id>/', edit_note, name='edit_note'),
    path('delete_note/<int:note_id>/', delete_note, name='delete_note'),
    path('search_note/', search_note, name='search_note'),
    path('admin/create/', admin_user_create, name='admin_user_create'),
    path('update_delivery/<int:delivery_id>/', update_delivery, name='update_delivery'),
    path('get_delivery', get_delivery, name='get_delivery'),
    path('admin/list/', admin_user_list, name='admin_user_list'),    
    path('add_delivery/', add_delivery, name='add_delivery'),
    path('delete_delivery/<int:delivery_id>/', delete_delivery, name='delete_delivery'),
    path('delete_command/<int:Command_id>/', delete_command, name='delete_command'),
    path('update_command/<int:pk>/', update_command, name='update_command'),
    path('search_command/', search_command, name='search_command'),
    path('get_command/', get_command, name='get_command'),
    path('add_command/', add_command, name='add_command'),
    path('search_delivery/', search_delivery, name='search_delivery'),
    path('admin/<int:user_id>/update/', admin_user_update, name='admin_user_update'),
    path('admin/<int:user_id>/delete/', admin_user_delete, name='admin_user_delete'),
    path('users/', user_list, name='user_list'),
    path('users/create/', user_create, name='user_create'),
    path('livreur/create/', livreur_create_view, name='livreur_create_view'),

    path('users/<int:user_id>/edit/', user_update, name='user_update'),
    path('users/<int:user_id>/delete/', user_delete, name='user_delete'),
    path('stock_levels/', get_stock_levels, name='get_stock_levels'), 
    path('home', home, name='home'),
    path('stock', stock, name='stock'),
    path('partners', partners, name='partners'),
    path('addfacture.html', add_facture, name='add_facture'),    
    path('update_facture/<int:facture_id>/', update_facture, name='update_facture'),
    path('delete_facture', delete_facture, name='delete_facture'),
    path('get_all_factures', get_all_factures, name='get_all_factures'),    
    path('search_facture', search_facture, name='search_facture'),  
    path('search_supplier', search_supplier, name='search_supplier'),  
    path('search_leaddata', search_leaddata, name='search_leaddata'),  
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
    path('search_itemvariant/', search_itemvariant, name='search_itemvariant'),
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
    path('search_customers/', search_customers, name='search_customers'),
    path('products/update_item/<int:item_id>/',update_item, name='update_item'),
    path('suppliers/update_supplier/<int:supplier_id>/',updatesupplier, name='updatesupplier'),
    path('products/updatevariant/<int:variant_id>/',update_item_variant, name='update_item_variant'),
    path('register/', registration_view, name='register'),
    path('updatepassword.html/', update_password, name='updatepassword'),
    path('logout.html/',logout_view, name='logout_view'),
    path('enterlead.html',add_lead, name='add_lead'),
    path('searchlead.html', search_lead, name='search_lead'),
    path('deletelead.html',delete_lead, name='delete_lead'),
    path('updatelead/<int:id>/',updatelead, name='updatelead'),
    path('addleaddata.html', add_data, name='add_data'),
    path('leaddetail.html', all_Details, name='all_Details'),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
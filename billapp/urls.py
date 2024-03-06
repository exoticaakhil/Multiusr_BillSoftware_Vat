from django.urls import re_path,path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [

    path('',views.home,name='home'),
    path('cmp_register/',views.cmp_register,name='cmp_register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('change_password/',views.change_password,name='change_password'),
    path('cmp_details/<int:id>/',views.cmp_details,name='cmp_details'),
    path('emp_register/',views.emp_register,name='emp_register'),
    path('dashboard/',views.dashboard,name='dashboard'),
     
    path('register_company/',views.register_company,name='register_company'),  
    path('register_company_details/<int:id>',views.register_company_details,name='register_company_details'),
    path('register_employee/',views.register_employee,name='register_employee'),  
    path('user_login/',views.user_login,name='user_login'),  
    path('cmp_profile/',views.cmp_profile,name='cmp_profile'),  
    path('load_edit_cmp_profile/',views.load_edit_cmp_profile,name='load_edit_cmp_profile'),  
    path('edit_cmp_profile',views.edit_cmp_profile,name='edit_cmp_profile'),  
    path('emp_profile/',views.emp_profile,name='emp_profile'),  
    path('load_edit_emp_profile/',views.load_edit_emp_profile,name='load_edit_emp_profile'),  
    path('edit_emp_profile',views.edit_emp_profile,name='edit_emp_profile'),  
    path('load_staff_request/',views.load_staff_request,name='load_staff_request'),  
    path('load_staff_list/',views.load_staff_list,name='load_staff_list'),  
    path('accept_staff/<int:id>',views.accept_staff,name='accept_staff'),  
    path('reject_staff/<int:id>',views.reject_staff,name='reject_staff'), 
    ######Akhil#####
    path('allbill',views.allbill,name='allbill'), 
    path('purchasebill',views.purchasebill,name='purchasebill'), 
    path('custdata',views.custdata,name='custdata'),
    path('cust_dropdown',views.cust_dropdown,name='cust_dropdown'),  
    path('itemdetails',views.itemdetails,name='itemdetails'), 
    path('item_dropdown',views.item_dropdown,name='item_dropdown'), 
    path('createbill',views.createbill,name='createbill'),
    path('billhistory',views.billhistory,name='billhistory'),
    path('delete_purchasebill/<int:id>',views.delete_purchasebill,name='delete_purchasebill'), 
    path('details_purchasebill/<int:id>',views.details_purchasebill,name='details_purchasebill'),
    path('history_purchasebill/<int:id>',views.history_purchasebill,name='history_purchasebill'),
    path('edit_purchasebill/<int:id>',views.edit_purchasebill,name='edit_purchasebill'),
    path('save_purchasebill/<int:id>',views.save_purchasebill,name='save_purchasebill'),
    path('save_item', views.save_item, name='save_item'),
    path('save_party1', views.save_party1, name='save_party1'),

    path('sharepdftomail/<int:id>',views.sharepdftomail, name='sharepdftomail'),
    path('check_trn_no_exists', views.check_trn_no_exists, name='check_trn_no_exists'),
    path('check_hsn_number_exists', views.check_hsn_number_exists, name='check_hsn_number_exists'),
    path('check_phone_number_exists', views.check_phone_number_exists, name='check_phone_number_exists'),
    path('unit_reload_modal', views.unit_reload_modal, name='unit_reload_modal'),
    path('save_unit', views.save_unit, name='save_unit'),

   
    
 

]

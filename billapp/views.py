from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.models import auth
from django.utils.crypto import get_random_string
import random
from datetime import date
from django.db.models import F
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.http.response import JsonResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.views.generic import View
from io import BytesIO
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages



def home(request):
  return render(request, 'home.html')

def login(request):
  return render(request, 'login.html')

def forgot_password(request):
  return render(request, 'forgot_password.html')

def cmp_register(request):
  return render(request, 'cmp_register.html')

def cmp_details(request,id):
  context = {'id':id}
  return render(request, 'cmp_details.html', context)

def emp_register(request):
  return render(request, 'emp_register.html')

def register_company(request):
  if request.method == 'POST':
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    uname = request.POST['uname']
    phno = request.POST['phno']
    passw = request.POST['pass']
    cpass = request.POST['cpass']
    rfile = request.FILES.get('rfile')

    if passw == cpass:
      if CustomUser.objects.filter(username = uname).exists():
        messages.info(request, 'Sorry, Username already in Use !!')
        return redirect('cmp_register')
      
      elif Company.objects.filter(contact = phno).exists():
        messages.info(request, 'Sorry, Phone Number already in Use !!')
        return redirect('cmp_register')

      elif not CustomUser.objects.filter(email = email).exists():
        user_data = CustomUser.objects.create_user(first_name = fname, last_name = lname, username = uname, email = email, password = passw, is_company = 1)
        cmp = Company( contact = phno, user = user_data, profile_pic = rfile)
        cmp.save()
        return redirect('cmp_details',user_data.id)

      else:
        messages.info(request, 'Sorry, Email already in Use !!')
        return redirect('cmp_register')
      
    messages.info(request, 'Sorry, Passwords must match !!')
    return render(request,'cmp_register.html')
  
def register_company_details(request,id):
  if request.method == 'POST':
    cname = request.POST['cname']
    address = request.POST['address']
    city = request.POST['city']
    state = request.POST['state']
    country = request.POST['country']
    pincode = request.POST['pincode']
    pannumber = request.POST['pannumber']
    gsttype = request.POST['gsttype']
    gstno = request.POST['gstno']

    if Company.objects.filter(pan_number = pannumber).exclude(pan_number='').exists():
      messages.info(request, 'Sorry, Pan number is already in Use !!')
      return redirect('cmp_details',id)
    
    if Company.objects.filter(gst_no = gstno).exclude(gst_no='').exists():
      messages.info(request, 'Sorry, GST number is already in Use !!')
      return redirect('cmp_details',id)

    code=get_random_string(length=6)

    usr = CustomUser.objects.get(id = id)
    cust = Company.objects.get(user = usr)
    cust.company_name = cname
    cust.address = address
    cust.city = city
    cust.state = state
    cust.company_code = code
    cust.country = country
    cust.pincode = pincode
    cust.pan_number = pannumber
    cust.gst_type = gsttype
    cust.gst_no = gstno
    cust.save()
    return redirect('login')

def register_employee(request):
  if request.method == 'POST':
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    uname = request.POST['uname']
    phno = request.POST['phno']
    passw = request.POST['pass']
    cpass = request.POST['cpass']
    ccode = request.POST['ccode']
    rfile = request.FILES.get('rfile')

    if not Company.objects.filter(company_code = ccode).exists():
      messages.info(request, 'Sorry, Company Code is Invalid !!')
      return redirect('emp_register')
    
    cmp = Company.objects.get(company_code = ccode)
    emp_names = Employee.objects.filter(company = cmp).values_list('user',flat=True)
    for e in emp_names:
       usr = CustomUser.objects.get(id=e)
       if str(fname).lower() == (usr.first_name ).lower() and str(lname).lower() == (usr.last_name).lower():
        messages.info(request, 'Sorry, Employee With this name already exits, try adding an initial !!')
        return redirect('emp_register')
    
    if passw == cpass:
      if CustomUser.objects.filter(username = uname).exists():
        messages.info(request, 'Sorry, Username already exists !!')
        return redirect('emp_register')
      
      elif Employee.objects.filter(contact = phno).exists():
        messages.info(request, 'Sorry, Phone Number already in Use !!')
        return redirect('emp_register')

      elif not CustomUser.objects.filter(email = email).exists():
        user_data = CustomUser.objects.create_user(first_name = fname, last_name = lname, username = uname, email = email, password = passw)
        emp = Employee(user = user_data, company = cmp, profile_pic = rfile, contact=phno)
        emp.save()
        return redirect('login')

      else:
        messages.info(request, 'Sorry, Email already exists !!')
        return redirect('emp_register')
      
    messages.info(request, 'Sorry, Passwords must match !!')
    return render(request,'emp_register.html')
  
def change_password(request):
  if request.method == 'POST':
    email= request.POST.get('email')
    if not CustomUser.objects.filter(email=email).exists():
      messages.success(request,'Sorry, No user found with this email !!')
      return redirect('forgot_password')
    
    else:
      otp = random.randint(100000, 999999)
      usr = CustomUser.objects.get(email=email)
      usr.set_password(str(otp))
      usr.save()

      subject = 'Password Reset Mail'
      message = f'Hi {usr.first_name} {usr.last_name}, Your Otp for password reset is {otp}'
      email_from = settings.EMAIL_HOST_USER
      recipient_list = [email ]
      send_mail(subject, message, email_from, recipient_list)
      messages.info(request,'Password reset mail sent !!')
      return redirect('forgot_password')

def user_login(request):
  if request.method == 'POST':
    email = request.POST['email']
    cpass = request.POST['pass']

    try:
      usr = CustomUser.objects.get(email=email)
      log_user = auth.authenticate(username = usr.username, password = cpass)
      if log_user is not None:
        if usr.is_company == 1:
          auth.login(request, log_user)
          return redirect('dashboard')
        else:
          emp = Employee.objects.get(user=usr)
          if emp.is_approved == 0:
            messages.info(request,'Employee is not Approved !!')
            return redirect('login')
          else:
            auth.login(request, log_user)
            return redirect('dashboard')
      messages.info(request,'Invalid Login Details !!')
      return redirect('login')
    
    except:
        messages.info(request,'Employee do not exist !!')
        return redirect('login')
    

def dashboard(request):
  context = {'usr':request.user}
  return render(request, 'dashboard.html', context)

def logout(request):
  auth.logout(request)
  return redirect('/')

def cmp_profile(request):
  cmp = Company.objects.get(user = request.user)
  context = {'usr':request.user, 'cmp':cmp}
  return render(request,'cmp_profile.html',context)

def load_edit_cmp_profile(request):
  cmp = Company.objects.get(user = request.user)
  context = {'usr':request.user, 'cmp':cmp}
  return render(request,'cmp_profile_edit.html',context)

def edit_cmp_profile(request):
  cmp =  Company.objects.get(user = request.user)
  if request.method == 'POST':
    email = request.POST['email']
    current_email = cmp.user.email
    if email != current_email:
      if CustomUser.objects.filter(email=email).exists():
        messages.info(request,'Sorry, Email Already in Use !!')
        return redirect('load_edit_cmp_profile')
      
    phno_list = list(filter(None,Company.objects.exclude(user = request.user).values_list('contact', flat=True)))
    gst_list = list(filter(None,Company.objects.exclude(user = request.user).values_list('pan_number', flat=True)))
    gno_list = list(filter(None,Company.objects.exclude(user = request.user).values_list('gst_no', flat=True)))

    if request.POST['phno'] in phno_list:
      messages.info(request,'Sorry, Phone number already in Use !!')
      return redirect('load_edit_cmp_profile')

    if request.POST['pan'] in gst_list:
      messages.info(request,'Sorry, PAN number already in Use !!')
      return redirect('load_edit_cmp_profile')

    if request.POST['gstnoval'] in gno_list:
      messages.info(request,'Sorry, GST number already in Use !!')
      return redirect('load_edit_cmp_profile')

    cmp.company_name = request.POST['cname']
    cmp.user.email = request.POST['email']
    cmp.user.first_name = request.POST['fname']
    cmp.user.last_name = request.POST['lname']
    cmp.contact = request.POST['phno']
    cmp.address = request.POST['address']
    cmp.city = request.POST['city']
    cmp.state = request.POST['state']
    cmp.country = request.POST['country']
    cmp.pincode = request.POST['pincode']
    cmp.pan_number = request.POST['pan']
    cmp.gst_type = request.POST['gsttype']
    cmp.gst_no = request.POST['gstnoval']
    old=cmp.profile_pic
    new=request.FILES.get('image')
    if old!=None and new==None:
      cmp.profile_pic=old
    else:
      cmp.profile_pic=new
    
    cmp.save() 
    cmp.user.save() 
    return redirect('cmp_profile') 
  
def emp_profile(request):
  emp = Employee.objects.get(user=request.user)
  context = {'usr':request.user, 'emp':emp}
  return render(request,'emp_profile.html',context)

def load_edit_emp_profile(request):
  emp = Employee.objects.get(user=request.user)
  context = {'usr':request.user, 'emp':emp}
  return render(request,'emp_profile_edit.html',context)

def edit_emp_profile(request):
  emp =  Employee.objects.get(user = request.user)
  if request.method == 'POST':
    email = request.POST['email']
    current_email = emp.user.email
    if email != current_email:
      if CustomUser.objects.filter(email=email).exists():
        messages.info(request,'Email Already in Use')
        return redirect('load_edit_emp_profile')
          
    phno_list = list(Employee.objects.exclude(user = request.user).values_list('contact', flat=True))

    if request.POST['phno'] in phno_list:
      messages.info(request,'Sorry, Phone number already in Use !!')
      return redirect('load_edit_emp_profile')

    emp.user.email = request.POST['email']
    emp.user.first_name = request.POST['fname']
    emp.user.last_name = request.POST['lname']
    emp.contact = request.POST['phno']
    old=emp.profile_pic
    new=request.FILES.get('image')
    if old!=None and new==None:
      emp.profile_pic=old
    else:
      emp.profile_pic=new
    
    emp.save() 
    emp.user.save() 
    return redirect('emp_profile') 

def load_staff_request(request):
  cmp = Company.objects.get(user = request.user)
  emp = Employee.objects.filter(company = cmp, is_approved = 0)
  context = {'usr':request.user, 'emp':emp, 'cmp':cmp}
  return render(request,'staff_request.html',context)

def load_staff_list(request):
  cmp = Company.objects.get(user = request.user)
  emp = Employee.objects.filter(company = cmp, is_approved = 1)
  context = {'usr':request.user, 'emp':emp, 'cmp':cmp}
  return render(request,'staff_list.html',context)

def accept_staff(request,id):
  emp = Employee.objects.get(id=id)
  emp.is_approved = 1
  emp.save()
  messages.info(request,'Employee Approved !!')
  return redirect('load_staff_request')

def reject_staff(request,id):
  emp = Employee.objects.get(id=id)
  emp.user.delete()
  emp.delete()
  messages.info(request,'Employee Deleted !!')
  return redirect('load_staff_request')
################Akhil###############
def allbill(request):
    if request.user.is_company:
          cmp = request.user.company
    else:
          cmp = request.user.employee.company
    usr = CustomUser.objects.get(username=request.user) 
   
    itm=PurchaseBill.objects.filter(company=cmp)
    pbill = PurchaseBill.objects.filter(company=cmp).values()
    pbills = PurchaseBill.objects.filter(company=cmp)

    for i in pbill:
      p_history= PurchaseBillTransactionHistory.objects.filter(purchasebill=i['id'],company=cmp).last()
      i['action']=p_history.action
      i['name']=p_history.staff.first_name+" "+p_history.staff.last_name
      i['party']=p_history.purchasebill.party.party_name
    return render(request, 'all_billdetils.html',{'itm':itm,'pbill':pbill,'pbills':pbills,'usr':request.user})
def purchasebill(request):
    if request.user.is_company:
          cmp = request.user.company
    else:
          cmp = request.user.employee.company
    usr = CustomUser.objects.get(username=request.user) 
    party=Party.objects.filter(company=cmp)
    item=Item.objects.filter(company=cmp)
    last_bill = PurchaseBill.objects.filter(company=cmp).order_by('-billno').first()
    if last_bill:
        bill_no = last_bill.billno + 1
    else:
        bill_no = 1
    # print (bill_no)
    context = {
        'bill_no': bill_no,
        'party':party,
        'item':item,
        'usr':request.user
        # Add other context variables as needed
    }
    return render(request, 'createpurchasebill.html',context)
def itemdetails(request):
  itmid = request.GET['id']
  itm = Item.objects.get(id=itmid)
  hsn = itm.itm_hsn
  vat = itm.itm_vat
  price = itm.itm_purchase_price
  qty = itm.itm_stock_in_hand
  # print(vat)
  return JsonResponse({'hsn':hsn, 'vat':vat,  'price':price, 'qty':qty})
def item_dropdown(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company
  options = {}
  option_objects = Item.objects.filter(company=cmp)
  for option in option_objects:
      options[option.id] = [option.itm_name]
  return JsonResponse(options)


def cust_dropdown(request):
    if request.user.is_company:
          cmp = request.user.company
    else:
          cmp = request.user.employee.company
    usr = CustomUser.objects.get(username=request.user) 
    party=Party.objects.filter(company=cmp,user=usr)

    id_list = []
    party_list = []
    for p in party:
      id_list.append(p.id)
      party_list.append(p.party_name)

    return JsonResponse({'id_list':id_list, 'party_list':party_list })


def custdata(request):
  cid = request.POST['id']
  part = Party.objects.get(id=cid)
  phno = part.contact
  address = part.address
  pay = part.payment
  bal = part.openingbalance
  return JsonResponse({'phno':phno, 'address':address, 'pay':pay, 'bal':bal})
def createbill(request):
  if request.method == 'POST': 
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company  
    usr = CustomUser.objects.get(username=request.user)  
    part = Party.objects.get(id=request.POST.get('customername'))
    pbill = PurchaseBill(party=part, 
                          billno=request.POST.get('bill_no'),
                          billdate=request.POST.get('billdate'),
                          subtotal=float(request.POST.get('subtotal')),
                          adjust = request.POST.get("adj"),
                          taxamount = request.POST.get("taxamount"),
                          grandtotal=request.POST.get('grandtotal'),
                          company=cmp,
                          staff=usr
                          )
    pbill.save()
    
        
    product = tuple(request.POST.getlist("product[]"))
    qty =  tuple(request.POST.getlist("qty[]"))
    discount =  tuple(request.POST.getlist("discount[]"))
    tax =  tuple(request.POST.getlist("vat[]"))
    total =  tuple(request.POST.getlist("total[]"))
    billno = PurchaseBill.objects.get(billno=pbill.billno,company=cmp)
    # print(billno)
    if len(product)==len(qty)==len(tax)==len(discount)==len(total):
        mapped=zip(product,qty,tax,discount,total)
        mapped=list(mapped)
        for ele in mapped:
          itm = Item.objects.get(id=ele[0])
          PurchaseBillItem.objects.create(product = itm,qty=ele[1], VAT=ele[2],discount=ele[3],total=ele[4],purchasebill=billno,company=cmp)

    PurchaseBill.objects.filter(company=cmp,staff=usr).update(tot_bill_no=F('tot_bill_no') + 1)
    
    
    pbill.tot_bill_no = pbill.billno
    print(pbill.tot_bill_no)
    pbill.save()

    PurchaseBillTransactionHistory.objects.create(purchasebill=pbill,action='Created',company=cmp,staff=usr)

    if 'Next' in request.POST:
      return redirect('purchasebill')
    
    if "Save" in request.POST:
      return redirect('allbill')
    
  else:
     return redirect('purchasebill')
def billhistory(request):
  pid = request.POST['id']
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  usr = CustomUser.objects.get(username=request.user) 
  pbill = PurchaseBill.objects.get(billno=pid,company=cmp,staff=usr)
  hst = PurchaseBillTransactionHistory.objects.filter(purchasebill=pbill,company=cmp).last()
  name = hst.staff.first_name + ' ' + hst.staff.last_name 
  action = hst.action
  return JsonResponse({'name':name,'action':action,'pid':pid,'usr':request.user})


def delete_purchasebill(request,id):
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  usr = CustomUser.objects.get(username=request.user) 
  pbill = PurchaseBill.objects.get(id=id)
  PurchaseBillItem.objects.filter(purchasebill=pbill,company=cmp).delete()
  pbill.delete()
  
  return redirect('allbill')

def details_purchasebill(request,id):
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  usr = CustomUser.objects.get(username=request.user) 
  pbill = PurchaseBill.objects.get(id=id,company=cmp)
  pitm = PurchaseBillItem.objects.filter(purchasebill=pbill,company=cmp)
  dis = 0
  for itm in pitm:
    dis += int(itm.discount)
  itm_len = len(pitm)

  context={'pbill':pbill,'pitm':pitm,'itm_len':itm_len,'dis':dis,'usr':request.user}
  return render(request,'vatbilldetils.html',context)
def history_purchasebill(request,id):
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company 
  usr = CustomUser.objects.get(username=request.user) 
  pbill = PurchaseBill.objects.get(id=id)
  hst= PurchaseBillTransactionHistory.objects.filter(purchasebill=pbill,company=cmp)

  context = {'hst':hst,'pbill':pbill,'usr':request.user}
  return render(request,'purchasebillhistory.html',context)
def edit_purchasebill(request,id):
  toda = date.today()
  tod = toda.strftime("%Y-%m-%d")
  
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  usr = CustomUser.objects.get(username=request.user) 
  cust = Party.objects.filter(company=cmp)
  item = Item.objects.filter(company=cmp)
  item_units = Unit.objects.filter(company=cmp)

  pbill = PurchaseBill.objects.get(id=id,company=cmp)
  billprd = PurchaseBillItem.objects.filter(purchasebill=pbill,company=cmp)
  bdate = pbill.billdate.strftime("%Y-%m-%d")
  context = { 'pbill':pbill, 'billprd':billprd,'tod':tod,
             'cust':cust, 'item':item, 'item_units':item_units, 'bdate':bdate,'usr':request.user}
  return render(request,'purchasebilledit.html',context)
def save_purchasebill(request,id):
  if request.method =='POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company  

    usr = CustomUser.objects.get(username=request.user) 
    print('haiii')
    print (request.POST.get('customername'))
    part = Party.objects.get(id=request.POST.get('customername'))
    print(part)
    pbill = PurchaseBill.objects.get(id=id, company=cmp)
    print(pbill)

        # Access the related PurchaseBill instance through the ForeignKey


    pbill.party = part
    pbill.billdate = request.POST.get('billdate')
    pbill.subtotal =float(request.POST.get('subtotal'))
    pbill.grandtotal = request.POST.get('grandtotal')
    pbill.taxamount = request.POST.get("taxamount")
    pbill.adjust = request.POST.get("adj")
    pbill.company=cmp
    pbill.save()

    product = tuple(request.POST.getlist("product[]"))
    qty = tuple(request.POST.getlist("qty[]"))
    tax =  tuple(request.POST.getlist("vat[]"))
    total = tuple(request.POST.getlist("total[]"))
    discount = tuple(request.POST.getlist("discount[]"))

    PurchaseBillItem.objects.filter(purchasebill=pbill).delete()
    if len(total)==len(discount)==len(qty)==len(tax):
      mapped=zip(product,qty,tax,discount,total)
      mapped=list(mapped)
      for ele in mapped:
        itm = Item.objects.get(id=ele[0])
        PurchaseBillItem.objects.create(product =itm,qty=ele[1], VAT=ele[2],discount=ele[3],total=ele[4],purchasebill=pbill,company=cmp)

    PurchaseBillTransactionHistory.objects.create(purchasebill=pbill,action='Updated',company=cmp,staff=usr)
    return redirect('allbill')

  return redirect('allbill')

    
def save_item(request):
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    usr = CustomUser.objects.get(username=request.user) 

    if request.method == 'POST':
      itm_type = request.POST.get('itm_type')
      name = request.POST.get('name')
      itm_hsn = request.POST.get('hsn')
      itm_unit = request.POST.get('unit')
      itm_taxable = request.POST.get('taxref')
      itm_vat = request.POST.get('vat')
      itm_sale_price = request.POST.get('sell_price')
      itm_purchase_price = request.POST.get('cost_price')
      itm_stock_in_hand = request.POST.get('stock ', 0)  # Default to 0 if not provided
      itm_at_price = request.POST.get('itmprice ', 0)  # Default to 0 if not provided
      itm_date = request.POST.get('itmdate')

      # Check if the HSN number already exists in the database
      if Item.objects.filter(itm_hsn=itm_hsn,company=cmp).exists():
          # Send a message indicating that the HSN number already exists
          messages.error(request, 'HSN number already exists!')
          return redirect('createbill')
      print(name)
      print(itm_type)
      print(itm_hsn)
      print(itm_taxable)
      itm = Item(
          user=usr,
          company=cmp,
          itm_type=itm_type,
          itm_name=name,
          itm_hsn=itm_hsn,
          itm_unit=itm_unit,
          itm_taxable=itm_taxable,
          itm_vat=itm_vat,
          itm_sale_price=itm_sale_price,
          itm_purchase_price=itm_purchase_price,
          itm_stock_in_hand=itm_stock_in_hand,
          itm_at_price=itm_at_price,
          itm_date=itm_date
      )
      itm.save()

      return JsonResponse({'success': True})
    
def save_party1(request):
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    usr = CustomUser.objects.get(username=request.user)

    if request.method == 'POST':
        partyname = request.POST.get('partyname')
        trn_no = request.POST.get('trn_no')
        contact = request.POST.get('contact')
        trn_type = request.POST.get('trn_type')
        address = request.POST.get('address')
        email = request.POST.get('email')
        balance = request.POST.get('balance')
        paymentType = request.POST.get('paymentType')
        currentdate = request.POST.get('currentdate')
        additionalfield1 = request.POST.get('additionalfield1')
        additionalfield2 = request.POST.get('additionalfield2')
        additionalfield3 = request.POST.get('additionalfield3')
        # print(trn_no)
        # print(partyname)

        # Check if the contact number already exists in the database
        if Party.objects.filter(contact=contact,company=cmp).exists():
            # Send a message indicating that the contact number already exists

            return redirect('createbill')

        # Check if the transaction number already exists in the database
        if trn_type == "Unregistered/Consumers":
            party = Party.objects.create(    user=usr,
            company=cmp,
            party_name=partyname,
            trn_no=trn_no,
            contact=contact,
            trn_type=trn_type,
            address=address,
            email=email,
            openingbalance=balance,
            payment=paymentType,
            current_date=currentdate,
            additionalfield1=additionalfield1,
            additionalfield2=additionalfield2,
            additionalfield3=additionalfield3)
            # Optionally, you can send a success message here

            return redirect('createbill')
        else:
             if Party.objects.filter(trn_no=trn_no, company=cmp).exists():
                # Send a message indicating that the transaction number already exists

                return redirect('createbill')
        Party.objects.create(
            user=usr,
            company=cmp,
            party_name=partyname,
            trn_no=trn_no,
            contact=contact,
            trn_type=trn_type,
            address=address,
            email=email,
            openingbalance=balance,
            payment=paymentType,
            current_date=currentdate,
            additionalfield1=additionalfield1,
            additionalfield2=additionalfield2,
            additionalfield3=additionalfield3
        )
        return redirect('createbill')
def sharepdftomail(request,id):
 if request.user:
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']
                

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                if request.user.is_company:
                  cmp = request.user.company
                else:
                  cmp = request.user.employee.company  
                usr = CustomUser.objects.get(username=request.user)
                # print(emails_list)
                pbill = PurchaseBill.objects.get(id=id,company=cmp)
                pitm = PurchaseBillItem.objects.filter(purchasebill=pbill)
                dis = 0
                for itm in pitm:
                  dis += int(itm.discount)
                itm_len = len(pitm)
                context={'pbill':pbill,'pitm':pitm,'itm_len':itm_len,'dis':dis}
                template_path = 'vatpdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
                pdf = result.getvalue()
                filename = f'Purchase bill - {pbill.billno}.pdf'
                subject = f"Purchase bill - {pbill.billno}"
                email = EmailMessage(subject, f"Hi,\nPlease find the Purchase bill- Bill-{pbill.billno}. \n{email_message}\n\n--\nRegards,\n{pbill.company.company_name}\n{pbill.company.address}\n - {pbill.company.city}\n{pbill.company.contact}", from_email=settings.EMAIL_HOST_USER,to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                msg = messages.success(request, 'purchase bill has been shared via email successfully..!')
                return redirect(details_purchasebill,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(details_purchasebill, id)
def check_trn_no_exists(request):
    trn_no = request.GET.get('trn_no')
    trn_type = request.POST.get('trn_type')
    print(trn_type)
    if trn_type != "Unregistered/Consumers":
      if Party.objects.filter(trn_no=trn_no).exists():
          return JsonResponse({'exists': True})
      return JsonResponse({'exists': False})

def check_phone_number_exists(request):
    phone_number = request.GET.get('phone_number')
    if Party.objects.filter(contact=phone_number).exists():
        return JsonResponse({'exists': True})
    return JsonResponse({'exists': False})



   


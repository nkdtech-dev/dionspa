from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json 
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST

''' email verification  imports '''
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
import threading

from user_client.task import *
### importing django background tasks for background data handling
# Create your views here.

''' view reservations from the employee view '''
from django.core.paginator import Paginator

@login_required(login_url='LoginRegister')
@csrf_exempt
def employee_view(request):
    reservations = Reservations.objects.all()

    # Create a list to store reservations with details
    reservations_with_details = []

    # Iterate through each reservation
    for reservation in reservations:
        # Load reservation details from JSONField
        res_details = json.loads(reservation.res_details)
        
        # Append the reservation and its details to the list
        reservations_with_details.append((reservation, res_details))

    # Handle search functionality
    query = request.GET.get('search')
    if query:
        # Filter reservations by username containing the search query
        reservations_with_details = [
            (reservation, res_details)
            for reservation, res_details in reservations_with_details
            if query.lower() in reservation.client_reserve.username.lower()
        ]

    ### used to print out  desired number of reservations for a page
    reservations_per_page = 1  # You can adjust this as needed

    paginator = Paginator(reservations, reservations_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'reservations_with_details': reservations_with_details,
        'reservations_test': page, 
    }
    
    return render(request, 'user_client/employee_view.html', context) 



def sum_price(location_details):
    total_price = int(location_details['formula_price'])
    for cats, itemss in location_details['activities'].items():
        for item, price in itemss.items():
            total_price = total_price + int(price)
    return total_price

def home(request):
    return render(request,'user_client/index.html')

# threading used to work with API's to create a better respond to the backend
class EmailThread(threading.Thread):

    def init(self, email):
        self.email = email
        threading.Thread.init(self)

    def run(self):
        self.email.send()


''' lOGOUT function '''

def log_out(request):
    request.session.clear()
    logout(request)
    messages.success(request, "You have successfully logged out!!")
    return redirect('home')


'''' Resending  or Regenerating new confirmation email '''
def resend_activation_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:

            user = User.objects.get(email=email)
            user_1 = User_data.objects.get(user_email=email)

            # trying to activate the user 
            if user_1.user_activation == False:
                current_site = get_current_site(request)
                email_subject = "Confirm your Email @ LilOspa Login!!"
                message = render_to_string('email_confirmation.html', {
                    'name': user.first_name,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': generate_token.make_token(user)
                })
                email = EmailMessage(
                    email_subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                # if not settings.PAYMENT_IDING:
                #     email.send()
                send_email_fun.delay(email_subject, message, settings.EMAIL_HOST_USER,user.email)
                messages.info(request, "A new activation link has been sent to your email.")
                return redirect('LoginRegister')
            else:
                messages.error(request, "Your account is already active.")
                return redirect('LoginRegister')
        except User.DoesNotExist:
            messages.error(request, "Account not found.")
            return redirect('LoginRegister')

    return render(request, 'user_client/resend_activation.html')




@login_required(login_url='LoginRegister')
def remove_item(request):
     #### calling instance of session for further process #######
    book_details = request.session.get('book_details', {})

    #### calling the session to get the data for further processing #######
    ReservationDetails = request.session.get('reservation_data', {})

    total_price = 0


    if request.method == "POST":
        if 'paybutton' in request.POST:
            
            total_price = sum_price(reservation=ReservationDetails)
            
            return redirect('home')
        try:
            item = request.POST.get("item")
            price = request.POST.get("price")
            category = request.POST.get("category")
            if item in ReservationDetails[category]:
                del ReservationDetails[category][item]
                total_price = sum_price(ReservationDetails)

            
        except:
            pass
        response_data = {"message": "Item removed successfully"}
        return JsonResponse(response_data)
    
    return JsonResponse({"message": "Invalid request"}, status=400)




########################## start  reservation ############################
@csrf_exempt
def reserveDate(request):
    book_details = {}
    request.session['token'] = 1
    try:
        if request.method == 'POST':
            if 'homesubmit' in request.POST:
                selected_date = request.POST.get('datetime')  # Get the selected dat
                num_seats = request.POST.get('Guest') 
            else:
                data = json.loads(request.body.decode('utf-8'))
                selected_date = data.get('date')
                
                num_seats = data.get('dropdownValue')
            book_details  = {
                    'reserve_date': selected_date,
                    'num_seats': num_seats,
                    
                    }
            request.session['book_date'] = book_details
            return redirect('ChooseLocation')
    except:
        pass

    return render(request,'user_client/reserve.html')

#### first we get the request.session['book_details'] to store the number of people
#### and their reservation date

@csrf_exempt
def ChooseLocation(request):
    if request.session.get('book_date',{}):

        try:
            mouscron = mouscronLocation.objects.all()
            tournai = tournaiLocation.objects.all()
            mouscronDetails = {}
            tournaiDetails ={}
            
            for room in mouscron:
                mouscronDetails['location_name'] = 'Mouscron'
                mouscronDetails['pictures'] ={
                    f'{room.room_name}pic1' : room.room_picture1.url,
                    f'{room.room_name}pic2' : room.room_picture2.url,
                    f'{room.room_name}pic3' : room.room_picture3.url
                }            
            for room in tournai:
                tournaiDetails['location_name'] = 'Tournai'
                tournaiDetails['pictures'] = {
                    f'{room.room_name}pic1' : room.room_picture1.url,
                    f'{room.room_name}pic2' : room.room_picture2.url,
                    f'{room.room_name}pic3' : room.room_picture3.url
                }

            context = {'mouscronlocation':mouscronDetails,'tournailocation':tournaiDetails}
            if request.method == "POST":
                try:
                    data = json.loads(request.body)
                    location_name = data.get('location', '')
                    request.session['locationName'] = location_name
                    return redirect('chooseRoom')
                except:
                    pass 
        except:
            pass
        print(request.session.get('book_date'))
        return render(request, 'user_client/choose_location.html',context)
    else:
        return redirect('reserveDate')


@csrf_exempt
def chooseRoom(request):
    if request.session.get('locationName'):
        try:
            locationName = request.session.get('locationName', '')
            roomDetails = {}
            if locationName =='Tournai':
                rooms = tournaiLocation.objects.all()
            elif locationName =='Mouscron':
                rooms = mouscronLocation.objects.all()

            for room in rooms:
                roomDetails[room.room_name] = {
                    'room_picture1': room.room_picture1.url,
                    'room_picture2': room.room_picture2.url,
                    'room_picture3': room.room_picture3.url,

                }

            ######## initialising a session ########
            request.session['roomDetails'] = roomDetails


            if request.method == "POST":
                try:
                    data = json.loads(request.body)
                    room_name = data.get('room', '')
                    ######## inititializing another session to store the roome name
                    request.session['roomname'] = room_name 
                    print('test',room_name)
                    return redirect('ChooseTime')


                except:
                    pass  # Use "name" instead of "locationName"
        except:
            pass
        context = {'roomDetails': request.session.get('roomDetails', {}), 'locationName': request.session.get('locationName', '')}

        return render(request, 'user_client/choose_room.html', context)
    else:
        return redirect('ChooseLocation')

@csrf_exempt
def ChooseTime(request):
    print(request.session.get('roomname'))
    if request.session.get('roomname'):
        try: 
            location_details = {
            'location': request.session.get('locationName', ''),
            'room': request.session.get('roomname', ''),
            'date':request.session.get('book_date', {})['reserve_date'],
            'seats':request.session.get('book_date', {})['num_seats'],
            # 'time': request.session.get('reserve_time', '')

            } 
            available_timeslots = []
            store = []   # USED TO STORE ANY RESERVED TIMESLOTS FOR THESAME DAY
            if Reservations.objects.exists():
                for reservation in Reservations.objects.all():
                    obj = reservation.res_details
                    # we convert the instance of the class to a json to ease querying 
                    obj = json.loads(obj)
                    if obj['location'] == request.session.get('locationName', '') and obj['room'] == request.session.get('roomname', '') and obj['date'] == request.session.get('book_date', {})['reserve_date']:
                            print(obj['location'])
                            rooName = request.session.get('roomname', '')

                            if obj['location'] =='Tournai':
                                timeslot = tournaiLocation.objects.get(room_name=rooName)
                                available_timeslots = timeslot.room_time.split(',')
                                ### first we convert the data to string
                                get_time = str(obj['time'])
                                #### then we get the index of the time after it has been stripped
                                # final = available_timeslots.index(s.strip("[]'"))
                                store.append(get_time)

                            elif obj['location'] =='Mouscron':
                                timeslot = mouscronLocation.objects.get(room_name=rooName)                            
                                available_timeslots = timeslot.room_time.split(',')
                                get_time = str(obj['time'])
                                # final = available_timeslots.index(s.strip("[]'"))
                                store.append(get_time)
                    
                    else:
                        rooName = request.session.get('roomname', '')
                        locationName = request.session.get('locationName', '')
                        if locationName == 'Tournai':
                            roomobj = tournaiLocation.objects.get(room_name=rooName)
                        elif locationName == 'Mouscron':
                            roomobj = mouscronLocation.objects.get(room_name=rooName)
                        available_timeslots = roomobj.room_time.split(',')
            else:               
                    rooName = request.session.get('roomname', '')
                    locationName = request.session.get('locationName', '')
                    if locationName == 'Tournai':
                        roomobj = tournaiLocation.objects.get(room_name=rooName)                   
                    elif locationName == 'Mouscron':
                        roomobj = mouscronLocation.objects.get(room_name=rooName)
                    
                    available_timeslots = roomobj.room_time.split(',')
        
            if request.method == "POST":
                try:
                    data = json.loads(request.body)
                    reserve_time = data.get('reserved_time', '')

                    ########### initialising another session for time picking ###########
                    request.session['reserve_time'] = reserve_time
                    return redirect('Formula')
                except:
                    pass
                    print('something not working')

        except Exception as e:
            pass   
        
        ######## this function is to delete all the timeslots that were already reserved
        context = {'available_timeslots': json.dumps(available_timeslots),'reserved_time': json.dumps(store),'roomname':request.session.get('roomname', '')}
        return render(request, 'user_client/timeslots.html', context)
    else:
        return redirect('chooseRoom')


@csrf_exempt
def Formula_view(request):
    if request.session.get('reserve_time'):
        formula_name = ''
        formulas = Formula.objects.all()
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                formula_name = data.get('formula', '').split(':')[0]
                formula_price = data.get('formula','').split(":")[1]
                print(formula_name)
                
                request.session['formula_name'] = formula_name
                request.session['formula_price'] = formula_price
                return redirect('ReserveService')
            except Exception as e:
                print(e, 'this')
        else:
            pass
        context = {'formula':formulas}        
        return render(request, 'user_client/formula.html', context)
    else:
        return redirect('ChooseTime')

@csrf_exempt
def update_selected_items(request):
    
    selected_items =''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_items = data.get('selected_items', {})
            request.session['reservation_data'] = selected_items
            
            return JsonResponse({'message': 'Data received successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data.'}, status=400)
        
    return JsonResponse({'message': 'Invalid request method.'}, status=400, selected_items=selected_items )

@csrf_exempt
def ReserveService(request):
    if request.session.get('formula_name'):
        drinks = Drinks.objects.all()
        hygiene = Hygien.objects.all()
        meals = Meals.objects.all()
        Activities = activities.objects.all()
        context = {
            'drinks': drinks,
            'hygienes': hygiene,
            'meals': meals,
            'activities': Activities
        }


        location_details = {
                        'location': request.session.get('locationName', ''),
                        'room': request.session.get('roomname', ''),
                        'date':request.session.get('book_date', {})['reserve_date'],
                        'seats':request.session.get('book_date', {})['num_seats'],
                        'time': request.session.get('reserve_time', ''),
                        'formula_name': request.session.get('formula_name', ''),
                        'formula_price': request.session.get('formula_price', ''),
                        'activities': request.session.get('reservation_data', {})

                    }
        request.session['location_details'] = location_details       
        
        return render(request, 'user_client/reserve_servce.html', context)
    else:
        return redirect('Formula')


@login_required(login_url='LoginRegister')
def payment_processing(request):
    if request.method == 'POST':
        try:
            total_price = request.POST.get('payment')
            print(total_price)
            request.session['amount'] = total_price
            response_data = {
                'message': 'Payment successful',
            }
            return JsonResponse(response_data)
            
        except Exception as e:
            response_data = {
                'message': 'Payment failed: ' + str(e),
            }
            return JsonResponse(response_data, status=500)  # Return an error response
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)  # Return a bad request response



''' viewing the reserve template '''

@login_required(login_url='LoginRegister')
def profile_view(request):
    location_details = {
                    'location': request.session.get('locationName', ''),
                    'room': request.session.get('roomname', ''),
                    'date':request.session.get('book_date', {})['reserve_date'],
                    'seats':request.session.get('book_date', {})['num_seats'],
                    'time': request.session.get('reserve_time', ''),
                    'formula_name': request.session.get('formula_name', ''),
                    'formula_price': request.session.get('formula_price', ''),
                    'activities': request.session.get('reservation_data', {})

                }
    
  
    ### calling session for the reservations details
    ReservationDetails = dict(location_details)
    total_price = sum_price(location_details)
    ### condition to check if price is doubled for the corresponding
    if request.session.get('book_date', {})['num_seats'] == 2:
        total_price *= 2
    request.session['amount'] = total_price
    context = {'reservations': ReservationDetails,'total_price':total_price}

    if request.session.get('token','') == 1:
        if request.user.is_authenticated:
            username = request.user.username
            user_id = request.user.id

            ### used for storing in the reservation table
            save = Reservations.objects.create(client_reserve = request.user ,res_details=json.dumps(ReservationDetails),payment_amount = request.session.get('amount'))
            ### used for displaying the reservation table from the database
            reservations = Reservations.objects.filter(client_reserve=request.user)
            del request.session['token']
            print('sssssssssss saved only once')

            return render(request, 'user_client/confirmResevations.html',context)
        
    else:
        print('no more saving')
    return render(request, 'user_client/confirmResevations.html',context)

    print('test',request.session.get('token',''))

''' User login and signUP most logic here'''
@csrf_exempt
def LoginRegister(request):

    ReservationDetails = ''
    #### calling the session to get the data for further processing #######
    try:
        location_details = {
                        'location': request.session.get('locationName', ''),
                        'room': request.session.get('roomname', ''),
                        'date':request.session.get('book_date', {})['reserve_date'],
                        'seats':request.session.get('book_date', {})['num_seats'],
                        'time': request.session.get('reserve_time', ''),
                    'formula_name': request.session.get('formula_name', ''),
                    'formula_price': request.session.get('formula_price', ''),
                        'activities': request.session.get('reservation_data', {})

                    }
        ReservationDetails = dict(location_details)
    except:
        pass

    
    ### calling session for the reservations details
    
    if request.method == 'POST':
       
        # Check if it's a login or signup form
        if 'loginButton' in request.POST:
            # Handle login logic
            email = request.POST.get('email')
            password = request.POST.get('loginPasword')
            
            try:
                users = User.objects.get(email=email)
                username = users.username
              
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                        ### Testing if the credentials inputed are that of the employee
                        if employee.objects.filter(user_employee=user).exists():
                                messages.success(request, "signed in as Employee!!")
                                login(request,user) 
                                return render(request, 'user_client/employee_home.html')
                        

                        test = User_data.objects.get(user_data=user)
                        if test.user_activation == False:
                            s = 1
                            messages.info(request, "Your account has not been activated, please activate your account")
                            context = {'activation_check': s}
                            return render(request,'user_client/loginRegister.html',context)
                        
                    # ''' this is a code to check if the user is credentials are that of employee or not'''
                        
                            ## if he is not of type employee, he signs in as a normal user
                        else:
                                messages.success(request, f"Welcome {user.username} ")
                                login(request,user) 

                                # condition to check if the user was already making some reservations or not 
                        if not request.session.get('reservation_data', {}):
                            
                                return redirect('home')
                            # else he is redirected home
                        else:
                                context = {'reservations': ReservationDetails, 'usernames':username}
                                # saving to the database
                                save = Reservations.objects.create(client_reserve = user ,res_details=json.dumps(ReservationDetails))

                                return render(request, 'user_client/confirmResevations.html',context )
                        # else we check if the user credentials are wrong
                else:
                        messages.error(request, "Invalid Login Credentials!! ")
                        return render(request, 'user_client/loginRegister.html')

            except User.DoesNotExist:
                messages.error(request, "Invalid Login Credentials!! ")

            
        elif 'signupbutton' in request.POST:
            # Handle signup logic
            # Extract data from POST
            fname = request.POST.get('fname')
            tel = request.POST.get('phone')
            countrycode = request.POST.get('countryCode')
            email = request.POST.get('signupEmail')
            password =request.POST.get('signupPassword')
            phone = '(+' +''+ countrycode +')' +' '+ tel
            print(phone)

            ### Check if the email is already in use

            try:
             
                if User.objects.filter(email=email).exists():
                    messages.error(request,"Email OR USERNAME already exists!!")
                   
                    return redirect('LoginRegister')
                else:
                 
                    myuser = User.objects.create_user(username= fname , email=email,password=password)
                    user_client = User_data.objects.create(user_data=myuser, user_name=fname,user_number=phone, user_email=email, user_password=password)
                    myuser.fname = fname
                    myuser.save()
                    user_client.save()
                    
                    subject = "Welcome to Lil'Ospa Login!!"
                    message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Lil'Ospa!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nLil'Ospa Team"        
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [myuser.email]

                    # Email Address Confirmation Email
                    current_site = get_current_site(request)
                    email_subject = "Confirm your Email @ LilOspa Login!!"
                    message2 = render_to_string('email_confirmation.html',{
                    
                        'name': myuser.first_name,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                        'token': generate_token.make_token(myuser)
                            })
                    email = EmailMessage(
                            email_subject,
                            message2,
                            settings.EMAIL_HOST_USER,
                            [myuser.email],
                            )
                    send_email_fun.delay(email_subject, message2, settings.EMAIL_HOST_USER,myuser.email)

                    # if not settings.PAYMENT_IDING:
                    #    email.send() 

                   
                    if not request.session.get('reservation_data', {}):
                            messages.info(request,"Please check your email to confirm Account") 
                            # special_logout(request)  
                            return redirect('home')
                    else:
                            messages.info(request, " Please check your email to confirm Account") 
                            # special_logout(request)  
                            return render(request, 'user_client/loginRegister.html')
            except Exception as e:
                print(e)
                return redirect('LoginRegister')
       
        
        
                   
    
            # Redirect to some success page
    content = {'check':ReservationDetails}
        
    return render(request, 'user_client/loginRegister.html',content)

''' used for email activation '''

def activate(request,uidb64,token):
    ReservationDetails = ''
    ### calling session for the reservations details
    try:
        location_details = {
                        'location': request.session.get('locationName', ''),
                        'room': request.session.get('roomname', ''),
                        'date':request.session.get('book_date', {})['reserve_date'],
                        'seats':request.session.get('book_date', {})['num_seats'],
                        'time': request.session.get('reserve_time', ''),
                    'formula_name': request.session.get('formula_name', ''),
                    'formula_price': request.session.get('formula_price', ''),
                        'activities': request.session.get('reservation_data', {})

                    }
        ReservationDetails = dict(location_details)
    except:
        pass
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        set_active = User_data.objects.get(user_data=myuser)
        set_active.user_activation = True
        set_active.save()
        # user.profile.signup_confirmation = True

        myuser.save()
        myuser.backend = 'django.contrib.auth.backends.ModelBackend'  
        login(request, myuser)
        messages.success(request, "Your account has been confirmed!!")
        if not request.session.get('reservation_data', {}):
            return redirect('home')
        else:
            messages.success(request, "Your account has been confirmed!!")
            context = {'reservations': ReservationDetails, 'ID':myuser.id}
            save = Reservations.objects.create(client_reserve = myuser,res_details=json.dumps(ReservationDetails))
            return render(request,'user_client/confirmResevations.html',context)
    else:
        
        return render(request,'user_client/activation_failed.html')


 ###### getting the payment ##


### for Users to view their own reservations
@login_required(login_url='LoginRegister')
def user_view_reservations(request,pk):
    # Get the user's reservations
    user = request.user
    reservations_with_details = []
    user_reservations = Reservations.objects.filter(client_reserve=user)
    for reservation in user_reservations:
        res_details = json.loads(reservation.res_details)
        reservations_with_details.append((reservation, res_details))

    context = {
        'reservations_with_details': reservations_with_details,
    }

    return render(request, 'user_client/view_reservations.html', context)

##################### used to delete User reservations ###########
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse


@login_required(login_url='LoginRegister')
def delete_reservation(request, res_id):
    reservation = get_object_or_404(Reservations, res_id=res_id)
    reservation.delete()
    key = request.user
    redirect_url = reverse('view_reservations', args=[key.id])
    return redirect(redirect_url)


######### used to view user policy ########
def privacy_policy(request):
    return render(request, 'user_client/terms.html')



PAYMENT_ID = ''
RESERVATION_ID = ''
@login_required(login_url = 'LoginRegister')
@csrf_exempt
@require_POST
def initiate_payment(request):
    global PAYMENT_ID,RESERVATION_ID
    print('test')
    if request.method == "POST":
        try:
            CURRENCY = 'EUR'
            CHARGES = 1.68
            amount = 0
            latest_record = Reservations.objects.latest('timestamp')
            request.session['new_payment_id'] = str(latest_record.res_id)
            store = json.loads(latest_record.res_details)
            redirect_url = request.build_absolute_uri(reverse('payment_status'))
            price = float(request.session.get('amount'))
            print(store['seats'])
            if int(store['seats']) == 2:
               
                # Perform the multiplication
                amount_for_2 = (price* 2 )-(0.1 * 2 * price)
                #Round the result to 2 decimal places
                amount = round(amount_for_2)
                print(amount)
            else:
                print('else there')
                amount = price
            print('entering')
            amount+=CHARGES
            mollie_client = Client()
            mollie_client.set_api_key("test_9jPz6AGpNG7KS9DSTTgSUcaTTa2MFG")
            latest_record.payment_amount = (amount-CHARGES)
            latest_record.save()
            payment = mollie_client.payments.create({
                'amount': {
                    'currency': 'EUR',
                    'value': str(amount),
                },
                'description': 'Order #' + str(latest_record.res_id),
                'redirectUrl': redirect_url,
                'webhookUrl':'https://71b6-154-72-153-217.ngrok-free.app/mollie-webhooks/',
            })
        
            # Save the payment ID in the session for later reference
            
            request.session['payment_id'] = payment.id
            PAYMENT_ID = request.session.get('payment_id','')
            RESERVATION_ID = request.session.get('new_payment_id','')
            print('entered last')
            return redirect(payment.checkout_url)
        except:
            return HttpResponse(status=400)
        
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from mollie.api.client import Client
from mollie.api.error import Error

@require_POST
@csrf_exempt
def mollie_webhook(request):
    global PAYMENT_ID,RESERVATION_ID
    if request.method == 'POST':
        try:
            mollie_client = Client()
            mollie_client.set_api_key("test_9jPz6AGpNG7KS9DSTTgSUcaTTa2MFG")
            print('Entering mollie webhook') 
            print(PAYMENT_ID)
            if not PAYMENT_ID or not RESERVATION_ID:
                return HttpResponse(status=400)
            mollie_payment = mollie_client.payments.get(PAYMENT_ID)
            if mollie_payment.is_paid():
                # Save the payment ID in your database for future reference
                print(RESERVATION_ID)
                latest_record = Reservations.objects.filter(res_id = RESERVATION_ID).first()
                latest_record.payment_id = PAYMENT_ID
                latest_record.payment_status = True
                latest_record.save()
                messages.success(request,'Payment completed successfully')
            # Handle other payment statuses if needed
            # Example: Handle pending, open, or canceled payments
            elif mollie_payment.is_pending():
                # Handle pending payment
                messages.info(request, 'Your payment is pending')
            elif mollie_payment.is_open():
                # Handle open payment
                pass  # You can add logic here if need
            else:
                # Handle canceled payment
                messages.error(request, 'Your payment has been cancelled')
                
        except:
            return HttpResponse(status=400)
    return HttpResponse(status=200)


@login_required(login_url='LoginRegister') 
def payment_success(request):
    return render(request, 'user_client/payment_succesful.html')

## paying from the reserve page
def complete_payment(request):
    reservation_id = request.GET.get('payment_id')
    payment_amount = request.GET.get('price')

    # creating sessions for payment details
    request.session['new_payment_id'] = reservation_id
    request.session['new_amount'] = payment_amount
    return redirect('payment_complete')


## paying the order from the payment page
@login_required(login_url = 'LoginRegister')
@csrf_exempt
def pay_complete(request):
        global PAYMENT_ID,RESERVATION_ID
        try:
            CHARGES = 1.68
            amount = 0
            redirect_url = request.build_absolute_uri(reverse('payment_status'))
            price = float(request.session.get('new_amount'))
            amount = price
            amount+=CHARGES
            mollie_client = Client()
            mollie_client.set_api_key("test_9jPz6AGpNG7KS9DSTTgSUcaTTa2MFG")
            
            payment = mollie_client.payments.create({
                'amount': {
                    'currency': 'EUR',
                    'value': str(amount),
                },
                'description': 'Order #' + str(request.session.get('new_payment_id')),
                'redirectUrl': redirect_url,
                'webhookUrl':'https://71b6-154-72-153-217.ngrok-free.app/mollie-webhooks/',
            })
            request.session['payment_id'] = payment.id
            PAYMENT_ID = request.session.get('payment_id','')
            RESERVATION_ID = request.session.get('new_payment_id','')

            return redirect(payment.checkout_url)
        except:
            return HttpResponse(status=400)


# used for rendering the giftcard
@login_required(login_url='LoginRegister')
def show_giftcard(request):
    return render(request, 'user_client/giftcard.html')

# views.py



@login_required(login_url='LoginRegister')
def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        print(name,email,subject,message)
        test = email
        recipients = ['info@lileospa.com',]
        msg_mail = str(message)+" " + "\n\n"+ "user sender email: " +str(email)
        send_mail(
            subject,
            msg_mail, 
            email, 
            recipients,
            fail_silently=False,
        )

        # Return a JSON response
        return JsonResponse({'message': 'Email sent successfully'})

    return render(request, 'user_client/contact_us.html')

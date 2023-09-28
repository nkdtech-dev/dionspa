
from celery import shared_task
from django.core.mail import send_mail
import time
from django.db.models import Q
@shared_task(serializer='json', name="send_mail")
def send_email_fun(subject, message, sender, receiver):
    time.sleep(10) # for check that sending email process runs in background 
    send_mail(subject, message, sender, [receiver])

# tasks.py
from datetime import timedelta,datetime
from django.utils import timezone
from user_client.models import Reservations

@shared_task
def delete_old_records():
    two_days_ago = timezone.now() - timedelta(days=2)
    # check that there are no records older than 2 days that were not paid
    Reservations.objects.filter(Q(timestamp__lt=two_days_ago) & Q(payment_status = False)).delete()

@shared_task
def delete_records():
    thirty_days_ago = timezone.now() - timedelta(days=30)
    # check that there are no records older than 30 days that were not paid
    Reservations.objects.filter(timestamp__lt=thirty_days_ago).delete()

### scheudule to remind users of their reservtions 


from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
from .models import Reservations  # Import your Reservations model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import json
@shared_task
def send_reservation_reminder():
    # Calculate the date one day from now
    tomorrow = timezone.now() + timedelta(days=1)
    
    # Get reservations that match the condition (1 day before)
    reservations = Reservations.objects.filter(payment_status = True)
    for reservation in reservations:
        store = json.loads(reservation.res_details)
        target_date = datetime.strptime(store['time'], '%m/%d/%Y')
        one_day_before = target_date - timedelta(days=1)
        current_date = timezone.now().date()
        if current_date == one_day_before.date():
            user = reservation.client_reserve
            subject = "Reservation Reminder"
            message = f"Hi {user.username}, your reservation is tomorrow. Don't forget!"
            
            # You can customize the email content here
            # You might want to use a template and load it with your context
            # Create an HTML email
            html_message = render_to_string('email_template.html', {'user': user})
            
            # Create a plain text version of the email
            plain_message = strip_tags(html_message)
            
            # Sender's email address (you may need to configure your email settings)
            from_email = settings.EMAIL_HOST_USER
            
            # Recipient's email address
            to_email = user.email
            
            # Send the email
            send_mail(
                subject,
                plain_message,
                from_email,
                [to_email],
                html_message=html_message
            )

#### used to notify users about payment reminders
@shared_task
def send_payment_reminders():
    # Find reservations with payment_status=False older than 24 hours
    unpaid_reservations = Reservations.objects.filter(payment_status=False)

    for reservation in unpaid_reservations:
        # Send payment reminder email
        subject = 'Payment Reminder'
        user = reservation.client_reserve
        message = 'This is a friendly reminder to complete your payment.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = user.email

        html_message = render_to_string('payment_reminder.html', {'reservation': reservation})
        plain_message = strip_tags(html_message)

        print(recipient_list)
         # Render the HTML content using your template
        
        # Create the EmailMessage instance and attach the HTML content
        send_mail(subject,plain_message,from_email, [recipient_list], html_message=html_message)

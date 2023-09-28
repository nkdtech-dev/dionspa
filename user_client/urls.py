from django.urls import path
from user_client import views
from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)


urlpatterns = [
    path('',views.home, name='home'),
    path('loginGoogle/', views.login, name='index'),
    path ('reserveDate/', views.reserveDate, name='reserveDate'),
    path ('contact_us/', views.contact_us, name='contact_us'),
    path ('ReserveService/', views.ReserveService, name='ReserveService'),
    path('update_selected_items/', views.update_selected_items, name='update_selected_items'),
    path('loginregister/', views.LoginRegister, name='LoginRegister'),
    path('confirmReservation/', views.profile_view, name='confirmReservation'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('logout/', views.log_out, name='logout'),
    path('employee-view/', views.employee_view, name='employee-view'),
    
    # resending activation link
    path('resend_activation/', views.resend_activation_email, name='resend_activation'),

    # password reset
    path('password-reset/', PasswordResetView.as_view(template_name='user_client/password_reset.html'),name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='user_client/reset_password_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='user_client/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='user_client/password_reset_complete.html'),name='password_reset_complete'),
    path('logout/', LogoutView.as_view(next_page='login'),name='logout'),
    path('remove_item/', views.remove_item, name='remove_item'),
    path('ChooseLocation/', views.ChooseLocation, name="ChooseLocation"),
    path('ChooseTime/', views.ChooseTime, name="ChooseTime"),
    path('chooseRoom/', views.chooseRoom, name="chooseRoom"),
    path('Formula/', views.Formula_view, name="Formula"),

    ## for user to view his reservations
    path('view_reservations/<str:pk>/', views.user_view_reservations, name="view_reservations"),
   ### delete reservations by user
    path('delete_reservation/<uuid:res_id>/',views.delete_reservation, name='delete_reservation'),
    path('terms/', views.privacy_policy, name='policy'),
    path('makepayments/',views.payment_processing, name='makepayments'),
    # path('pay/',views.pay, name='pay'),
    # path('pay-for-2/',views.pay_2, name = 'pay_for_2'),

    # for payment intergration
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    # used for payment checking weburl
    path('mollie-webhooks/', views.mollie_webhook, name='mollie_webhook'),
    # payment succesful page
    path('payment-status/', views.payment_success, name='payment_status'),

    path('complete-payment/', views.complete_payment, name='complete_payment'),
    # to initiate payment
    path('payment-complete', views.pay_complete, name='payment_complete'),
    path('giftcard/', views.show_giftcard, name='giftcard')
]


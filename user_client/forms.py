from django.forms import ModelForm
from .models import *
''' used to create input fields needed by the user client '''

class UserClientForm(ModelForm):
    class Meta:
        model = User_data
        fields = ['user_name', 'user_email', 'user_password', 'user_number', 'user_DOB','user_gender']
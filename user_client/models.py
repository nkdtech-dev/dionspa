from django.db import models
import uuid
from django.contrib.auth.models import User



# Create your models here.
# Create your models here.
from PIL import Image

def resize_image(image_field, max_size):
    if image_field:
        img = Image.open(image_field.path)
        img.thumbnail(max_size)
        img.save(image_field.path)




GENDER_CHOICES =    (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)




"""First class implies creating a user class needed for clients if they dont have
social accounts and can easily book reservations """
# TODO 1: User class
class User_data(models.Model):


    # creating the reltionship with the default django user class
    user_data = models.OneToOneField(User, on_delete=models.CASCADE,null=True)

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    user_name = models.CharField(max_length=50)
    user_email = models.EmailField(max_length=50)
    user_number = models.CharField(max_length=50 , null=True , blank=True, default='None')
    user_gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True,default='other')
    user_password = models.CharField(max_length=50)

    user_activation = models.BooleanField(default=False,null=True,blank=True)
    user_DOB = models.DateField(null=True ,blank=True,default=None)

    def __str__(self):
        return self.user_name
    
    
"""This class is for employee here by which they can easily handle the 
or monitor the reservations ordered by the clients"""

class employee(models.Model):
    user_employee = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    emp_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    emp_name = models.CharField(max_length=50)
    emp_email = models.EmailField(max_length=50,default='dionslilospa@gmail.com')
    emp_password= models.CharField(max_length=50)
    def __str__(self):
        return self.emp_name
    
    # USED FOR ADDING THE VARIOUS APPOINTMENTS 
class appointment(models.Model):
    app_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    emp_id = models.ForeignKey(employee, on_delete=models.CASCADE)
    app_date = models.DateField()

    # --------------------------------------------------------APPOINTMENT classes---------------------------------
class Drinks(models.Model):
    drinl_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    drink_name = models.CharField(max_length=50)
    drink_price = models.IntegerField()
    drink_type = models.CharField(max_length=50)
    drink_image = models.ImageField(null=True, blank = True, default='default.png')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.drink_image, (256, 256))
    
    def __str__(self):
        return self.drink_name

class Hygien(models.Model):
    hyg_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    hyg_name = models.CharField(max_length=50)
    hyg_price = models.IntegerField()
    hyg_time = models.CharField(max_length=50,blank=True,null=True)
    hyg_des = models.CharField(max_length=200,null=True)
    hyg_imge = models.ImageField(null=True, blank = True, default='default.png')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.hyg_imge, (256, 256))

    def __str__(self):
        return self.hyg_name

########## meals ####################

class Meals(models.Model):
    meal_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    meal_name = models.CharField(max_length=50)
    meal_price = models.IntegerField()
    meal_type = models.CharField(max_length=50)
    meal_image = models.ImageField(null=True, blank = True, default='default.png')
    meal_des = models.CharField(max_length=200,null=True,blank=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.meal_image, (256, 256))


    def __str__(self):
        return self.act_name

class Reservations(models.Model):
    client_reserve = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    res_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    res_details = models.JSONField()

    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(null=True, blank=True,default='null')
    payment_amount = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    check_people = models.CharField(default='half paid')

    def __str__(self):
        return str(self.created)


############ class rooms ###################
def default_tournai():
    return '11:30AM - 1:15 PM,2:00 PM - 3:45 PM,4:30 PM - 6:15 PM,7:00 PM - 8:45 PM,9:30 PM - 11:15 PM'

class tournaiLocation(models.Model):
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    room_name = models.CharField(max_length=50,null=True, blank=True)
    room_picture1 = models.ImageField(null=True, blank = True, default='default.png')
    room_picture2 = models.ImageField(null=True, blank = True, default='default.png')
    room_picture3 = models.ImageField(null=True, blank = True, default='default.png')
    room_time = models.CharField(default=default_tournai)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.room_picture1, (421, 226))
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.room_picture2, (421, 226))
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.room_picture3, (421, 226))

    def __str__(self):
        return str(self.room_name)


#### room 2 ####################
def default_mouscron():
    return '11:30AM - 1:15 PM,2:00 PM - 3:45 PM,4:30 PM - 6:15 PM,7:00 PM - 8:45 PM,9:30 PM - 11:15 PM'

            

class mouscronLocation(models.Model):

    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    room_name = models.CharField(max_length=50,null=True,blank=True)
    room_picture1 = models.ImageField(null=True, blank = True, default='default.png')
    room_picture2 = models.ImageField(null=True, blank = True, default='default.png')
    room_picture3 = models.ImageField(null=True, blank = True, default='default.png')
    room_time = models.CharField(default=default_mouscron)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.room_picture1, (421, 226))
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.room_picture2, (421, 226))
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.room_picture3, (421, 226))

    def __str__(self):
        return str(self.room_name)


class activities(models.Model):
    act_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    act_name = models.CharField(max_length=50)
    act_price = models.IntegerField()
    act_time = models.CharField(max_length=50,null=True,blank=True) 
    act_des = models.CharField(max_length=200, null=True)
    act_image = models.ImageField(null=True, blank = True, default='default.png')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.act_image, (256, 256))
    

    def __str__(self):
        return self.act_name

##############   formula for service  #############

class Formula(models.Model):
    formula_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    formula_name = models.CharField(max_length=50)
    formula_price = models.IntegerField()
    formula_image = models.ImageField(null=True, blank = True, default='default.png')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.formula_image, (400, 200))

    def __str__(self):
        return self.formula_name
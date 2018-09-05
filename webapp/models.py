from django.db import models
from django.contrib.auth.models import AbstractUser
<<<<<<< HEAD
import datetime
=======
>>>>>>> 65e64f29cb305c7a26d9e7e55d0aacdd8cf9adf4

# Create your models here.
class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_prof = models.BooleanField(default=False)
    is_ra= models.BooleanField(default=False)
class signup_table(models.Model):
    username=models.CharField(max_length=200)
    email=models.CharField(max_length=300,null=True)
    role=models.IntegerField(null=True)
    def __str__(self):
        return self.username
class blog(models.Model):
    title=models.CharField(max_length=255,null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural="Blog"
class mobile_phone(models.Model):
    mobile_companny= models.CharField(max_length=200, null= True)
    mobile_name= models.CharField(max_length=300)
    price=models.IntegerField()
    rating=models.CharField(max_length=300)
    description=models.TextField()
    def __str__(self):
        return self.mobile_companny
    class Meta:
        verbose_name_plural="mobile_phone"
        
class phone(models.Model):
    Mobile_Companny= models.CharField(max_length=200, null= True)
    Mobile_Name= models.CharField(max_length=300, null= True)
    Whats_new= models.TextField( null= True)
    OS=models.CharField(max_length=300, null= True)
    Dimensions=models.CharField(max_length=300, null= True)
    Weight=models.CharField(max_length=100, null= True)
    Colors=models.CharField(max_length=300, null= True)
    Cpu=models.CharField(max_length=500, null= True)
    Chip=models.CharField(max_length=500, null= True)
    Gpu=models.CharField(max_length=500, null= True)
    Size=models.CharField(max_length=300, null= True)
    Resolution=models.CharField(max_length=500, null= True)
    price=models.IntegerField( null= True)
    rating=models.CharField(max_length=300, null= True)
    image_path=models.CharField(max_length=300, null=True)
    def __str__(self):
        return self.Mobile_Companny
    class Meta:
        verbose_name_plural="phone"
class samsung_phone(models.Model):
    Mobile_Companny= models.CharField(max_length=200, null= True)
    Mobile_Name= models.CharField(max_length=300, null= True)
    Whats_new= models.TextField( null= True)
    Chip=models.CharField(max_length=500, null= True)  
    Colors=models.CharField(max_length=300, null= True) 
    Cpu=models.CharField(max_length=500, null= True)
    Dimensions=models.CharField(max_length=300, null= True)
    Gpu=models.CharField(max_length=500, null= True)
    Resolution=models.CharField(max_length=500, null= True)
    Size=models.FloatField(null=True)
    Weight=models.IntegerField(null= True)
    price=models.IntegerField( null= True)
    rating=models.FloatField(null= True)
    OS=models.CharField(max_length=300, null= True)
    imagepath1=models.CharField(max_length=300,null=True)
    imagepath2=models.CharField(max_length=300,null=True)
    battery=models.CharField(max_length=400,null=True)
    back_camera=models.CharField(max_length=400,null=True)
    def __str__(self):
        return self.Mobile_Name
    class Meta:
        verbose_name_plural="samsungphone"
class sort_feature(models.Model):
    f_id=models.IntegerField(null=True)
    feature=models.CharField(max_length=200,null=True)
    position=models.IntegerField(null=True)
    sh_hd=models.IntegerField(null=True)
    roles=models.IntegerField(null=True)

    def __str__(self):
        return self.feature
    class Meta:
<<<<<<< HEAD
        verbose_name_plural="Sort Feature"
=======
        verbose_name_plural="sort feature"
>>>>>>> 65e64f29cb305c7a26d9e7e55d0aacdd8cf9adf4
class feature(models.Model):
    feature=models.CharField(max_length=200,null=True)
    def __str__(self):
        return self.feature
    class Meta:
<<<<<<< HEAD
        verbose_name_plural="feature"

class userscoreRecord (models.Model):
    column_id=models.IntegerField(null=True)
    element_id=models.IntegerField(null=True)
    feat_priority=models.IntegerField(null=True)
    feat_name=models.CharField(max_length=200,null=True)
    mobile_id=models.IntegerField(null=True)
    user_id=models.IntegerField(null=True)
    date_created= models.DateField(("Date"), default=datetime.date.today)
    date_modified = models.DateField(("Date"), default=datetime.date.today)
    def __str__(self):
        return self.feat_name
    class Meta:
        verbose_name_plural="User Score Record"


    
=======
        verbose_name_plural="sort feature"

>>>>>>> 65e64f29cb305c7a26d9e7e55d0aacdd8cf9adf4

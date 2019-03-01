from django.db import models
from django.db.models import CharField, Model
from django_mysql.models import ListCharField
from django.contrib.auth.models import AbstractUser
from django_mysql.models import ListCharField,ListTextField


import datetime

# Create your models here.

class Role(models.Model):
    
    role_name=models.CharField(max_length=45)
 
    def __str__(self):
        return self.role_name
    class Meta:
        verbose_name_plural="Role"
        ordering=['pk']

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_prof = models.BooleanField(default=False)
    is_ra= models.BooleanField(default=False)
    platform_admin= models.BooleanField(default=False)
    experiment_admin=models.BooleanField(default=False)
    role_id = models.ForeignKey(Role, on_delete=models.CASCADE,default=None,null=True)
    custom_id=models.CharField(max_length=100,unique=True,default=None,null=True,blank=True)
    def __str__(self):
        userStr = str(self.custom_id) + ": " + str(self.username)
        return userStr

class templates(models.Model):
    template_name=models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    update_at = models.DateTimeField(auto_now_add=True, blank=True)
    def __str__(self):
        return self.template_name
    class Meta:
        verbose_name_plural="Templates"
    
class template_roles(models.Model):
    role_id = models.ForeignKey(Role, on_delete=models.CASCADE,default=None,null=True)
    template_id = models.ForeignKey(templates, on_delete=models.CASCADE,default=None,null=True)
    can_add=models.BooleanField(default=True)
    can_view=models.BooleanField(default=True)
    can_edit=models.BooleanField(default=True)
    can_del=models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    update_at = models.DateTimeField(auto_now_add=True, blank=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        verbose_name_plural="Template Roles"
        
class platform_feature(models.Model):
    feature_name=models.CharField(max_length=100,null=True,blank=True)
    feature_symbol=models.CharField(max_length=3,null=True)
    feature_levels = ListCharField(
        base_field=models.CharField(max_length=20),
        size=6,
        max_length=(6 * 21), # 6 * 10 character nominals, plus commas
        null=True,
        blank=True
    )

    #feature_levels=models
    def __str__(self):
        return self.feature_name
    class Meta:
        verbose_name_plural="platform_feature"
        ordering = ['pk']

class  experiment(models.Model):
    status = models.CharField(max_length=100,default='DESIGN_MODE')
    """
    STATUS LEVELS:
     DESIGN_MODE = Under Construction
     READY = Design complete but login not shared with Subjects
     OPEN = READY + login shared
     ACTIVE = Subject(s) are undergoing experiment
     INACTIVE = Partially completed but no Subjects
     CLOSED = No longer accepting Subjects - awaiting analysis
     SUSPENDED = Not accepting Subjects - 
                 but could be reopened - some design changes (such as cap change) allowed
     CANCELLED = Abandoned - not accepting subjects ever
     ANALYZED = Analysis Reports 
    """
    custom_exp_id=models.CharField(max_length=100,null=True,blank=True,unique=True)
    batches_title=models.CharField(max_length=100, null=True, blank=True)
    # subj_id_field=models.CharField(max_length=100, null=True, blank=True)
    # subj_email_field=models.CharField(max_length=100, null=True, blank=True)
    # subj_subdetail=ListCharField(
    #     base_field=CharField(max_length=20),
    #     size=10,
    #     max_length=(10*21)
    # )
    capacity=models.IntegerField(default=100, null=True, blank=True)
    #DONE 24/10/2018 as ManyToMany: NEED ADD ADMIN ID AS A FOREIGN KEY
    admin=models.ManyToManyField(to=User, related_name='can_modify')
    #right now on delete will throw a PROTECT error, but
    #we should TODO change this to SET_DEFAULT once we can 
    #identify which user is to be DEFAULT platform admin.
    owner=models.ForeignKey(User, on_delete=models.PROTECT, related_name='creator')
    inFile=models.CharField(max_length=256,null=True,blank=True)
    outFile=models.CharField(max_length=256,null=True,blank=True)
    def __str__(self):
        return self.custom_exp_id
    class Meta:
        verbose_name_plural="experiment"
        ordering = ['pk']

class Batch(models.Model):
     exp = models.ForeignKey(experiment, on_delete=models.CASCADE)
     batch_label= models.CharField(max_length=100, null=True, blank=True)

class Block(models.Model):
    #The Experiment Id where it is used
    used_in = models.ForeignKey(experiment, on_delete=models.CASCADE)
    #So if there are 16 blocks, the serial_no will be a number from 1-16
    #This should help recompile a tuple list if needed later, to ensure order
    serial_no = models.IntegerField()
    levels_set = ListCharField(
        base_field=CharField(max_length=20),
        size=10,
        max_length=(10*21)
    )
    def __str__(self):
        blockStr = str(self.serial_no).zfill(2)+": "+str(self.levels_set)
        return blockStr
    class Meta:
        #verbose_name_plural="block"
        ordering = ['pk']

class Subject(models.Model):
    #NOTE: I HAVE CHANGED SUBJECT TO ONLY HAVE USER AS FK
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exp = models.ForeignKey(experiment, on_delete=models.CASCADE)
    batch = models.CharField(max_length=100, null=True, blank=True) #ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    block = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=100)
    def __str__(self):
        return str(self.user.custom_id)

class experiment_feature(models.Model):
    used_in = models.ForeignKey(experiment, on_delete=models.CASCADE)
    p_feature = models.ForeignKey(platform_feature, on_delete=models.CASCADE)
    chosen_levels = ListCharField(
         base_field=models.CharField(max_length=20),
         size=6,
         max_length=(6 * 21) # 6 * 10 character nominals, plus commas
    )
    def __str__(self):
        fName = self.p_feature.feature_name
        return fName
    
class exp_fLevel(models.Model):
    e_feature = models.ForeignKey(experiment_feature, on_delete=models.CASCADE)
    chosen_level = models.CharField(max_length=100)
    def __str__(self):
        fLevel = self.chosen_level 
        return fLevel

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
        
class mobilephones(models.Model):
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
    # changed from price_in_pkr
    price=models.IntegerField( null= True)
    price_in_usd=models.IntegerField( null= True)
    rating=models.FloatField(null= True)
    OS=models.CharField(max_length=300, null= True)
    # imagepath1 = models.ImageField(null=True, blank=True, upload_to="webapp/img/sampleimages/")
    # imagepath2=  models.ImageField(null=True, blank=True, upload_to="webapp/img/sampleimages/")
    imagepath1=models.CharField(max_length=300,null=True)
    imagepath2=models.CharField(max_length=300,null=True)
    battery=models.CharField(max_length=400,null=True)
    # changed from back_camera
    backcam=models.CharField(max_length=400,null=True)
    
    def __str__(self):
        return self.Mobile_Name
    
    class Meta:
        verbose_name_plural="mobilephones"
        

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
    price_in_pkr=models.IntegerField( null= True)
    price_in_usd=models.IntegerField( null= True)
    rating=models.FloatField(null= True)
    OS=models.CharField(max_length=300, null= True)
    imagepath1=models.CharField(max_length=300,null=True)
    imagepath2=models.CharField(max_length=300,null=True)
    battery=models.CharField(max_length=400,null=True)
    back_camera=models.CharField(max_length=400,null=True)

    def __str__(self):
        return self.Mobile_Name
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural="samsungphone"
class sort_feature(models.Model):
    f_id=models.IntegerField(null=True)
    feature=models.CharField(max_length=200,null=True)
    position=models.IntegerField(null=True)
    sh_hd=models.IntegerField(null=True)
    # roles=models.IntegerField(null=True)
    roles = models.ForeignKey(Role, on_delete=models.CASCADE,default=None,null=True)


    def __str__(self):
        return self.feature
    class Meta:
        verbose_name_plural="Sort Feature"

class feature(models.Model):
    feature=models.CharField(max_length=200,null=True)
    def __str__(self):
        return self.id
    class Meta:

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
class prunedmobilephones(models.Model):
    u_id=models.IntegerField(null=True)
    m_id=models.IntegerField(null=True)
    roles=models.IntegerField(null=True)
    def __str__(self):
        return self.u_id
    class Meta:
       verbose_name_plural="Pruned Mobile Phones"

class userroles(models.Model):
    userrole=models.CharField(max_length=200,null=True)

class selectedAdminPhones(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exp = models.ForeignKey(experiment, on_delete=models.CASCADE)
    batch_label=models.CharField(max_length=200,null=True)
    mob = models.ForeignKey(mobilephones, on_delete=models.CASCADE)

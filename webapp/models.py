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
    default_levels=ListCharField(
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
class exStatusCd(models.Model):
    status_name=models.CharField(max_length=100,null=True,blank=True)
    status_code=models.IntegerField()
    s_description=models.TextField(null=True,blank=True)
    def __str__(self):
        return self.status_name
    class Meta:
        verbose_name_plural="ExpStatusCode"
        ordering = ['pk']
DEFAULT_EXAM_ID=1
class  experiment(models.Model):

    status = models.CharField(max_length=100,default='DESIGN_MODE')
    status_code=models.ForeignKey(exStatusCd,on_delete=models.CASCADE,default=DEFAULT_EXAM_ID)
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
     HOLD = Not accepting Subjects - non-design - experiment admin issue 
    """
    custom_exp_id=models.CharField(max_length=100,null=True,blank=True)
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
    desc=models.CharField(max_length=256,null=True,blank=True)
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

class exp_fdefaults(models.Model):
    used_in = models.ForeignKey(experiment, on_delete=models.CASCADE)
    d_feature = models.ForeignKey(platform_feature, on_delete=models.CASCADE)
    default_level = models.CharField(max_length=20)
    def __str__(self):
        fName = self.p_feature.feature_name
        return fName
    class Meta:
        verbose_name_plural="Exp Default Feature"


class experiment_feature(models.Model):
    used_in = models.ForeignKey(experiment, on_delete=models.CASCADE)
    p_feature = models.ForeignKey(platform_feature, on_delete=models.CASCADE)
    chosen_levels = ListCharField(
        base_field=models.CharField(max_length=20),
        size=6,
        max_length=(6 * 21), # 6 * 10 character nominals, plus commas
        null=True,
        blank=True,
    )
    default_levels= ListCharField(
        base_field=models.CharField(max_length=20),
        size=6,
        max_length=(6 * 21), # 6 * 10 character nominals, plus commas
        null=True,
        blank=True,
   )
    # default_levels=models.CharField(max_length=50,null=True,blank=True)

    def __str__(self):
        fName = self.p_feature.feature_name
        return fName
    
class exp_fLevel(models.Model):
    used_in = models.ForeignKey(experiment, on_delete=models.CASCADE,null=True,blank=True)
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

        
class mobilephones(models.Model):
    Brand= models.CharField(max_length=200, null= True)
    Mobile_Name= models.CharField(max_length=300, null= True)
    Whats_new= models.TextField( blank=True,null= True)
    price=models.FloatField( null= True,blank=True)
    Memory=models.CharField(max_length=500, null= True,blank=True)
    Ram=models.CharField(max_length=500, null= True,blank=True)
    Cpu=models.CharField(max_length=500, null= True)
    Dimensions=models.CharField(max_length=300, null= True)
    Gpu=models.CharField(max_length=500, null= True)
    Resolution=models.CharField(max_length=500, null= True)
    Size=models.FloatField(null=True)
    Weight=models.IntegerField(null= True)
    Chip=models.CharField(max_length=500, null= True)  
    Colors=models.CharField(max_length=300, null= True) 
    # changed from price_in_pkr
   
    price_in_usd=models.IntegerField( blank=True,null= True)
    rating=models.FloatField(blank=True,null= True)
    OS=models.CharField(max_length=300, null= True)
    # imagepath1 = models.ImageField(null=True, blank=True, upload_to="webapp/img/sampleimages/")
    # imagepath2=  models.ImageField(null=True, blank=True, upload_to="webapp/img/sampleimages/")
    imagepath1=models.CharField(max_length=300,null=True,blank=True)
    sideimage1=models.CharField(max_length=300,null=True,blank=True)
    sideimage2=models.CharField(max_length=300,null=True,blank=True)
    sideimage3=models.CharField(max_length=300,null=True,blank=True)
    sideimage4=models.CharField(max_length=300,null=True,blank=True)

    # changed from back_camera
    battery=models.CharField(max_length=400,null=True)
    backcam=models.CharField(max_length=400,null=True)
 
    
    def __str__(self):
        return self.Mobile_Name
    
    class Meta:
        verbose_name_plural="mobilephones"
class MobilePhones_Test(models.Model):
    Mobile_Companny= models.CharField(max_length=200, null= True)
    Mobile_Name= models.CharField(max_length=300, null= True)
    Whats_new= models.TextField( null= True)
    price=models.IntegerField( null= True)
    battery=models.CharField(max_length=400,null=True)
   
    Cpu=models.CharField(max_length=500, null= True)
    Dimensions=models.CharField(max_length=300, null= True)
    Gpu=models.CharField(max_length=500, null= True)
    Resolution=models.CharField(max_length=500, null= True)
    Size=models.FloatField(null=True)
    Weight=models.IntegerField(null= True)
    Chip=models.CharField(max_length=500, null= True)  
    Colors=models.CharField(max_length=300, null= True) 
    # changed from price_in_pkr
   
    price_in_usd=models.IntegerField( null= True)
    rating=models.FloatField(null= True)
    OS=models.CharField(max_length=300, null= True)
    # imagepath1 = models.ImageField(null=True, blank=True, upload_to="webapp/img/sampleimages/")
    # imagepath2=  models.ImageField(null=True, blank=True, upload_to="webapp/img/sampleimages/")
    imagepath1=models.CharField(max_length=300,null=True)
    imagepath2=models.CharField(max_length=300,null=True)
    
    # changed from back_camera
    backcam=models.CharField(max_length=400,null=True)
 
    
    def __str__(self):
        return self.Mobile_Name
    
    class Meta:
        verbose_name_plural="Mobile Phones Test"

class criteria_catalog_disp(models.Model):
    
        catalog_crit_display_order=ListCharField(
        base_field=CharField(max_length=20),
        size=10,
        max_length=(10*21),
        null=True
    )
        exp = models.ForeignKey(experiment, on_delete=models.CASCADE,null=True,blank=True)


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
# This Model is not used anywhere now. 
class sort_feature(models.Model):
    f_id=models.IntegerField(null=True)
    feature=models.CharField(max_length=200,null=True)
    position=models.IntegerField(null=True)
    sh_hd=models.IntegerField(null=True)
    # roles=models.IntegerField(null=True)
    roles = models.ForeignKey(Role, on_delete=models.CASCADE,default=None,null=True)
    exp_sets=models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.feature
    class Meta:
        verbose_name_plural="Sort Feature"

class subjectScoreInExperiment(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    subject=models.ForeignKey(Subject, on_delete=models.CASCADE,null=True,blank=True)
    exp=models.ForeignKey(experiment, on_delete=models.CASCADE,null=True,blank=True)
    score=ListCharField(
        base_field=models.CharField(max_length=20),
        size=10,
        max_length=(10*21),
        null=True,
        blank=True
    )



class userroles(models.Model):
    userrole=models.CharField(max_length=200,null=True)

class selectedAdminPhones(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    exp = models.ForeignKey(experiment, on_delete=models.CASCADE,null=True,blank=True)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, null=True,blank=True)
    pset_id = models.CharField(max_length=10,null=True,blank=True)
    mob = models.ForeignKey(mobilephones, on_delete=models.CASCADE,null=True,blank=True)
    p_order = models.IntegerField(null=True,blank=True)

class PhoneCriteria(models.Model):
    criteria_name=models.CharField(max_length=20,null=True)
    status=models.CharField(max_length=20,null=True)
    priority=models.CharField(max_length=20,null=True)
    position=models.IntegerField(null=True)
    def __str__(self):
        return self.criteria_name
    class Meta:
       verbose_name_plural="Phone Criteria"


class ExpCriteriaOrder(models.Model):
    exp = models.ForeignKey(experiment, on_delete=models.CASCADE,null=True)
    block = models.ForeignKey(Block, on_delete=models.CASCADE,null=True,blank=True)
    cOrder_id = models.CharField(max_length=25,null=True)
    fvp=models.CharField(max_length=25,null=True)
    #NEED TO KEEP A RECORD OF THE EXISTING SET OF AVAILABLE CRITERIA IN THE MOBILE PHONES TABLE
    pCriteria = models.ForeignKey(PhoneCriteria, on_delete=models.CASCADE,null=True)

    # pCriteria = models.CharField(max_length=200, null=True)
    position = models.IntegerField(null=True)

    sh_hd=models.IntegerField(null=True)
class StoreHoverBarChartLogs(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    value=models.FloatField(null=True,blank=True)
    phone_name=models.CharField(max_length=45,null=True,blank=True)
    time=models.CharField(max_length=100,null=True,blank=True)
class StoreHoverPieChartLogs(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    value=models.FloatField(null=True,blank=True)
    criteria_name=models.CharField(max_length=45,null=True,blank=True)
    time=models.CharField(max_length=100,null=True,blank=True)
class StoreNextPrevButtonLogs(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    button_name=models.CharField(max_length=45,null=True,blank=True)
    time=models.CharField(max_length=100,null=True,blank=True)
    phone_name=models.CharField(max_length=45,null=True,blank=True)

class StoreCritWeightLogs(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    value=models.FloatField(null=True,blank=True)
    criteria_name=models.CharField(max_length=45,null=True,blank=True)
    time=models.CharField(max_length=100,null=True,blank=True)

class generalCriteriaData(models.Model):
    criteria = models.ForeignKey(PhoneCriteria, on_delete=models.CASCADE,null=True,blank=True)
    valuelist=ListCharField(
        base_field=models.CharField(max_length=20),
        size=10,
        max_length=(10*21),
        null=True,
        blank=True
    )
    inputtype=models.CharField(max_length=20,default="-")
class customExpSessionTable(models.Model):
    expid=models.IntegerField(null=True,blank=True)
    cusexpid=models.CharField(null=True,blank=True,max_length=100)
    status=models.CharField(null=True,blank=True,max_length=20)

class surveyForm(models.Model):
    exp = models.ForeignKey(experiment, on_delete=models.CASCADE,null=True,blank=True)
    surveydata=ListCharField(
        base_field=models.CharField(max_length=300),
        size=30,
        max_length=(300*50),
        null=True,
        blank=True
    )
    # resultdata=ListCharField(
    #     base_field=models.CharField(max_length=30),
    #     size=10,
    #     max_length=(10*40),
    #     null=True,
    #     blank=True
    # )
class criteriaBasicInfo(models.Model):
    criteria_name=models.CharField(null=True,blank=True,max_length=100)
    basic_info=models.TextField(null=True,blank=True)
    more_detail=models.TextField(null=True,blank=True)
    
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.admin import ImportExportActionModelAdmin

from .models import User,MobilePhones_Test
from .models import signup_table,blog,mobilephones,experiment
from .models import samsung_phone,sort_feature,userscoreRecord,Role,platform_feature
from .models import selectedAdminPhones,PhoneCriteria,exStatusCd,exp_fdefaults
from .models import Subject,experiment_feature,Batch,Block,ExpCriteriaOrder,criteria_catalog_disp,generalCriteriaData

from .models import StoreHoverBarChartLogs,StoreHoverPieChartLogs,StoreNextPrevButtonLogs,StoreCritWeightLogs
class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': (
             'is_student',
             'is_prof',
             'is_ra',
             'platform_admin',
             'experiment_admin',
             'role_id',
             'custom_id',
             )}),

    )
class ExpCriteriaOrderResource(resources.ModelResource):
    class meta:
        model=ExpCriteriaOrder
class ExpCriteriaOrderAdmin(ImportExportActionModelAdmin):
    list_display=('id','exp','cOrder_id','pCriteria','fvp','position','sh_hd')

class PhoneCriteriaResource(resources.ModelResource):
    class meta:
        model=PhoneCriteria



class PhoneCriteriaAdmin(ImportExportActionModelAdmin):
    list_display=('id','criteria_name','status','priority','position')

class ExperimentAdmin(admin.ModelAdmin):
    list_display= ('id','custom_exp_id','status','status_code','batches_title',"desc")


class SubjectAdmin(admin.ModelAdmin):
    
    list_display=("user","exp","block")
class experiment_featureAdmin(admin.ModelAdmin):
    list_display= ('id','used_in','p_feature','chosen_levels',"default_levels")

class exStatusCdResourse(resources.ModelResource):
    class meta:
        model=exStatusCd
class exStatusCdAdmin(ImportExportActionModelAdmin):
    list_display=('id',"status_name","status_code","s_description")


class exp_fdefaultsResourse(resources.ModelResource):
    class meta:
        model=exp_fdefaults
class exp_fdefaultsAdmin(ImportExportActionModelAdmin):
    list_display=('id',"used_in","d_feature","default_level")


#----------------------------------------------------------------------------

# platform_feature resource
class platformResource(resources.ModelResource):
    class meta:
        model=platform_feature
#platform_feature admin
class PlatformFeatureAdmin(ImportExportActionModelAdmin):
    list_display= ('id', 'feature_name','feature_symbol','feature_levels',"default_levels")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
#----------------------------------------------------------------------------

# samsung_phone Resource
class samsung_phone_Resource(resources.ModelResource):
    class meta:
        model=samsung_phone
# samsung_phone admin
class SamsungAdmin(ImportExportActionModelAdmin):
    pass

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# 
class MobilePhones_Test_Resource(resources.ModelResource):
    class meta:
        model=MobilePhones_Test
class MobilePhones_TestAdmin(ImportExportActionModelAdmin):
    pass
 
#----------------------------------------------------------------------------

class roleResource(resources.ModelResource):
    class meta:
        model=Role
class RoleAdmin(ImportExportActionModelAdmin):
    list_display= ('id', 'role_name')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
#----------------------------------------------------------------------------
class selectedAdminPhonesResource(resources.ModelResource):
    class meta:
        model=selectedAdminPhones
class selectedAdminPhones_Admin(ImportExportActionModelAdmin):
    list_display=('id','exp','block','pset_id','mob','p_order')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
#----------------------------------------------------------------------------

class sort_featureResource(resources.ModelResource):
    class meta:
        model=sort_feature
class sort_featureAdmin(ImportExportActionModelAdmin):
    pass

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
#----------------------------------------------------------------------------
class mobilephonesResource(resources.ModelResource):
    class meta:
        model=mobilephones
class mobilephonesAdmin(ImportExportActionModelAdmin):
    pass

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
#----------------------------------------------------------------------------
class criteria_catalog_disp_Admin(admin.ModelAdmin):
    list_display=('id','catalog_crit_display_order')  
      
class StoreHoverBarChartLogsAdmin(admin.ModelAdmin):
    list_display=("id","user","value","phone_name","time")
class StoreHoverPieChartLogsAdmin(admin.ModelAdmin):
    list_display=("id","user","value","criteria_name","time")
class StoreNextPrevButtonLogsAdmin(admin.ModelAdmin):
    list_display=("id","user","button_name","phone_name","time")
class StoreCritWeightLogsAdmin(admin.ModelAdmin):
    list_display=("id","user","value","criteria_name","time")
class generalCriteriaDataAdmin(admin.ModelAdmin):
    list_display=("id","criteria","valuelist","inputtype")

admin.site.register(User, MyUserAdmin)
admin.site.register(ExpCriteriaOrder, ExpCriteriaOrderAdmin)
admin.site.register(selectedAdminPhones, selectedAdminPhones_Admin)
admin.site.register(PhoneCriteria, PhoneCriteriaAdmin)
admin.site.register(samsung_phone,SamsungAdmin)
admin.site.register(Role,RoleAdmin)
admin.site.register(platform_feature,PlatformFeatureAdmin)
admin.site.register(MobilePhones_Test,MobilePhones_TestAdmin)

admin.site.register(sort_feature,sort_featureAdmin)
admin.site.register(mobilephones,mobilephonesAdmin)
admin.site.register(userscoreRecord)
admin.site.register(signup_table)
admin.site.register(blog)


admin.site.register(Subject,SubjectAdmin)
admin.site.register(Batch)
admin.site.register(Block)
admin.site.register(experiment,ExperimentAdmin)
admin.site.register(exp_fdefaults,exp_fdefaultsAdmin)


admin.site.register(exStatusCd,exStatusCdAdmin)

admin.site.register(experiment_feature,experiment_featureAdmin)

admin.site.register(criteria_catalog_disp, criteria_catalog_disp_Admin)

admin.site.register(StoreHoverBarChartLogs, StoreHoverBarChartLogsAdmin)
admin.site.register(StoreHoverPieChartLogs, StoreHoverPieChartLogsAdmin)
admin.site.register(StoreNextPrevButtonLogs, StoreNextPrevButtonLogsAdmin)
admin.site.register(StoreCritWeightLogs, StoreCritWeightLogsAdmin)
admin.site.register(generalCriteriaData, generalCriteriaDataAdmin)


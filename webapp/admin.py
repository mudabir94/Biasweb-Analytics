from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.admin import ImportExportActionModelAdmin

from .models import User
from .models import signup_table,blog,mobile_phone,mobilephones,experiment
from .models import samsung_phone,sort_feature,userscoreRecord,Role,platform_feature
from .models import template_roles,templates,feature,selectedAdminPhones,PhoneCriteria
from .models import Subject,experiment_feature,Batch,Block,prunedmobilephones,ExpCriteriaOrder


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
class templateAdmin(admin.ModelAdmin):
    list_display=('id','template_name')    
class templateRoleAdmin(admin.ModelAdmin):
    list_display=('id','role_id','template_id',\
    'can_add','can_view','can_del',\
    'created_at','update_at',)    

class ExpCriteriaOrderAdmin(admin.ModelAdmin):
    list_display=('id','exp','cOrder_id','pCriteria','fvp','position','sh_hd')
class PhoneCriteriaAdmin(admin.ModelAdmin):
    list_display=('id','criteria_name','status','priority','position')

class ExperimentAdmin(admin.ModelAdmin):
    list_display= ('id','custom_exp_id')

class experiment_featureAdmin(admin.ModelAdmin):
    list_display= ('id','used_in','p_feature','chosen_levels')

#----------------------------------------------------------------------------

# platform_feature resource
class platformResource(resources.ModelResource):
    class meta:
        model=platform_feature
#platform_feature admin
class PlatformFeatureAdmin(ImportExportActionModelAdmin):
    list_display= ('id', 'feature_name','feature_symbol','feature_levels')

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


admin.site.register(User, MyUserAdmin)
admin.site.register(ExpCriteriaOrder, ExpCriteriaOrderAdmin)
admin.site.register(selectedAdminPhones, selectedAdminPhones_Admin)
admin.site.register(PhoneCriteria, PhoneCriteriaAdmin)
admin.site.register(samsung_phone,SamsungAdmin)
admin.site.register(Role,RoleAdmin)
admin.site.register(platform_feature,PlatformFeatureAdmin)

admin.site.register(templates,templateAdmin)
admin.site.register(template_roles,templateRoleAdmin)
admin.site.register(sort_feature,sort_featureAdmin)
admin.site.register(mobilephones,mobilephonesAdmin)
admin.site.register(userscoreRecord)
admin.site.register(signup_table)
admin.site.register(blog)
admin.site.register(mobile_phone)

admin.site.register(Subject)
admin.site.register(Batch)
admin.site.register(Block)
admin.site.register(prunedmobilephones)
admin.site.register(feature)
admin.site.register(experiment,ExperimentAdmin)
admin.site.register(experiment_feature,experiment_featureAdmin)


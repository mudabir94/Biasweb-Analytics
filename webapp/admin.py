from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import User
from .models import signup_table,blog,mobile_phone,phone,experiment
from .models import samsung_phone,sort_feature,userscoreRecord,Role,platform_feature


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
class RoleAdmin(admin.ModelAdmin):
    list_display= ('id', 'role_name')
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
    
class PlatformFeatureAdmin(admin.ModelAdmin):
    list_display= ('id', 'feature_name')
class ExperimentAdmin(admin.ModelAdmin):
    list_display= ('id', 'experiment_name')
    
admin.site.register(User, MyUserAdmin)
admin.site.register(signup_table)
admin.site.register(blog)
admin.site.register(mobile_phone)
admin.site.register(phone)
admin.site.register(samsung_phone)
admin.site.register(sort_feature)
admin.site.register(userscoreRecord)
admin.site.register(Role,RoleAdmin)
admin.site.register(platform_feature,PlatformFeatureAdmin)
admin.site.register(experiment,ExperimentAdmin)
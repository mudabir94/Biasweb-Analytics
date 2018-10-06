from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import User
from .models import signup_table,blog,mobile_phone,phone,samsung_phone,sort_feature,userscoreRecord,Role


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
admin.site.register(User, MyUserAdmin)
admin.site.register(signup_table)
admin.site.register(blog)
admin.site.register(mobile_phone)
admin.site.register(phone)
admin.site.register(samsung_phone)
admin.site.register(sort_feature)
admin.site.register(userscoreRecord)
admin.site.register(Role)


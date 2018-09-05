from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import User
<<<<<<< HEAD
from .models import signup_table,blog,mobile_phone,phone,samsung_phone,sort_feature,userscoreRecord
=======
from .models import signup_table,blog,mobile_phone,phone,samsung_phone,sort_feature
>>>>>>> 65e64f29cb305c7a26d9e7e55d0aacdd8cf9adf4


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_student', 'is_prof','is_ra',)}),

    )
admin.site.register(User, MyUserAdmin)
admin.site.register(signup_table)
admin.site.register(blog)
admin.site.register(mobile_phone)
admin.site.register(phone)
admin.site.register(samsung_phone)
admin.site.register(sort_feature)
<<<<<<< HEAD
admin.site.register(userscoreRecord)
=======
>>>>>>> 65e64f29cb305c7a26d9e7e55d0aacdd8cf9adf4

from django.forms import ModelForm
from .models import blog,signup_table,mobile_phone,phone,samsung_phone,sort_feature
from django import forms
from django.contrib.auth.forms import UserCreationForm
<<<<<<< HEAD
from django.contrib.auth.models import User
from webapp.models import User as SubjUser 
=======
from django.contrib.auth.models import User 
## Not using these forms 
#----------------------------------------------------------------------------------------
>>>>>>> 4fb2919aff208b9724276cf9c5a71410fbc985e6
class blogForm(ModelForm):
    class Meta:
        model=blog
        fields=['title']
class SignUpForm(UserCreationForm):
   
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', )

class SubjectCreationForm(forms.ModelForm):
    class Meta:
        model = SubjUser
        fields = ('username', 'custom_id')

    def save(self, commit=True, pwd='qwerty12345'):
        # Save the provided password in hashed format
        user = super(SubjectCreationForm, self).save(commit=False)
        default_password = pwd
        user.set_password(default_password) #Set de default password
        if commit:
            user.save()
        return user

class mobile_phone_form(ModelForm):
    class Meta:
        model=samsung_phone
        fields='__all__'
class filterform(ModelForm):
    class Meta:
        model=samsung_phone
        fields='__all__'
class sort_filter_form(ModelForm):
    class Meta:
        model=sort_feature
        fields='__all__'
# this class is just for testing will have to change the name once test is complete. 
class NameForm(forms.Form):
     csvfilepath=forms.CharField(label='file path',max_length=100)

class uploadSampleFileForm(forms.Form):
    samplefile = forms.FileField()
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Parol',widget=forms.PasswordInput)
    password2 = forms.CharField(label='Parol2',widget=forms.PasswordInput)


    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']

    def clean_password2(self):
        data = self.cleaned_data
        if data['password']!= data['password2']:
            raise forms.ValidationError('Kiritilgan parollar bir biriga mos bo\'lish shart')
        return data['password']


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email']

class ProfileEditForms(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo','date_of_birth']
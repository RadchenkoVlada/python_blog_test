from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text',)

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Your e-mail address', max_length=100)
    first_name = forms.CharField(label = "First name", max_length=100)
    last_name = forms.CharField(label = "Last name", max_length=100)
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email",)

    def save(self, commit=True):
    	user = super(RegisterForm, self).save(commit=False)
    	user.email = self.cleaned_data['email']
    	user.first_name = self.cleaned_data['first_name']
    	user.last_name = self.cleaned_data['last_name']

    	if commit:
    		user.save()
    	return user
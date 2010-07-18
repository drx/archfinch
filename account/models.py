from django.db import models
from django.contrib.auth.forms import UserCreationForm
from users.models import User
from django import forms


class SignupForm(UserCreationForm):
    #email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ['username', 'email']

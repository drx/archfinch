from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from users.models import User
from django import forms


class SignupForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    username = forms.RegexField(label="Username", max_length=30, regex=r'^[\w.@+-]+$',
        error_messages = {
            'invalid': "Username may contain only letters, numbers and @/./+/-/_ characters.",
            'required': "You need to provide a username.",
            'max_length': "Username must be at most 30 characters long.",
        })
    password = forms.CharField(label="Password", widget=forms.PasswordInput,
        error_messages = {'required': "You need to provide a password."})

    class Meta:
        model = User
        fields = ("username",)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("A user with that username already exists.")

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users.
    """
    username = forms.CharField(label="Username", max_length=30,
        error_messages = {
            'required': "You need to provide a username.",
            'max_length': "Username must be at most 30 characters long.",
        })
    password = forms.CharField(label="Password", widget=forms.PasswordInput,
        error_messages = {'required': "You need to provide a password."})

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Please enter a correct username and password. Note that both fields are case-sensitive.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")

        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in.")

        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


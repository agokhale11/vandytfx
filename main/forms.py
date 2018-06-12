from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django import forms


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=16,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=16,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password'}))


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(label="Full Name", max_length=50,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'full_name'}))

    email = forms.EmailField(label = "Email", max_length =50, widget=forms.EmailInput(attrs={'class': 'form-control', 'name': 'email'}))

    class Meta:
        model = User
        fields = ("email", "full_name", "username", "password1", "password2")

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.full_name = self.cleaned_data["full_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class EmailSignupForm(UserCreationForm):
    full_name = forms.CharField(label="Full Name", max_length=50,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'full_name'}))

    class Meta:
        model = User
        fields = ("full_name", "username", "password1", "password2")

    def save(self, commit=True):
        user = super(EmailSignupForm, self).save(commit=False)
        user.full_name = self.cleaned_data["full_name"]
        if commit:
            user.save()
        return user

class ChangePasswordForm(forms.Form):
    security_code = forms.CharField(label="Security Code", max_length=50,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'security_code'}))

    password1 = forms.CharField(label="New Password", max_length=16,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password1'}))
    password2 = forms.CharField(label="Re-enter New Password", max_length=16,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password2'}))


    class Meta:
        fields = ("security_code", "password1", "password2")
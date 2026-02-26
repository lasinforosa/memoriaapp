from django import forms
from django.contrib.auth.models import User

class RegistreForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contrasenya")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Repeteix la contrasenya")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Les contrasenyes no coincideixen.')
        return cd['password2']
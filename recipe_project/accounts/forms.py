from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']


class ProfileEditForm(forms.ModelForm):
    new_email = forms.EmailField(label='Новый Email', required=False)

    class Meta:
        model = CustomUser
        fields = ['avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.email:
            self.initial['new_email'] = self.instance.email

    def clean_new_email(self):
        new_email = self.cleaned_data['new_email']
        if not new_email:
            return new_email

        if new_email == self.instance.email:
            return new_email

        if CustomUser.objects.filter(email__iexact=new_email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с таким Email уже зарегистрирован.')

        return new_email

    def save(self, commit=True):
        user = super().save(commit=False)
        new_email = self.cleaned_data.get('new_email')

        if new_email and new_email != user.email:
            user.unconfirmed_email = new_email
        else:
            user.unconfirmed_email = None

        if commit:
            user.save()
        return user

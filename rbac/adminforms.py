from django import forms


class UserAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="密码")
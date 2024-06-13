from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=100,
        min_length=3,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control border border-primary',
            'name': 'username',
            'placeholder': 'Enter your Username',
            'id': 'username'
        })
    )
    password = forms.CharField(
        label='Password',
        max_length=50,
        min_length=5,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control border border-primary',
            'name': 'password',
            'placeholder': 'Enter your Password',
            'id': 'password'
        })
    )


class RegisterForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=100,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control border border-primary',
            'name': 'username',
            'placeholder': 'Enter your Username'
        })
    )
    email = forms.EmailField(
        label='Email',
        max_length=35,
        min_length=5,
        widget=forms.EmailInput(attrs={
            'class': 'form-control border border-primary',
            'name': 'email',
            'placeholder': 'Your email address'
        })
    )
    password1 = forms.CharField(
        label='Password',
        max_length=50,
        min_length=5,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control border border-primary',
            'name': 'password',
            'placeholder': 'Enter your Password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        max_length=50,
        min_length=5,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control border border-primary',
            'name': 'password_confirm',
            'placeholder': 'Password confirmation'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password1')
        password_confirm = cleaned_data.get('password2')
        if password != password_confirm:
            self.add_error('password1', 'Passwords are not the same !!')

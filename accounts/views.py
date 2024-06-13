from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm
from django.views.generic import View
from django.db.models import Q


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        login_form = LoginForm()
        return render(request, 'accounts/login.html', context={'form': login_form})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            data = login_form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                redirect_url = request.GET.get('next', 'polls:list')
                return redirect(redirect_url)
            else:
                login_form.add_error('username', 'Invalid User Data')
        return render(request, 'accounts/login.html', context={'form': login_form})


class Register(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        register_form = RegisterForm()
        return render(request, 'accounts/register.html', {'form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            data = register_form.cleaned_data
            if User.objects.filter(Q(username=data['username']) | Q(email=data['email'])).exists():
                register_form.add_error('username', 'Username or Email already exists!')
            else:
                user = User.objects.create_user(username=data['username'], password=data['password1'], email=data['email'])
                login(request, user)
                return redirect('polls:list')
        return render(request, 'accounts/register.html', {'form': register_form})


def user_logout(request):
    logout(request)
    return redirect('home')

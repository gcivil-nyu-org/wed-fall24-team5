# Create your views here.
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import MyAuthenticationForm, MyUserCreationForm

def register_view(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        email = request.POST.get('email')

        # Check if the email is already in use
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, 'accounts/register.html', {'form': form})

        if form.is_valid():
            user = form.save(commit=False)  # Create a user object but don't save it yet
            user.username = form.cleaned_data.get('email')  # Set username as email
            user.save()  # Save the user object
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('accounts:profile')
        else:
            messages.error(request, "Registration Failed!! Password mismatch or too generic")
            form = MyUserCreationForm()
            return render(request, 'accounts/register.html', {'form': form})
    else:
        form = MyUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = MyAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Incorrect email or password. Please try again.')
            form = MyAuthenticationForm()
            return render(request, 'accounts/login.html', {'form': form})
    else:
        form = MyAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

def logout_view(request):
    logout(request)
    return redirect('/')

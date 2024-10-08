# Create your views here.
import os
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from dotenv import load_dotenv, set_key
from .forms import MyAuthenticationForm, MyUserCreationForm

# In your app's views.py or signals.py
@receiver(post_migrate)
def my_signal_receiver(sender, **kwargs):
    # Safe to access the database here
    from django.contrib.sites.models import Site
    
    site, _ = Site.objects.get_or_create(
        domain=os.getenv('domain','http://127.0.0.1:8000'),
        defaults={'name': os.getenv('domain_name', 'http://127.0.0.1:8000')}
    )

    site.save()

    # Path to your .env file
    load_dotenv()
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env') # pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long
    set_key(env_file, 'SITE_ID', str(site.id)) # Write or update SITE_ID

    app, _ = SocialApp.objects.get_or_create(provider='google', name='google')
    app.client_id = os.getenv('client_id')
    app.secret = os.getenv('secret_key')
    app.sites.add(site)
    app.save()

def register_view(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        email = request.POST.get('email')

        # Check if the email is already in use
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, 'accounts/register.html', {'form': form})

        if form.is_valid(): # pylint: disable=no-else-return, locally-disabled, multiple-statements, fixme, line-too-long
            user = form.save(commit=False)  # Create a user object but don't save it yet
            user.username = form.cleaned_data.get('email')  # Set username as email
            user.save()  # Save the user object
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('accounts:profile')
        else:
            messages.error(request, "Registration Failed!! Password mismatch or too generic") # pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long
            form = MyUserCreationForm()
            return render(request, 'accounts/register.html', {'form': form})
    else:
        form = MyUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = MyAuthenticationForm(request, data=request.POST)
        if form.is_valid(): # pylint: disable=no-else-return, locally-disabled, multiple-statements, fixme, line-too-long
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
    storage = get_messages(request)
    for _ in storage:
        # Simply iterate over the messages to clear them
        pass
    logout(request)
    return redirect('/')

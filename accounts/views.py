from django import forms
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages  # Import messages
from django.conf import settings
from .models import *
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from .forms import RegistrationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse
from .tokens import AccountActivationTokenGenerator
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect

User = get_user_model()

def index(request):
     return render(request, "index.html")
    
    
def resend_activation_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email, is_active=False).first()
        if user:
            # Send activation email
            subject = 'Activate Your Account'
            message = render_to_string('activation_email.html', {
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, None, [email])
            messages.success(request, 'A new activation email has been sent.')
        else:
            messages.error(request, 'No inactive account found with the provided email.')
    return render(request, 'resend_activation_email.html')

def account_activation_sent(request):
    print("Activation Days:", settings.ACCOUNT_ACTIVATION_DAYS)
    context = {
        'activation_days': settings.ACCOUNT_ACTIVATION_DAYS
    }
    return render(request, 'account_activation_sent.html', context)
        
def activate(request, uidb64, token):
    try:
        # Decode the user ID from base64
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # Log the user in after activating
        login(request, user)

        # Redirect to a success page or home with a success message
        messages.success(request, "Your account has been activated successfully!")
        return redirect('index')  # Make sure 'home' is a defined URL pattern name
    else:
        # Provide an error message and render a failure template
        messages.error(request, "The activation link was invalid!")
        return render(request, 'activation_invalid.html')

def user_settings(request):
    return render(request, 'settings.html')

    

def update_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == "POST":
        user.email = request.POST.get('email', user.email)
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        user.save()
        profile.save()
        context = {
            'user': user,
            'profile': profile,
            'alert': 'Profile updated successfully!'
        }
        return render(request, 'index.html', context)

    return render(request, 'update_profile.html', {'user': user, 'profile': profile})
    
def change_password(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password updated successfully.")
            return redirect('change_password')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)  

    return render(request, "change_password.html", {
        'form': form
    })
        
@staff_member_required
def admin_dashboard(request):
    if request.user.is_staff:
        users_pending_approval = fosUser.objects.filter(is_approved=False, is_active=False)
        approved_not_activated = fosUser.objects.filter(is_approved=True, is_active=False)
        return render(request, 'admin_dashboard.html', {
            'users_pending_approval': users_pending_approval,
            'approved_not_activated': approved_not_activated
        })
    else:
        return render(request, 'index.html')
    
@require_POST
@login_required
@permission_required('accounts.approve_user', raise_exception=True)
def admin_approve(request, user_id):
    try:
        user = fosUser.objects.get(pk=user_id)
        user.is_approved = True
        user.save()

        token_generator = AccountActivationTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = request.build_absolute_uri(
            reverse('activate', kwargs={'uidb64': uid, 'token': token})
        )

        subject = 'Please Activate Your Account'
        message = render_to_string('activation_email.html', {
            'user': user,
            'activation_link': activation_link
        })
        send_mail(subject, message, 'webmaster@localhost', [user.email], fail_silently=False)

        messages.success(request, 'User approved and activation email sent.')
        return redirect('admin_dashboard')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_dashboard')
        

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.full_name = form.cleaned_data['full_name']
            user.phone_number = form.cleaned_data['phone_number']
            user.is_active = False
            user.save()

            # Update or create profile
            Profile.objects.update_or_create(user=user, defaults={
                'name': user.full_name,
                'phone_number': user.phone_number
            })

            # Send activation email to the admin for approval
            admin_email = getattr(settings, 'DEFAULT_ADMIN_EMAIL', 'default_admin@example.com')
            subject = 'Approval Required for New User'
            admin_dashboard_url = request.build_absolute_uri(reverse('admin_dashboard'))
            message = f"Please approve the new user registration for {user.email}. Click here to approve: {admin_dashboard_url}"
            send_mail(subject, message, 'webmaster@localhost', [admin_email], fail_silently=False)

            return redirect('account_activation_sent')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

    
def Login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                alert = True
                return render(request, "login.html", {"alert":alert})
    return render(request, "login.html")

def Logout(request):
    logout(request)
    alert = True
    return render(request, "index.html", {'alert':alert})

from django.shortcuts import redirect, render
from django.http import HttpResponse, response
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout
from .helpers import login_prohibited
from .forms import LogInForm, UserForm, PasswordForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from .models import User, MembershipType
from django.core.exceptions import ObjectDoesNotExist
from .Constants import consts

# Create your views here.

def home(request):
    return render(request, 'home.html')

def test(request):
    return render(request, 'test.html')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('test')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                redirect_url = next or 'test'
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next': next})


def log_out(request):
    logout(request)
    return redirect('home')

def edit_details(request):
    return redirect('edit_details')


@login_required
def profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('test')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'profile.html', {'form': form})

@login_required
def promote(request, user_id):
    """user_id: the primary key of the user being promoted to 'member'
    Officers and Club Owners are able to promote specific applicants to members"""
    try:
        user = User.objects.get(pk=user_id)
        membership = MembershipType.objects.get(user=user)

    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid user to promote")
        return redirect("user_list")
    else:
        current_user = request.user

        if current_user.get_type()==consts.OFFICER or current_user.get_type()==consts.CLUB_OWNER:
            if (membership.type=="applicant"):
                membership.type = "member"
                membership.save()
                messages.add_message(request, messages.SUCCESS, "User successfully promoted to member")
            else:
                messages.add_message(request, messages.INFO, "User is already a member")

            return redirect("user_list")
        else:
            messages.add_message(request, messages.ERROR, "You are not are not allowed to promote users")
            return redirect("user_list")

@login_required
def password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('test')
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = PasswordForm()
    return render(request, 'password.html', {'form': form})

@login_required
def user_list(request):
    users = User.objects.all()
    current_user = request.user
    type = current_user.get_type()

    return render(request, 'user_list.html', {'users': users, "type": type})

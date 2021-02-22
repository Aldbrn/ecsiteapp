from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm

# Create your views here.


def signup(request):
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
        form.save()
        input_email = form.cleaned_data["email"]
        input_password = form.cleaned_data["password1"]
        new_user = authenticate(email=input_email, password=input_password)
        if new_user is not None:
            login(request, new_user)
            return redirect("app:index")
    else:
        form = CustomUserCreationForm()
    return render(request, "app/signup.html", {"form": form})


def index(request):
    return render(request, "app/index.html")

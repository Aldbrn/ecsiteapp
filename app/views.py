from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm
from .models import Product

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
    products = Product.objects.all().order_by("-id")
    return render(request, "app/index.html", {"products": products})


def detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {"product": product}
    return render(request, "app/detail.html", context)


@login_required
@require_POST
def toggle_fav_product_status(request):

    product = get_object_or_404(Product, pk=request.POST["product_id"])
    user = request.user

    if product in user.fav_products.all():
        user.fav_products.remove(product)
    else:
        user.fav_products.add(product)
    return redirect("app:detail", product_id=product.id)


@login_required
def fav_products(request):
    user = request.user
    products = user.fav_products.all()
    return render(request, "app/index.html", {"products": products})

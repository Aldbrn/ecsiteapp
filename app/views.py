from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import CustomUserCreationForm
from .forms import AddToCartForm
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

    if request.method == "POST":
        add_to_cart_form = AddToCartForm(request.POST)
        if add_to_cart_form.is_valid():
            num = add_to_cart_form.cleaned_data["num"]
            if "cart" in request.session:
                if str(product_id) in request.session["cart"]:
                    request.session["cart"][str(product_id)] += num
                else:
                    request.session["cart"][str(product_id)] = num
            else:
                request.session["cart"] = {str(product_id): num}
        messages.success(request, f"{product.name}を{num}個カートに入れました!")
        return redirect("app:detail", product_id=product_id)

    add_to_cart_form = AddToCartForm()
    context = {
        "product": product,
        "add_to_cart_form": add_to_cart_form,
    }
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


@login_required
def cart(request):
    cart = request.session.get("cart", {})
    cart_products = {}
    total_price = 0
    for product_id, num in cart.items():
        product = Product.objects.filter(id=product_id).first()
        if product is None:
            continue
        cart_products[product] = num
        total_price += product.price * num

    context = {"cart_products": cart_products, "total_price": total_price}
    return render(request, "app/cart.html", context)


@login_required
@require_POST
def change_product_amount(request):
    product_id = request.POST["product_id"]
    cart_session = request.session["cart"]

    if product_id in cart_session:
        if "action_remove" in request.POST:
            cart_session[product_id] -= 1
        if "action_add" in request.POST:
            cart_session[product_id] += 1
        if cart_session[product_id] <= 0:
            del cart_session[product_id]
        return redirect("app:cart")

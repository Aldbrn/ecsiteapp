import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import CustomUserCreationForm, AddToCartForm, PurchaseForm
from .models import Product, Sale

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
    user = request.user
    cart = request.session.get("cart", {})
    cart_products = {}
    total_price = 0
    for product_id, num in cart.items():
        product = Product.objects.filter(id=product_id).first()
        if product is None:
            continue
        cart_products[product] = num
        total_price += product.price * num

    if request.method == "POST":
        purchase_form = PurchaseForm(request.POST)
        if purchase_form.is_valid():
            if "search_address" in request.POST:
                zip_code = request.POST["zip_code"]
                address = fetch_address(zip_code)
                if not address:
                    messages.warning(request, "住所を取得できませんでした。")
                    return redirect("app:cart")
                purchase_form = PurchaseForm(
                    initial={"zip_code": zip_code, "address": address}
                )

            if "buy_product" in request.POST:
                if not purchase_form.cleaned_data["address"]:
                    messages.warning(request, "住所の入力は必須です。")
                    return redirect("app:cart")
                if not cart:
                    messages.warning(request, "カートは空です。")
                    return redirect("app:cart")
                if total_price > user.point:
                    messages.warning(request, "所持ポイントが足りません")
                    return redirect("app:cart")

                for product, num in cart_products.items():
                    sale = Sale(
                        product=product,
                        user=request.user,
                        amount=num,
                        price=product.price,
                        total_price=num * product.price,
                    )
                    sale.save()
                user.point -= total_price
                user.save()

                del request.session["cart"]
                messages.success(request, "商品の購入が完了しました。")
                return redirect("app:cart")
    else:
        purchase_form = PurchaseForm()
    context = {
        "purchase_form": purchase_form,
        "cart_products": cart_products,
        "total_price": total_price,
    }
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


def fetch_address(zip_code):
    """
    郵便番号検索APIを利⽤する関数
    引数に指定された郵便番号に対応する住所を返す
    住所取得に失敗した場合は空⽂字を返す
    """

    REQUEST_URL = f"http://zipcloud.ibsnet.co.jp/api/search?zipcode={zip_code}"
    response = requests.get(REQUEST_URL)
    response = json.loads(response.text)
    results, api_status = response["results"], response["status"]

    address = ""
    if api_status == 200 and results is not None:
        result = results[0]
        address = result["address1"] + result["address2"] + result["address3"]
    return address


@login_required
def order_histry(request):
    user = request.user
    sales = Sale.objects.filter(user=user).order_by("-created_at")
    return render(request, "app/order_histry.html", {"sales": sales})

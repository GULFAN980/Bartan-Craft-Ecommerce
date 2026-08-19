from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import Product, Order, OrderItem


# =========================================================
# HOME
# =========================================================

def home(request):
    products = Product.objects.all().order_by("-created_at")

    return render(request, "store/home.html", {
        "products": products
    })


# =========================================================
# PRODUCTS
# =========================================================

def products(request):
    product_list = Product.objects.all().order_by("-created_at")

    return render(request, "store/products.html", {
        "products": product_list
    })


# =========================================================
# PRODUCT DETAIL
# =========================================================

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, "store/product_detail.html", {
        "product": product
    })


# =========================================================
# ADD TO CART
# =========================================================

def add_to_cart(request, product_id):

    if request.method != "POST":
        return redirect("store:product_detail", product_id=product_id)

    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(
            request,
            "Sorry, this product is out of stock."
        )
        return redirect(
            "store:product_detail",
            product_id=product_id
        )

    cart = request.session.get("cart", {})

    product_id_str = str(product_id)

    current_quantity = int(
        cart.get(product_id_str, 0)
    )

    if current_quantity >= product.stock:
        messages.warning(
            request,
            f"Only {product.stock} items are available."
        )
        return redirect("store:cart")

    cart[product_id_str] = current_quantity + 1

    request.session["cart"] = cart
    request.session.modified = True

    messages.success(
        request,
        f"{product.name} added to cart."
    )

    return redirect("store:cart")


# =========================================================
# CART
# =========================================================

def cart(request):

    cart_data = request.session.get("cart", {})

    cart_items = []
    total = Decimal("0.00")
    cart_count = 0

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=int(product_id)
        )

        quantity = int(quantity)

        item_total = product.price * quantity

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "item_total": item_total,
        })

        total += item_total
        cart_count += quantity

    return render(
        request,
        "store/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
            "cart_count": cart_count,
        }
    )


# =========================================================
# REMOVE FROM CART
# =========================================================

def remove_from_cart(request, product_id):

    cart = request.session.get("cart", {})

    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("store:cart")


# =========================================================
# UPDATE CART
# =========================================================

def update_cart(request, product_id):

    if request.method != "POST":
        return redirect("store:cart")

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart = request.session.get("cart", {})

    product_id_str = str(product_id)

    try:
        quantity = int(
            request.POST.get("quantity", 1)
        )
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:

        cart.pop(product_id_str, None)

    elif quantity > product.stock:

        cart[product_id_str] = product.stock

        messages.warning(
            request,
            f"Only {product.stock} items are available."
        )

    else:

        cart[product_id_str] = quantity

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("store:cart")


# =========================================================
# CHECKOUT
# =========================================================

@login_required(login_url="/login/")
def checkout(request):

    cart_data = request.session.get("cart", {})

    if not cart_data:
        messages.warning(
            request,
            "Your cart is empty."
        )
        return redirect("store:cart")

    cart_products = []
    total = Decimal("0.00")

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=int(product_id)
        )

        quantity = int(quantity)

        subtotal = product.price * quantity

        cart_products.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

        total += subtotal

    return render(
        request,
        "store/checkout.html",
        {
            "cart_products": cart_products,
            "total": total,
        }
    )


# =========================================================
# PLACE ORDER
# =========================================================

@login_required(login_url="/login/")
@transaction.atomic
def place_order(request):

    if request.method != "POST":
        return redirect("store:checkout")

    cart_data = request.session.get("cart", {})

    if not cart_data:
        messages.error(
            request,
            "Your cart is empty."
        )
        return redirect("store:cart")

    customer_name = request.POST.get(
        "name",
        ""
    ).strip()

    phone = request.POST.get(
        "phone",
        ""
    ).strip()

    address = request.POST.get(
        "address",
        ""
    ).strip()

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not customer_name:
        messages.error(
            request,
            "Please enter your name."
        )
        return redirect("store:checkout")

    if not phone:
        messages.error(
            request,
            "Please enter your phone number."
        )
        return redirect("store:checkout")

    if not address:
        messages.error(
            request,
            "Please enter your delivery address."
        )
        return redirect("store:checkout")

    # -----------------------------------------------------
    # CHECK PRODUCTS AND STOCK
    # -----------------------------------------------------

    total = Decimal("0.00")

    order_products = []

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=int(product_id)
        )

        quantity = int(quantity)

        if quantity <= 0:
            continue

        if product.stock < quantity:

            messages.error(
                request,
                f"Only {product.stock} units of "
                f"{product.name} are available."
            )

            return redirect("store:cart")

        subtotal = product.price * quantity

        total += subtotal

        order_products.append({
            "product": product,
            "quantity": quantity,
        })

    if not order_products:
        messages.error(
            request,
            "Your cart is empty."
        )
        return redirect("store:cart")

    # -----------------------------------------------------
    # CREATE ORDER
    # -----------------------------------------------------

    order = Order.objects.create(
        customer=request.user,
        customer_name=customer_name,
        phone=phone,
        address=address,
        total_amount=total,
    )

    # -----------------------------------------------------
    # CREATE ORDER ITEMS
    # -----------------------------------------------------

    for item in order_products:

        product = item["product"]
        quantity = item["quantity"]

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
        )

        product.stock -= quantity

        product.save(
            update_fields=["stock"]
        )

    # -----------------------------------------------------
    # CLEAR CART
    # -----------------------------------------------------

    request.session["cart"] = {}
    request.session.modified = True

    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    return redirect(
        "store:order_success",
        order_id=order.id
    )


# =========================================================
# ORDER SUCCESS
# =========================================================

@login_required(login_url="/login/")
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    return render(
        request,
        "store/order_success.html",
        {
            "order": order
        }
    )


# =========================================================
# MY ORDERS
# =========================================================

@login_required(login_url="/login/")
def my_orders(request):

    orders = Order.objects.filter(
        customer=request.user
    ).prefetch_related(
        "items__product"
    ).order_by("-created_at")

    return render(
        request,
        "store/my_orders.html",
        {
            "orders": orders
        }
    )


# =========================================================
# ORDER DETAIL
# =========================================================

@login_required(login_url="/login/")
def order_detail(request, order_id):

    # IMPORTANT:
    # Customer can ONLY see his/her own order.

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__product"
        ),
        id=order_id,
        customer=request.user
    )

    order_items = order.items.all()

    return render(
        request,
        "store/order_detail.html",
        {
            "order": order,
            "order_items": order_items,
        }
    )


# =========================================================
# REGISTER
# =========================================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not username or not password:
            return render(
                request,
                "store/register.html",
                {
                    "error":
                    "Username and password are required."
                }
            )

        if password != confirm_password:
            return render(
                request,
                "store/register.html",
                {
                    "error":
                    "Passwords do not match."
                }
            )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "store/register.html",
                {
                    "error":
                    "Username already exists."
                }
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(
            request,
            user
        )

        return redirect("store:home")

    return render(
        request,
        "store/register.html"
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("store:home")

        return render(
            request,
            "store/login.html",
            {
                "error":
                "Invalid username or password."
            }
        )

    return render(
        request,
        "store/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect("store:home")

# =========================================================
# OPERATOR LOGIN
# =========================================================

def operator_login(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect("store:operator_dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:

            login(request, user)

            return redirect("store:operator_dashboard")

        return render(
            request,
            "store/operator_login.html",
            {
                "error": "Invalid operator credentials."
            }
        )

    return render(
        request,
        "store/operator_login.html"
    )


# =========================================================
# OPERATOR DASHBOARD
# =========================================================

@login_required(login_url="/operator-login/")
def operator_dashboard(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to access the operator panel."
        )
        return redirect("store:home")

    products = Product.objects.all().order_by("-created_at")

    orders = Order.objects.all().order_by("-created_at")[:10]

    return render(
        request,
        "store/operator_dashboard.html",
        {
            "products": products,
            "orders": orders,
        }
    )


# =========================================================
# ADD PRODUCT
# =========================================================

@login_required(login_url="/operator-login/")
def add_product(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to perform this action."
        )
        return redirect("store:home")

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        description = request.POST.get(
            "description",
            ""
        ).strip()

        price = request.POST.get("price", "").strip()
        stock = request.POST.get("stock", "").strip()

        image = request.FILES.get("image")

        if not name or not description or not price or not stock:
            messages.error(
                request,
                "Please fill all required fields."
            )
            return redirect("store:add_product")

        try:
            price = Decimal(price)
            stock = int(stock)

            if price < 0 or stock < 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                "Please enter valid price and stock."
            )
            return redirect("store:add_product")

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image,
        )

        messages.success(
            request,
            f"{name} added successfully."
        )

        return redirect("store:operator_dashboard")

    return render(
        request,
        "store/add_product.html"
    )


# =========================================================
# EDIT PRODUCT
# =========================================================

@login_required(login_url="/operator-login/")
def edit_product(request, product_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to perform this action."
        )
        return redirect("store:home")

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        description = request.POST.get(
            "description",
            ""
        ).strip()

        price = request.POST.get("price", "").strip()
        stock = request.POST.get("stock", "").strip()

        image = request.FILES.get("image")

        if not name or not description or not price or not stock:
            messages.error(
                request,
                "Please fill all required fields."
            )
            return redirect(
                "store:edit_product",
                product_id=product.id
            )

        try:
            price = Decimal(price)
            stock = int(stock)

            if price < 0 or stock < 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                "Please enter valid price and stock."
            )
            return redirect(
                "store:edit_product",
                product_id=product.id
            )

        product.name = name
        product.description = description
        product.price = price
        product.stock = stock

        if image:
            product.image = image

        product.save()

        messages.success(
            request,
            f"{product.name} updated successfully."
        )

        return redirect(
            "store:operator_dashboard"
        )

    return render(
        request,
        "store/edit_product.html",
        {
            "product": product
        }
    )


# =========================================================
# DELETE PRODUCT
# =========================================================

@login_required(login_url="/operator-login/")
def delete_product(request, product_id):

    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorized to perform this action."
        )
        return redirect("store:home")

    if request.method != "POST":
        return redirect(
            "store:operator_dashboard"
        )

    product = get_object_or_404(
        Product,
        id=product_id
    )

    product_name = product.name

    product.delete()

    messages.success(
        request,
        f"{product_name} deleted successfully."
    )

    return redirect(
        "store:operator_dashboard"
    )


# =========================================================
# OPERATOR LOGOUT
# =========================================================

@login_required(login_url="/operator-login/")
def operator_logout(request):

    if not request.user.is_staff:
        return redirect("store:home")

    logout(request)

    return redirect(
        "store:operator_login"
    )
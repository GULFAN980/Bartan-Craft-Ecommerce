from django.urls import path
from . import views


app_name = "store"


urlpatterns = [

    # =====================================================
    # HOME
    # =====================================================

    path(
        "",
        views.home,
        name="home"
    ),

    # =====================================================
    # PRODUCTS
    # =====================================================

    path(
        "products/",
        views.products,
        name="products"
    ),

    path(
        "products/<int:product_id>/",
        views.product_detail,
        name="product_detail"
    ),

    # =====================================================
    # CART
    # =====================================================

    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/remove/<int:product_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "cart/update/<int:product_id>/",
        views.update_cart,
        name="update_cart"
    ),

    # =====================================================
    # CHECKOUT
    # =====================================================

    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    path(
        "place-order/",
        views.place_order,
        name="place_order"
    ),

    # =====================================================
    # ORDER
    # =====================================================

    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),

    # =====================================================
    # MY ORDERS
    # =====================================================

    path(
        "my-orders/",
        views.my_orders,
        name="my_orders"
    ),

    path(
        "my-orders/<int:order_id>/",
        views.order_detail,
        name="order_detail"
    ),

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "register/",
        views.register_view,
        name="register"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # =====================================================
    # OPERATOR
    # =====================================================

    path(
        "operator-login/",
        views.operator_login,
        name="operator_login"
    ),

    path(
        "operator-dashboard/",
        views.operator_dashboard,
        name="operator_dashboard"
    ),

    path(
        "operator/add-product/",
        views.add_product,
        name="add_product"
    ),

    path(
        "operator/edit-product/<int:product_id>/",
        views.edit_product,
        name="edit_product"
    ),

    path(
        "operator/delete-product/<int:product_id>/",
        views.delete_product,
        name="delete_product"
    ),

    path(
        "operator-logout/",
        views.operator_logout,
        name="operator_logout"
    ),
]
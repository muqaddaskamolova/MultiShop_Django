from django.urls import path
from .views import *

app_name = 'store'

urlpatterns = [
    # path('', ProductListView.as_view, name='product_list'),
    path('', product_list, name='product_list'),
    path('category/<int:category_id>/', category_products, name='category'),
    #  path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('category/<slug:slug>/', category_page, name='category_detail'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='product_detail'),
    # path('request/', RequestInfoView.as_view(), name='request'),
    path('cart/', cart, name='cart'),
    path('to_cart/<int:product_id>/<str:action>/', to_cart, name='to_cart'),
    path('clear_cart/', clear_cart, name='clear_cart'),
    path('checkout/', checkout, name='checkout'),
    path('shop/', shop, name='shop'),
    path('payment/', create_checkout_sessions, name='payment'),
    path('payment_success/', successPayment, name='success'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('contact/', contact, name='contact'),
    path('shop_detail/', shop_detail, name='shop_detail'),
    path('about/', about, name='about'),
    path('FAQ/', FAQs, name='FAQs'),
    path('profile/', profile, name='users-profile'),
    path('selectcurrency/', selectcurrency, name='selectcurrency'),
    path('savelangcurr/', savelangcurr, name='savelangcurr'),
]

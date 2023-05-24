from django.core.checks import messages
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import translation

from .models import *
from django.views.generic import DetailView, ListView, CreateView
from random import randint
from .forms import CustomerForm, ShippingForm
from .utils import *

import stripe
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate, get_language, gettext
from multishop import settings


# Create your views here.
# class ProductListView(ListView):
#  model = Product
#  context_object_name = 'categories'

# extra_context = {
#     'title': 'MULTI SHOP - ONLINE',

#  }
# template_name = 'store/product_list.html'

#  def get_queryset(self):
#    categories = Category.objects.filter(parent=None)
#   return categories


def profile(request):
    return render(request, 'users/profile.html')


def product_list(request):
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY

    #  setting = Setting.objects.get(pk=1)
    products = Product.objects.all().order_by('-id')[:4]
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]

    if defaultlang != currentlang:
        setting = settings.LANGUAGES.objects.get(language=currentlang)
        products = Product.objects.row(
            'SELECT p.id, p.price, l.title, l.description, l.slang'
            'FROM product as p'
            'LEFT JOIN productlang as l '
            'ON p.id = l.product_id'
            'WHERE l.language ORDER_BY p.id DESC LIMIT 4', [currentlang]
        )

    products_slider = Product.objects.all().order_by('id')[:4]
    products_picked = Product.objects.all().order_by('?')[:4]
    categories = Category.objects.filter(parent=None)
    trans = translate(language='ru')
    context = {
        'title': 'MULTI SHOP - ONLINE',
        'setting': 'setting',
        'categories': categories,
        'products': products,
        'products_slider': products_slider,
        'products_picked': products_picked,
        'trans': trans,

    }
    return render(request, 'store/product_list.html', context)


def translate(language):
    cur_language = get_language()
    try:
        activate(language)
        text = gettext('Shopping')
    finally:
        activate(cur_language)
    return text


def category_products(request, category_id, category_slug):
    products = Product.objects.filter(category_id=category_id)
    products = products.order_by('-created_at')

    category = Category.objects.get(pk=category_id, slug=category_slug)
    categories = Category.objects.all()
    if category_slug:
        category_slug = get_object_or_404(Category, slug=category_slug)
    context = {
        'title': f'Category: {category.title}',
        'categories': categories,
        'products': products,
        'category': category_slug
    }

    return render(request, 'components/_nav.html', context)


# def product_detail(request, slug):
#  product = get_object_or_404(Product, slug=slug, quantity=True)
# product = Product.objects.get(slug=slug)
# context = {
#     'product': product
# }
# return render(request, 'store/components/product_detail.html', context)
# class RequestInfoView(CreateView):
#  template_name = 'request_info.html'
# form_class = RequestInfoForm
# success_url = '/thanks/'

#  def form_valid(self, form):
#     name = form.cleaned_data['name']
#    email = form.cleaned_data['email']
#   phone = form.cleaned_data['phone']
#  state = form.cleaned_data['state']
# vendor = form.cleaned_data['vendor']
# product_name = form.cleaned_data['product']

# message = name + " " + email + " " + state + " " + str(product_name)

#  html_message = render_to_string('mail_request.html', context=({'name': name,
#                                                                'email': email,
#                                                              'phone': phone,
#                                                             'state': state,
#                                                              'product': product_name}))
# try:
#    send_mail('Sales Inquiry from: ' + name, message, email, ['test@example.com'],
#             html_message=html_message)
# except:
#   return HttpResponse('Invalid header found.')
# return super().form_valid(form)


class ProductDetail(DetailView):
    model = Product
    template_name = 'store/components/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Product: {product.title}'

        products = Product.objects.all()
        data = []
        for i in range(0):
            random_index = randint(0, len(products))
            p = products[random_index]

            if p not in data:
                data.append(p)

        context['products'] = data

        return context


# class CategoryView(ListView):
#    model = Product
#    context_object_name = 'products'
#  template_name = 'store/_category_page.html'

#   def get_queryset(self):
#      main_category = Category.objects.get(slug=self.kwargs['slug'])
#     subcategories = main_category.subcategories.all()
#    data = []
#     for subcategory in subcategories:
#        products = subcategory.products.all()
#        for product in products:
#            data.append(product)
#           return data


def category_page(request, slug):
    main_category = Category.objects.get(category=request.POST.get('category'), slug=slug)
    subcategories = main_category.subcategories.all()
    products = Product.objects.filter(category__in=subcategories)
    paginate_by = 4

    context = {
        'products': products,
        'main_category': main_category,
        'subcategories': subcategories,
        'pagination': paginate_by
    }

    sort_fields = request.Get.get('sort')
    if sort_fields:
        context['products'] = context['products'].order_by(*sort_fields)

    return render(request, 'store/category_page.html', context)


def cart(request):
    cart_info = get_cart_data(request)

    context = {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'order': cart_info['order'],
        'products': cart_info['products']
    }
    return render(request, 'store/cart.html', context)


def to_cart(request, product_id, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, product_id, action)
        return redirect('cart', {'user_cart': user_cart})
    else:
        messages.error(request, "Xaridni amalga oshirish uchun, Avrotizatsiyadan yoki ro'yxatdan o'ting")
        return redirect('login_registration')


def checkout(request):
    cart_info = get_cart_data(request)
    context = {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'order': cart_info['order'],
        'items': cart_info['products'],
        'customer_form': CustomerForm(),
        'shipping_form': ShippingForm(),
        'title': 'Make an order'
    }
    return render(request, 'store/checkout.html', context)


def shop(request):
    return render(request, 'store/shop.html', {})


def create_checkout_sessions(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        '''Bu yerda foydalanuvchi ma'lumotlarini saqlaymiz.'''
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()
        customer_form = CustomerForm(data=request.POST)
        if customer_form.is_valid():
            customer = Customer.objects.get(user=request.user)
            customer.first_name = customer_form.cleaned_data['first_name']
            customer.last_name = customer_form.cleaned_data['last_name']
            customer.save()
            user = User.objects.get(username=request.user.username)
            user.first_name = customer_form.cleaned_data['first_name']
            user.last_name = customer_form.cleaned_data['last_name']
            user.save()
        shipping_form = ShippingForm(data=request.POST)
        if shipping_form.is_valid():
            address = shipping_form.save(commit=False)
            address.customer = Customer.objects.get(user=request.user)
            address.order = user_cart.get_cart_info()['order']
            address.save()

        total_price = cart_info['cart_total_price']
        total_quantity = cart_info['cart_total_quantity']
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Products'
                    },
                    'unit_amount': int(total_price * 100)
                },
                'quantity': total_quantity
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('success')),
        )
        return redirect(session.url, 303)


def successPayment(request):
    user_cart = CartForAuthenticatedUser(request)
    user_cart.clear()
    messages.success(request, "The Payment was made successfully!")
    return render(request, 'store/success.html')


def clear_cart(request):
    user_cart = CartForAuthenticatedUser(request)
    order = user_cart.get_cart_info()['order']
    order_products = order.orderproduct_set.all()
    for order_product in order_products:
        quantity = order_product.quantity
        product = order_product.product
        order_product.delete()
        product.quantity += quantity
        product.save()
    return redirect('cart')


def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        context = {'form': form}
        return render(request, 'store/components/register.html', context)

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
        user = form.cleaned_data.get('username')
        messages.success(request, 'Account was created for ' + user)

        return redirect('product_list')
    else:
        form = RegisterForm()
        messages.error(request, 'Error Processing Your Request')
        context = {'form': form}
        return render(request, 'store/components/register.html', context)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                messages.success(request, 'You have successfully logged in!')
                return redirect('product_list')
            else:
                messages.error(request, 'You have not logged in,  Or  your login or password is wrong!')
                return redirect('login')
        else:
            messages.error(request, 'You have not logged in,  Or  your login or password is wrong!')
            return redirect('login')
    else:
        form = LoginForm()
        context = {
            'title': 'LOGIN',
            'form': form
        }
        return render(request, 'store/components/login.html', context)


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    messages.warning(request, 'You have successfully logged out!')
    return redirect('product_list')


def contact(request, ):
    if request.method == 'POST':
        message_name = request.POST['message-name'],
        message_email = request.POST['message-email'],
        subject_name = request.POST['subject-name'],
        message = request.POST['message'],

        send_mail(
            message_name,
            subject_name,
            message,
            message_email,
            ['kamolovamuqaddas@gmail.com']
        )

        return render(request, 'store/components/contact.html', {'message_name': message_name,
                                                                 'message_email': message_email,
                                                                 'subject_name': subject_name,
                                                                 'message': message})
    else:
        return render(request, 'store/components/contact.html', {})


def shop_detail(request):
    context = {}

    return render(request, 'store/components/shop_detail.html', context)


def about(request):
    context = {}

    return render(request, 'store/components/about.html', context)


def FAQs(request):
    context = {}

    return render(request, 'store/components/FAQs.html', context)


def selectcurrency(request):
    lasturl = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        curr_currency = translation.get_language()

        request.session['currency'] = request.POST['currency']
        return HttpResponseRedirect(lasturl)


def savelangcurr(request):
    lasturl = request.META.get('HTTP_REFERER')
    current_user = request.user
   # language = Language.objects.get(code=request.LANGUAGE_CODE[0:2])
    data = UserProfile.objects.get(user_id=current_user.id)
  #  data.language_id = language.id
    data.currency_id = request.session['currency']
    data.save()
    return HttpResponseRedirect(lasturl)

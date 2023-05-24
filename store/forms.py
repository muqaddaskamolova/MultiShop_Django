from django import forms
import datetime
import re
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate, get_language


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control',
                                                 'placeholder': 'Firstname...'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control',
                                                'placeholder': 'Lastname...'})
        }


class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['address', 'city', 'state', 'shipping_zip', 'phone']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control',
                                              'placeholder': 'Address...'}),
            'city': forms.Select(attrs={'class': 'form-select',
                                        'placeholder': 'City...'}),
            'state': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'State...'}),
            'shipping_zip': forms.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'Shipping Zip...'}),
            'phone': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Phone...'})
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username:', max_length=16, help_text="Max 16 symbols",
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Username'
                               }))
    password = forms.CharField(label='Password:', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your Password'
    }))


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Submit Password'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        }))
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your surname'
        }))
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        }))
    birthday = forms.DateTimeField(widget=forms.DateTimeInput(attrs={
        'class': 'form-control',
        'placeholder': 'Birthday'
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'birthday', 'password1', 'password2')

    check = forms.BooleanField(required=True)


def cc_expire_years():
    current_year = datetime.datetime.now().year
    years = range(current_year, current_year + 12)
    return [(str(x), str(x)) for x in years]


def cc_expire_months():
    months = []
    for month in range(1, 13):
        if len(str(month)) == 1:
            numeric = '0' + str(month)
        else:
            numeric = str(month)

        months.append((numeric, datetime.date(2021, 3, 2).strftime('%B')))

    return months


CARD_TYPES = (('Mastercard', 'Mastercard'),
              ('VISA', 'VISA'),
              ('AMEX', 'AMEX'),
              ('Discover', 'Discover'),)


def strip_non_numbers(data):
    """ gets rid of all non-number characters """
    non_numbers = re.compile('\D')
    return non_numbers.sub('', data)


# Gateway test credit cards won't pass this validation
def cardLuhnChecksumIsValid(card_number):
    """ checks to make sure that the card passes a luhn mod-10 checksum """
    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1
    for count in range(0, num_digits):
        digit = int(card_number[count])
        if not ((count & 1) ^ oddeven):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9
        sum = sum + digit
    return ((sum % 10) == 0)

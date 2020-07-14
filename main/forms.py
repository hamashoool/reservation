from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.forms import ModelChoiceField

from .models import User, Restaurant, Table, People, UserType, Time

CHOICES = (
    ('R', 'Restaurant'),
    ('P', 'Person'),
)


class EmailValidationOnForgotPassword(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "There is no user registered with the specified E-Mail address."
            self.add_error('email', msg)
        return email


class CustomUserForm(forms.ModelForm):
    who = forms.ChoiceField(choices=CHOICES, required=True, help_text="This field is required. Choose One.")

    class Meta:
        model = UserType
        fields = [
            'who'
        ]


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.', widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    username = forms.CharField(max_length=30, required=True, help_text='Required.', widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password1 = forms.CharField( required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'password1',
                  'password2',
                  )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            msg = "Email already exists."
            self.add_error('email', msg)
        return email

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
        ]


class UserModelUpdateForm(forms.ModelForm):
    class Meta:
        model = People
        fields = ['profile_image', 'address', 'phone']


class Booking(forms.ModelForm):
    phone = forms.CharField(required=True, help_text="Required, including country code ex.'+1 xxx xxx xxxx'. ", label='Phone')
    address = forms.CharField(max_length=250, help_text="Required, Ex.'Block D, Rd No.1, House 22/L, Bashundhara, Dhaka 1229' ")

    class Meta:
        model = People
        fields = [
            'phone',
            'address',
        ]

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if People.objects.filter(phone=phone).exists():
            msg = "Phone already exists."
            self.add_error('phone', msg)
        return phone


class BookingFormm(forms.ModelForm):
    booked = forms.BooleanField(label='Book this table')

    class Meta:
        model = Table
        fields = ['booked']


class TablesForm(forms.ModelForm):
    name = forms.CharField(max_length=250, label="Table Name")
    time = forms.ModelChoiceField(queryset=Time.objects.all())

    class Meta:
        model = Table
        fields = [
            'name',
            'time',
        ]


class TableUpdateForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['name', 'time']


class RestaurantForm(forms.ModelForm):
    name = forms.CharField(label="Restaurant Name")
    description = forms.CharField(widget=forms.Textarea)
    restaurant_image = forms.ImageField(label="Restaurant Profile")

    class Meta:
        model = Restaurant
        fields = [
            'name',
            'description',
            'restaurant_image'
        ]


class CancelBooking(forms.ModelForm):
    # cancel = course = forms.ModelChoiceField(queryset=Table.objects.all(), widget=forms.HiddenInput)
    booked = forms.BooleanField(label='Cancel Booking')

    class Meta:
        model = Table
        fields = ['booked']

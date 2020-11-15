from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation
from star_ratings.models import Rating

CHOICES = (
    ('R', 'Restaurant'),
    ('P', 'Person'),
)


class UserType(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    who = models.CharField(max_length=1, choices=CHOICES, blank=True)

    def __str__(self):
        return '{}-{}'.format(self.user.username, self.who)


@receiver(post_save, sender=User)
def user_type(sender, instance, created, **kwargs):
    if created:
        UserType.objects.create(user=instance)
    instance.usertype.save()


class RestaurantQuerySet(models.QuerySet):
    def search(self, query=None):
        qs = self
        if query is not None:
            or_lookup = (Q(name__icontains=query) |
                         Q(description__icontains=query) |
                         Q(slug__icontains=query))
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs


class RestaurantManager(models.Manager):
    def get_queryset(self):
        return RestaurantQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset().search(query=query)


class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField()
    restaurant_image = models.ImageField(upload_to='restaurant_images/%Y/%m/%d/', blank=False, default='resta.jpg')
    slug = models.SlugField(default='', editable=False)
    ratings = GenericRelation(Rating, related_query_name='restaurants')
    objects = RestaurantManager()

    def get_absolute_url(self):
        kwargs = {
            'pk': self.id,
            'slug': self.slug
        }
        return reverse('restaurant_detail', kwargs=kwargs)

    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Time(models.Model):
    time = models.CharField(help_text="Write the time like 19:30 or 7:30pm. And max input is 5 digits.", max_length=5)

    def __str__(self):
        return '{}'.format(self.time)


class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    time = models.ForeignKey(Time, on_delete=models.CASCADE, null=True, blank=False)
    booked_by = models.OneToOneField(User, null=True, on_delete=models.SET_NULL, related_name='table_booked', blank=True)
    name = models.CharField(max_length=100, help_text="Table name or number.", blank=False)
    booked = models.BooleanField(default=False)
    slug = models.SlugField(default='', editable=False,)

    def get_absolute_url(self):
        kwargs = {
            'pk': self.id,
            'slug': self.slug
        }
        return reverse('booking', kwargs=kwargs)

    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def is_booked(self):
        # This returns True if booked_by is set, False otherwise
        return self.booked_by_id is not None

    def __str__(self):
        return '{}-{}'.format(self.name, self.restaurant)


class People(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_created=True, null=True)
    phone = models.CharField(help_text="including country code ex.'+1 xxx xxx xxxx'. ", blank=False, null=True, max_length=16)
    address = models.CharField(max_length=250, help_text="Required, "
                                                         "Ex.'Block D, Rd No.1, House 22/L, Bashundhara, Dhaka 1229' ", blank=True)
    profile_image = models.ImageField(upload_to='profile_images/%Y/%m/%d/', blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_people_profile(sender, instance, created, **kwargs):
    try:
        instance.people.save()
    except ObjectDoesNotExist:
        People.objects.create(user=instance)

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class Setting(models.Model):
    hotel_name = models.CharField(max_length=255)
    about_description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    instagram = models.CharField(max_length=3060, blank=True, null=True)
    twitter = models.CharField(max_length=3060, blank=True, null=True)
    facebook = models.CharField(max_length=3060, blank=True, null=True)
    api_key = models.CharField(max_length=3060, blank=True, null=True)


    def clean(self):
        if Setting.objects.exists() and not self.pk:
            raise ValidationError("Only one setting instance is allowed.")

    def __str__(self):
        return f"Settings for {self.hotel_name}"
    
    def save(self, *args, **kwargs):
        if not self.pk and Setting.objects.exists():
            # If there's an existing instance and we're trying to create a new one, raise an error
            raise ValidationError("There is already an instance of Settings. You can only update the existing one.")
        super(Setting, self).save(*args, **kwargs)



# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('viewer', 'Viewer'),
        ('manager', 'Manager'),
        ('supervisor', 'Supervisor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

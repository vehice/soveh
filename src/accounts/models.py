from django.contrib.auth.models import User, Group
from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=250, null=True, blank=True)
    rut = models.CharField(max_length=250, null=True, blank=True)
    phone = models.CharField(max_length=250, null=True, blank=True)
    state = models.IntegerField(default=1, null=True, blank=True)
    signature = models.FileField(upload_to='signatures', blank=True, null=True)
    confirmation_code = models.CharField(max_length=250, null=True, blank=True)
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.username

    class Meta:
        default_permissions = ()

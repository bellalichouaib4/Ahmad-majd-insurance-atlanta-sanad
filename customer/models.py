from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    """Represents an insured client (Assuré)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/Customer/', null=True, blank=True)
    address = models.CharField(max_length=200, blank=True, verbose_name="Adresse")
    mobile = models.CharField(max_length=20, verbose_name="Téléphone")
    cin = models.CharField(max_length=20, blank=True, verbose_name="CIN")

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.get_name or self.user.username

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

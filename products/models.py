from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, null=False,
                            blank=False, unique=True)


class Product(models.Model):

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    sub_category = models.CharField(max_length=255, default="")
    image = models.ImageField(upload_to="products/", null=True, blank=True)



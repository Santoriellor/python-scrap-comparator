from django.db import models
from django.utils import timezone

class Search(models.Model):
    query = models.CharField('Query', max_length=120, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Search Query: {self.query}"

class Product(models.Model):
    name = models.CharField(max_length=120)
    img_src = models.TextField(blank=True, null=True)
    img_srcset = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_from = models.CharField(max_length=120)  # e.g., 'coop', 'migros'
    search = models.ForeignKey(Search, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Product name: {self.name}"
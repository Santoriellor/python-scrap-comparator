from django.db import models
from django.utils import timezone

# Create your models here.
class Products(models.Model):
    name = models.CharField('Products', max_length=120)
    img_src = models.CharField(max_length=200, blank=True, null = True)
    img_srcset = models.CharField(max_length=500, blank=True, null = True)
    price = models.FloatField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Search(models.Model):
    query = models.CharField('Query', max_length=120)
    products_from_coop = models.TextField(blank=True)
    products_from_migros = models.TextField(blank=True)
    products_from_aldi = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Search Query: {self.query}"
    
    def save(self, *args, **kwargs):
        # Update created_at every time the object is saved
        if not self.id:
            self.created_at = timezone.now()
        return super().save(*args, **kwargs)
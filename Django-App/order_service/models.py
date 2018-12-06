from django.db import models

# Create your models here.


class Product(models.Model):
    productId = models.IntegerField(unique=True)

    def __str__(self):
        return f"Product Code: {self.productId}"


class Order(models.Model):
    productCode = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    user = models.CharField(max_length=64, default="devin.mens@sap.com")
    order_amount = models.IntegerField(default=1)
    placed = models.BooleanField(default=True)
    created_at = models.FloatField()

    def __str__(self):
        return f"Order:{self.id}, User:{self.user}, {self.productCode}, Quantity: {self.order_amount}, Created: {self.created_at}, Placed: {self.placed}"


class StockLevel(models.Model):
    productId = models.OneToOneField(Product, on_delete=models.DO_NOTHING)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.productId}, Amount: {self.amount}"

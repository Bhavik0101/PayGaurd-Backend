from django.db import models
from users.models import CustomUser
# Create your models here.

class Transaction(models.Model):
    STATUS_CHOICES=[
        ('Pending','Pending'),
        ('Success','Success'),
        ('Flagged','Flagged'),
        ('Failed','Failed'),
        ('Fraud','Fraud')

    ]
  

    merchant=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=12,decimal_places=2)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES)
    created_at=models.DateTimeField(auto_now_add=True)
    payment_id=models.CharField(max_length=100,unique=True,null=True,blank=True)

    def __str__(self):
        return f"{self.merchant.email} - {self.amount}"
    
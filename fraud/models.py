from django.db import models

# Create your models here.
from transactions.models import Transaction
class FraudCheck(models.Model):
    transaction=models.OneToOneField(Transaction,on_delete=models.CASCADE)
    score=models.IntegerField(default=0)
    reasons=models.JSONField(default=list)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction.id}-score{self.score}"
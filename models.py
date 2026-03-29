from django.db import models

class Account(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    balance = models.FloatField(default=0)

class Transaction(models.Model):

    account=models.ForeignKey(Account,on_delete=models.CASCADE)

    type=models.CharField(max_length=20)

    amount=models.IntegerField()

    balance_before=models.IntegerField()

    balance_after=models.IntegerField()

    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
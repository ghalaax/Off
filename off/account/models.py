from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import Sum
from django.dispatch import receiver
from django.utils.translation import gettext
import uuid


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    system_account = models.BooleanField(default=False)

    def credits(self):
        total_credits = self.transaction_credit.aggregate(
            value=Sum('value'))
        total_debits = self.transaction_debit.aggregate(value=
            Sum('value'))
        result = (total_credits['value'] or 0) - (total_debits['value'] or 0)
        return result if result > 0 else 0

    def __str__(self):
        if self.system_account:
            return 'system:' + str(self.user)
        return 'user:' + str(self.user)


class Block(models.Model):
    pass


class Transaction(models.Model):
    CREATION_TYPE = 'CREATION'
    EXCHANGE_TYPE = 'EXCHANGE'
    TRANSACTION_TYPES = [(CREATION_TYPE, gettext('CREATION')),
                         (EXCHANGE_TYPE, gettext('EXCHANGE'))]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_from = models.ForeignKey(
        Account, null=True, on_delete=models.SET_NULL, db_index=True, related_name="transaction_debit")
    account_to = models.ForeignKey(
        Account, null=True, on_delete=models.SET_NULL, db_index=True, related_name='transaction_credit')
    created_on = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(default="system")
    value = models.PositiveIntegerField()
    transtype = models.CharField(max_length=10, choices=TRANSACTION_TYPES)

    class Meta:
        ordering = ['-created_on']
        indexes = [
            models.Index(fields=['-created_on'])
        ]

    def __str__(self):
        return str(self.id) + ':' + str(self.account_from) + '->' + str(self.account_to) + ':' + str(self.value)


@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)

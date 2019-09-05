from off.account.models import Transaction
from django.db import transaction
from off.account.services.preconditions import Preconditions


class Services:

    @staticmethod
    @transaction.atomic
    def CreateTransaction(value, account_from, account_to, reason=None, transaction_type=Transaction.EXCHANGE_TYPE):
        trans = Transaction()
        trans.account_from = account_from
        trans.account_to = account_to
        trans.value = value
        trans.transtype = transaction_type
        trans.reason = reason
        trans.save()
        return trans

    @staticmethod
    @transaction.atomic
    def CreateCreationTransaction(value, account_from, account_to, reason=None):
        return Services.CreateTransaction(value, account_from, account_to, transaction_type=Transaction.CREATION_TYPE, reason=reason)
    
    @staticmethod
    @transaction.atomic
    def DeleteTransaction(transaction:Transaction):
        transaction.delete()
        return transaction

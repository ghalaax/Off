from OffAccount.models import OffTransaction
from django.db import transaction
from OffAccount.services.preconditions import Preconditions


class Services:

    @staticmethod
    @transaction.atomic
    def CreateTransaction(value, account_from, account_to, reason=None, transaction_type=OffTransaction.EXCHANGE_TYPE):
        trans = OffTransaction()
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
        return Services.CreateTransaction(value, account_from, account_to, transaction_type=OffTransaction.CREATION_TYPE, reason=reason)
    
    @staticmethod
    @transaction.atomic
    def DeleteTransaction(transaction:OffTransaction):
        transaction.delete()
        return transaction

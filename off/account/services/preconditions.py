

class SameAccountException(Exception):
    pass


class NotSystemAccountException(Exception):
    pass


class NotEnoughCreditsException(Exception):
    def __init__(total, count, *args, **kwargs):
        super().__init__(args, kwargs)
        self.total = total
        self.count = count


class Preconditions:
    @staticmethod
    def ensure_different_accounts(account1, account2):
        if account1 == account2:
            raise SameAccountException()

    @staticmethod
    def ensure_account_can_create_credit(account):
        if not account.system_account:
            raise NotSystemAccountException()

    @staticmethod
    def ensure_account_can_afford(account, count):
        total_account_credits = account.credits()
        if total_account_credits < count:
            raise NotEnoughCreditsException(total_account_credits, count)

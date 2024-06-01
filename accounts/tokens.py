from django.contrib.auth.tokens import PasswordResetTokenGenerator
import datetime
from django.conf import settings

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _num_days(self, dt):
        return (dt - datetime.date(2001, 1, 1)).days

    def _today(self):
        return self._num_days(datetime.date.today())

    def check_token(self, user, token):
        try:
            ts_b36, hash = token.split("-")
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False
        if (self._today() - ts) > settings.ACCOUNT_ACTIVATION_DAYS:
            return False
        return self._make_hash_value(user, ts) == hash




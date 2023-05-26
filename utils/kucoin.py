from kucoin.client import Client as _Client


class Client(_Client):
    def __init__(self, user):
        super().__init__(user.kc_key, user.kc_secret, user.kc_passphrase)

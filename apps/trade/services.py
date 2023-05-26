from .models import Trader, Account, Order
from django.db.models import F
from django.utils import timezone
from kucoin.client import Client
from kucoin.exceptions import KucoinAPIException


def validate_kucoin_credentials(key, secret, passphrase):
    try:
        Client(key, secret, passphrase).get_accounts()
    except KucoinAPIException as e:
        raise ValueError('Invalid credentials') from e


def sync_accounts(accounts, trader):
    for account_data in accounts:
        account = Account.objects.filter(trader=trader, kc_id=account_data['id']).first()
        if not account:
            account = Account.objects.create(
                trader=trader,
                kc_id=account_data['id'],
                currency=account_data['currency'],
                type=account_data['type'],
                balance=account_data['balance'],
                available=account_data['available'],
                holds=account_data['holds'],
            )
        else:
            account.balance = account_data['balance']
            account.available = account_data['available']
            account.holds = account_data['holds']
        account.save()


# def sync_orders(orders, trader):
#     for order_data in orders:
#         order = Order.objects.filter(trader=trader, kc_id=order_data['id']).first()
#         if not account:
#             account = Account.objects.create(
#                 trader=trader,
#                 kc_id=account_data['id'],
#                 currency=account_data['currency'],
#                 type=account_data['type'],
#                 balance=account_data['balance'],
#                 available=account_data['available'],
#                 holds=account_data['holds'],
#             )
#         else:
#             account.balance = account_data['balance']
#             account.available = account_data['available']
#             account.holds = account_data['holds']
#         account.save()


def sync_trader(trader):
    client = Client(trader.kc_key, trader.kc_secret, trader.kc_passphrase)

    accounts = client.get_accounts()
    sync_accounts(accounts, trader)

    # if trader.is_master:
    #     orders = client.get_orders()
        # sync_orders(orders, trader)

    trader.kc_last_sync = timezone.now()
    trader.save()


def sync_traders():
    # traders_to_sync = Trader.objects.all().order_by(
    #     F('kc_last_sync').asc(nulls_first=True)
    # )[:10]
    traders_to_sync = Trader.objects.all()

    for trader in traders_to_sync:
        sync_trader(trader)

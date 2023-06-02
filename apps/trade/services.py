from .models import Trader, Account, Order
from django.db.models import F
from django.utils import timezone
from kucoin.client import Client
from kucoin.exceptions import KucoinAPIException
import datetime


def validate_kucoin_credentials(key, secret, passphrase, write_access=False):
    try:
        Client(key, secret, passphrase).create_limit_order(
            symbol='FOO-BAR',
            side='sell',
            price='10',
            size='10',
        )
    except KucoinAPIException as e:
        if e.code in ['400003', '400004', '400005']:
            raise ValueError('Invalid Kucoin Credentials')
        elif e.code in ['400007']:
            if write_access:
                raise ValueError('Invalid Kucoin Permissions')
        elif e.code not in ['900001']:
            raise ValueError('Unexpected Error Occurred')


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


def sync_orders(orders, trader):
    for order_data in orders:
        order = Order.objects.filter(trader=trader, kc_id=order_data['id']).first()  # TODO: fix n+1 select

        if not order:
            order = Order.objects.create(
                trader=trader,
                kc_id=order_data['id'],
                kc_created_at=timezone.make_aware(datetime.datetime.fromtimestamp(int(order_data['createdAt'] / 1000))),
                src_currency=order_data['symbol'].split('-')[0],
                dst_currency=order_data['symbol'].split('-')[1],
                price=order_data['price'],
                size=order_data['size'],
            )

            # TODO: open position, reflect to all slaves

            order.save()

    for order in Order.objects.filter(trader=trader, status=Order.Status.ACTIVE):
        order_data = list(filter(lambda o: o['id'] == order.kc_id, orders))
        if not order_data:
            order.status = Order.Status.CANCELLED

            # TODO: close position, reflect to all slaves

            order.save()


def sync_trader(trader):
    client = Client(trader.kc_key, trader.kc_secret, trader.kc_passphrase)

    accounts = client.get_accounts()
    sync_accounts(accounts, trader)

    if trader.is_master:
        orders = client.get_orders(status='active')['items']  # TODO: handle pagination
        sync_orders(orders, trader)

    trader.kc_last_sync = timezone.now()
    trader.save()


def sync_traders():
    traders_to_sync = Trader.objects.all().order_by(
        F('kc_last_sync').asc(nulls_first=True)
    )[:10]

    for trader in traders_to_sync:
        sync_trader(trader)

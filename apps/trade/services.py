from .models import Trader, Account, Order, Follow
from django.db.models import F, OuterRef, Exists, Subquery, Case, When, Sum
from django.utils import timezone
from kucoin.client import Trade as Client, Market
from django.conf import settings
import datetime
import json
import redis

redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)


def get_kucoin_api_error_code(e: Exception):
    return json.loads('-'.join(str(e).split('-')[1:])).get('code', '85000')


def validate_kucoin_credentials(key, secret, passphrase, write_access=False):
    try:
        Client(key, secret, passphrase).create_limit_order(
            symbol='FOO-BAR',
            side='sell',
            price='10',
            size='10',
        )
    except Exception as e:
        code = get_kucoin_api_error_code(e)
        if code in ['400003', '400004', '400005']:
            raise ValueError('Invalid Kucoin Credentials')


def create_trader(user, is_master, key, secret, passphrase):
    trader = Trader(
        user=user,
        is_master=is_master,
        kc_key=key,
        kc_secret=secret,
        kc_passphrase=passphrase,
    )

    client = Client(key, secret, passphrase)

    try:
        client.create_limit_order(
            symbol='FOO-BAR',
            side='sell',
            price='10',
            size='10',
        )
    except Exception as e:
        code = get_kucoin_api_error_code(e)
        if code in ['900001']:
            trader.kc_spot_access = True

    try:
        client.create_limit_margin_order(
            symbol='FOO-BAR',
            side='sell',
            price='10',
            size='10',
        )
    except Exception as e:
        code = get_kucoin_api_error_code(e)
        if code in ['400312']:
            trader.kc_margin_access = True

    trader.save()


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

    accounts = client._request('GET', '/api/v1/accounts', params={})
    if type(accounts) is list:
        sync_accounts(accounts, trader)

    # if trader.is_master:
    #     orders = client.get_order_list(status='active')['items']  # TODO: handle pagination
    #     sync_orders(orders, trader)
    #
    # trader.kc_last_sync = timezone.now()
    # trader.save()


def sync_traders():
    traders_to_sync = Trader.objects.all().order_by(
        F('kc_last_sync').asc(nulls_first=True)
    )[:10]

    for trader in traders_to_sync:
        sync_trader(trader)


def cancel_order(kc_id):
    Order.objects.filter(kc_id=kc_id).update(status=Order.Status.CANCELLED)
    for order in Order.objects.filter(origin__kc_id=kc_id).select_related('trader'):
        try:
            client = Client(order.trader.kc_key, order.trader.kc_secret, order.trader.kc_passphrase)
            client.cancel_order(order.kc_id)
        except Exception as e:
            print(e)
        order.status = Order.Status.CANCELLED
        order.save()


def create_order(trader_id, order_data):
    order = Order.objects.create(
        trader_id=trader_id,
        kc_id=order_data['orderId'],
        kc_created_at=timezone.make_aware(datetime.datetime.fromtimestamp(int(order_data['orderTime'] / 1000))),
        src_currency=order_data['symbol'].split('-')[0],
        dst_currency=order_data['symbol'].split('-')[1],
        price=float(order_data['price']),
        size=float(order_data['size']),
        side=order_data['side'],
    )

    master_account = Account.objects.get(trader_id=trader_id, currency=order.src_currency, type='trade')
    # ratio = order.size / (order.size + master_account.available)
    ratio = order.size / master_account.available

    account_query = Account.objects.filter(trader_id=OuterRef('pk'), currency=order.src_currency)

    slaves = Trader.objects.annotate(
        is_followed=Exists(Follow.objects.filter(master_id=trader_id, slave=OuterRef('pk'))),
        my_account_available=Subquery(account_query.values("available")[:1]),
    ).filter(is_followed=True)

    for slave in slaves:
        size = ratio * slave.my_account_available

        if not size:
            continue

        try:
            client = Client(slave.kc_key, slave.kc_secret, slave.kc_passphrase)
            res = client.create_limit_order(
                symbol="%s-%s" % (order.src_currency, order.dst_currency),
                side=order_data['side'],
                size='{:.8f}'.format(size).rstrip('0'),
                price='{:20.1f}'.format(order.price).lstrip(),
            )

            Order.objects.create(
                trader=slave,
                kc_id=res['orderId'],
                kc_created_at=timezone.now(),
                src_currency=order.src_currency,
                dst_currency=order.dst_currency,
                price=order.price,
                size=size,
                side=order_data['side'],
                origin=order,
            )
        except Exception as e:
            print(e)


def process_master_order(master_id, order_data):
    if order_data['type'] == 'open':
        create_order(master_id, order_data)

    if order_data['type'] == 'filled':
        Order.objects.filter(kc_id=order_data['orderId']).update(status=Order.Status.DONE)

    if order_data['type'] == 'match':
        if not Order.objects.filter(kc_id=order_data['orderId']).exists():
            create_order(master_id, order_data)

    if order_data['type'] == 'canceled':
        cancel_order(order_data['orderId'])


def update_master_balance(master_id, balance_data):
    pass


def calculate_profits_by_master(trader):
    profits = Order.objects.filter(trader=trader, status=Order.Status.DONE, origin__isnull=False).select_related(
        'origin__trader').annotate(
        size_change=Case(
            When(side=Order.Side.SELL, then=-F('size')),
            When(side=Order.Side.BUY, then=F('size')),
        ),
        price_change=Case(
            When(side=Order.Side.SELL, then=F('price')),
            When(side=Order.Side.BUY, then=-F('price')),
        ),
    ).values('origin__trader', 'origin__trader__user__username', 'src_currency', 'dst_currency').annotate(
        total_size_change=Sum('size_change'),
        total_price_change=Sum('price_change'),
    )

    return [{
        'trader_id': row['origin__trader'],
        'trader_username': row['origin__trader__user__username'],
        'src_currency': row['src_currency'],
        'dst_currency': row['dst_currency'],
        'total_size_change': row['total_size_change'],
        'total_price_change': row['total_price_change'],
        'total_usd_change': row['total_size_change'] * float(redis_client.get('symbol:'+row['src_currency'])) + row[
            'total_price_change'] * float(redis_client.get('symbol:'+row['dst_currency']))
    } for row in profits]


def update_currencies_from_kucoin():
    client = Market()
    prices = client._request('GET', '/api/v1/prices', params={'base': 'USD'})
    redis_client.mset({'symbol:' + symbol: float(price) for symbol, price in prices.items()})

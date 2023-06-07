from celery import shared_task
from .services import sync_traders, process_master_order, update_master_balance


@shared_task
def sync_kucoin():
    sync_traders()


@shared_task
def dispatch_order(trader_id, order_data):
    process_master_order(trader_id, order_data)


@shared_task
def update_balance(trader_id, balance_data):
    update_master_balance(trader_id, balance_data)
from celery import shared_task
# from .services import sync_traders


@shared_task
def sync_kucoin():
    print("This is a test message")
    # sync_traders()

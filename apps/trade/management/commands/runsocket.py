import asyncio
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient
from django.core.management.base import BaseCommand
from ...models import Trader
from ...tasks import dispatch_order, update_balance


class Command(BaseCommand):
    help = "Runs websocket listeners for master trading orders"

    async def main(self):
        async for trader in Trader.objects.all():
            async def deal_msg(msg):
                topic = msg['topic']
                if topic == '/spotMarket/tradeOrders':
                    dispatch_order.delay(trader.id, msg['data'])
                if topic == '/account/balance':
                    update_balance.delay(trader.id, msg['data'])

            client = WsToken(key=trader.kc_key, secret=trader.kc_secret,
                             passphrase=trader.kc_passphrase)
            ws_client = await KucoinWsClient.create(None, client, deal_msg, private=True)
            await ws_client.subscribe('/spotMarket/tradeOrders')
            await ws_client.subscribe('/account/balance')

        while True:
            self.stdout.write(self.style.SUCCESS('Sleeping to prevent stopping loop'))
            await asyncio.sleep(20)

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())

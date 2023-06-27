from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.myauth.models import User


class Trader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trader')
    is_master = models.BooleanField(default=False)
    kc_key = models.CharField(max_length=24, unique=True)
    kc_secret = models.CharField(max_length=36)
    kc_passphrase = models.CharField(max_length=32)
    kc_last_sync = models.DateTimeField(null=True, blank=True)

    kc_spot_access = models.BooleanField(default=False)
    kc_margin_access = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('trader')
        verbose_name_plural = _('traders')

    def __str__(self):
        return self.user.username


class Follow(models.Model):
    master = models.ForeignKey(Trader, on_delete=models.CASCADE, related_name='followers')
    slave = models.ForeignKey(Trader, on_delete=models.CASCADE, related_name='followings')
    max_loss = models.FloatField(blank=True, null=True)
    max_trading_rate = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = _('following')
        verbose_name_plural = _('followings')
        constraints = (
            models.UniqueConstraint(fields=('master', 'slave'),
                                    name='trade_follow_master_slave_uniq'),
        )

    def __str__(self):
        return "%s → %s" % (self.slave, self.master)


class FollowSymbol(models.Model):
    follow = models.ForeignKey(Follow, on_delete=models.CASCADE, related_name='symbols')
    symbol = models.CharField(max_length=127)


class Account(models.Model):
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE, related_name='accounts')
    kc_id = models.CharField(max_length=24, unique=True)
    currency = models.CharField(max_length=63)
    type = models.CharField(max_length=63)
    balance = models.FloatField(default=.0)
    available = models.FloatField(default=.0)
    holds = models.FloatField(default=.0)

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')

    def __str__(self):
        return "%s %s" % (self.trader, self.currency)


class Order(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('active')
        DONE = 'DONE', _('done')
        CANCELLED = 'CANCELLED', _('cancelled')

    class Side(models.TextChoices):
        SELL = 'sell', _('sell')
        BUY = 'buy', _('buy')

    trader = models.ForeignKey(Trader, on_delete=models.CASCADE, related_name='orders')
    origin = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='copies', blank=True, null=True)
    status = models.CharField(max_length=63, choices=Status.choices, default=Status.ACTIVE)
    kc_id = models.CharField(max_length=24, unique=True)
    kc_created_at = models.DateTimeField()
    src_currency = models.CharField(max_length=63)
    dst_currency = models.CharField(max_length=63)
    price = models.FloatField()
    side = models.CharField(max_length=15, choices=Side.choices)
    size = models.FloatField()
    src_usd = models.FloatField()
    dst_usd = models.FloatField()

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return "%s %s-%s" % (self.trader, self.src_currency, self.dst_currency)

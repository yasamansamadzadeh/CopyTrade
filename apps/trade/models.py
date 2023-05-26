from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.myauth.models import User


class Trader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trader')
    is_master = models.BooleanField(default=False)
    kc_key = models.CharField(max_length=24)
    kc_secret = models.CharField(max_length=36)
    kc_passphrase = models.CharField(max_length=32)

    class Meta:
        verbose_name = _('trader')
        verbose_name_plural = _('traders')

    def __str__(self):
        return self.user.username


class Follow(models.Model):
    master = models.ForeignKey(Trader, on_delete=models.CASCADE, related_name='followers')
    slave = models.ForeignKey(Trader, on_delete=models.CASCADE, related_name='followings', unique=True)

    class Meta:
        verbose_name = _('following')
        verbose_name_plural = _('followings')
        constraints = (
            models.UniqueConstraint(fields=('master', 'slave'),
                                    name='trade_follow_master_slave_uniq'),
        )

    def __str__(self):
        return "%s → %s" % (self.slave, self.master)

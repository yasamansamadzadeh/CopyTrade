# Generated by Django 4.2.1 on 2023-05-26 14:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Trader',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_master', models.BooleanField(default=False)),
                ('kc_key', models.CharField(max_length=24)),
                ('kc_secret', models.CharField(max_length=36)),
                ('kc_passphrase', models.CharField(max_length=32)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='trader', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'trader',
                'verbose_name_plural': 'traders',
            },
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='trade.trader')),
                ('slave', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followings', to='trade.trader', unique=True)),
            ],
            options={
                'verbose_name': 'following',
                'verbose_name_plural': 'followings',
            },
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('master', 'slave'), name='trade_follow_master_slave_uniq'),
        ),
    ]
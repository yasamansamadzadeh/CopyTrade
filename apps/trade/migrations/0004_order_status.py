# Generated by Django 4.2.1 on 2023-05-26 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0003_trader_kc_last_sync_alter_trader_kc_key_order_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'active'), ('DONE', 'done'), ('CANCELLED', 'cancelled')], default='ACTIVE', max_length=63),
        ),
    ]
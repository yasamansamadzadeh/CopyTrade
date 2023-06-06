# Generated by Django 4.2.1 on 2023-06-06 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0006_trader_kc_margin_access_trader_kc_spot_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='origin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='copies', to='trade.order'),
        ),
    ]

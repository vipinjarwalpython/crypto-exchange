# Generated by Django 4.2.8 on 2024-01-23 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crypto_user', '0012_usercryptowallet_profitandloss'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='transaction_type',
        ),
        migrations.AddField(
            model_name='transaction',
            name='coin_details',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='crypto_user.usercryptowallet'),
            preserve_default=False,
        ),
    ]

# Generated by Django 5.1.3 on 2024-12-02 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autorization', '0004_clientuser_referral_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientuser',
            name='referral_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='реферальный код'),
        ),
    ]

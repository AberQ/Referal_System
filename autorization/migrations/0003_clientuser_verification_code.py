# Generated by Django 5.1.3 on 2024-12-02 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autorization', '0002_clientuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientuser',
            name='verification_code',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='код подтверждения'),
        ),
    ]

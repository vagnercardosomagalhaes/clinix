# Generated by Django 5.2.4 on 2025-07-08 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdigital', '0003_usuarios_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='agenda',
            name='telefone',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Telefone'),
        ),
    ]

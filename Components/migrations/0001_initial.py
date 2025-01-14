# Generated by Django 4.2.16 on 2024-11-17 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('image', models.URLField()),
                ('description', models.TextField()),
                ('usableQuantity', models.PositiveIntegerField()),
                ('safeStockQuantity', models.PositiveIntegerField()),
                ('industryLine', models.CharField(max_length=15)),
                ('suppliedBy', models.CharField(max_length=25)),
            ],
        ),
    ]

# Generated by Django 3.1.6 on 2021-02-22 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fav_products',
            field=models.ManyToManyField(blank=True, to='app.Product'),
        ),
        migrations.AlterField(
            model_name='user',
            name='point',
            field=models.PositiveIntegerField(default=10000),
        ),
    ]

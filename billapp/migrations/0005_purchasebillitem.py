# Generated by Django 4.2.8 on 2024-01-16 03:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0004_purchasebill'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseBillItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField(default=0, null=True)),
                ('total', models.IntegerField(default=0, null=True)),
                ('VAT', models.CharField(max_length=100)),
                ('discount', models.CharField(default=0, max_length=100, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billapp.company')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billapp.item')),
                ('purchasebill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billapp.purchasebill')),
            ],
        ),
    ]

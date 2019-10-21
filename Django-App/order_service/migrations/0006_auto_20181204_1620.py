# Generated by Django 2.1.2 on 2018-12-04 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("order_service", "0005_order_placed")]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="productCode",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="order_service.Product",
            ),
        ),
        migrations.AlterField(
            model_name="stocklevel",
            name="productId",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="order_service.Product",
            ),
        ),
    ]
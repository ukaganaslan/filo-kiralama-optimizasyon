from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0030_vehiclemodel_reservation_preferred_vehicle_model_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dailyprice',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='dailyprice',
            name='vehicle_group',
        ),
        migrations.AddField(
            model_name='dailyprice',
            name='vehicle_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_prices', to='vehicles.vehiclemodel'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='dailyprice',
            unique_together={('date', 'vehicle_model')},
        ),
    ]

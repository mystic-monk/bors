from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('returns', '0006_seed_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='seedlicence',
            name='year',
            field=models.PositiveIntegerField(default=2026),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='seedvehicle',
            name='year',
            field=models.PositiveIntegerField(default=2026),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='seedlicence',
            unique_together={('operator_access', 'year', 'route_no')},
        ),
        migrations.AlterUniqueTogether(
            name='seedvehicle',
            unique_together={('operator_access', 'year', 'vehicle_reg')},
        ),
    ]

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('returns', '0007_seed_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='YearLock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField(unique=True)),
                ('locked_by', models.CharField(blank=True, max_length=200)),
                ('locked_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Year Lock',
                'ordering': ['-year'],
            },
        ),
    ]

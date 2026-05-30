from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('returns', '0008_yearlock'),
    ]

    operations = [
        migrations.AddField(
            model_name='operatoraccess',
            name='is_test',
            field=models.BooleanField(default=False, help_text='Mark as a test account — submissions can be wiped independently of real data.'),
        ),
    ]

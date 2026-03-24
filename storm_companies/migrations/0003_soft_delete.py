# Generated migration for soft delete fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storm_companies', '0002_deployment_deployed_from_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='deployment',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='stormevent',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

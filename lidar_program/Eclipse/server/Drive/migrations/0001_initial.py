# Generated by Django 4.2.5 on 2023-11-08 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Drive',
            fields=[
                ('drive_id', models.AutoField(primary_key=True, serialize=False)),
                ('serial_number', models.CharField(max_length=255)),
                ('storage_total_gb', models.DecimalField(decimal_places=2, max_digits=4)),
                ('storage_used_gb', models.DecimalField(decimal_places=2, max_digits=4)),
                ('file_count', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'drive',
                'managed': False,
            },
        ),
    ]

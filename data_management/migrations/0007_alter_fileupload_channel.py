# Generated by Django 5.0.4 on 2024-05-22 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0006_uploadedfile_remove_fileupload_channel'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileupload',
            name='channel',
            field=models.IntegerField(default=0),
        ),
    ]

# Generated by Django 3.2.8 on 2021-10-18 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default=None, max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='watermark_avatar',
            field=models.ImageField(blank=True, null=True, upload_to='watermark_avatars/'),
        ),
    ]

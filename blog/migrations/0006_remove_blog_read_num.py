# Generated by Django 2.2 on 2019-05-15 02:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_blog_read_num'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blog',
            name='read_num',
        ),
    ]

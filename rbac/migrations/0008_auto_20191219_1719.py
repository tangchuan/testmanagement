# Generated by Django 3.0 on 2019-12-19 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0007_remove_menu_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='icon',
            field=models.CharField(default='fa-th-large', max_length=32, verbose_name='菜单图标'),
        ),
        migrations.AlterField(
            model_name='user',
            name='realname',
            field=models.CharField(max_length=150, verbose_name='姓名'),
        ),
    ]

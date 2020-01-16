# Generated by Django 3.0 on 2019-12-12 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='菜单名')),
                ('priority', models.IntegerField(blank=True, help_text='菜单的显示顺序，优先级越小显示越靠前', null=True, verbose_name='显示优先级')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('parent', models.ForeignKey(blank=True, help_text='如果添加的是子菜单，请选择父菜单', null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.Menu', verbose_name='父级菜单')),
            ],
            options={
                'verbose_name': '菜单表',
                'verbose_name_plural': '菜单表',
                'ordering': ['priority', 'id'],
            },
        ),
    ]

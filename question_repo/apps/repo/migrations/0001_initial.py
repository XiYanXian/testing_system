# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-07 02:00
from __future__ import unicode_literals

import apps.repo.validator
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='分类名')),
            ],
            options={
                'verbose_name': '分类',
                'verbose_name_plural': '分类',
            },
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.IntegerField(blank=True, choices=[(1, '入门'), (2, '简单'), (3, '中等'), (4, '困难'), (5, '超难')], null=True, validators=[apps.repo.validator.valid_difficulty], verbose_name='题目难度')),
                ('title', models.CharField(max_length=256, unique=True, verbose_name='题目标题')),
                ('content', models.TextField(blank=True, null=True, verbose_name='题目详情')),
                ('answer', models.TextField(blank=True, null=True, verbose_name='题目答案')),
                ('pub_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='入库时间')),
                ('status', models.BooleanField(default=False, verbose_name='审核状态')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repo.Category', verbose_name='分类')),
                ('contributor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='贡献者')),
            ],
            options={
                'verbose_name': '题库',
                'verbose_name_plural': '题库',
                'permissions': (('can_change_question', '可以修改题目'), ('can_add_question', '可以添加题目')),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='标签名')),
            ],
            options={
                'verbose_name': '标签',
                'verbose_name_plural': '标签',
            },
        ),
        migrations.AddField(
            model_name='questions',
            name='tag',
            field=models.ManyToManyField(to='repo.Tag', verbose_name='题目标签'),
        ),
    ]

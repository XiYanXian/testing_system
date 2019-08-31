from django.db import models
from django.contrib.auth.models import AbstractUser
from easy_thumbnails.fields import ThumbnailerImageField
# 继承自AbstractUser


class User(AbstractUser):
    realname = models.CharField(max_length=8, verbose_name="真实姓名")
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    qq = models.CharField(max_length=11, verbose_name="QQ号")
    avator_sor = ThumbnailerImageField(upload_to="avator/%Y%m%d/", default="avator/default.jpg", verbose_name="头像")


class FindPassword(models.Model):
    verify_code = models.CharField(max_length=128, verbose_name="验证码")
    email = models.EmailField(verbose_name='邮箱')
    create_time = models.DateTimeField(auto_now=True, verbose_name="重置时间")
    status = models.BooleanField(default=False, verbose_name="是否已重置")

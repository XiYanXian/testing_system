"""
@file:   handler.py
@date:   2019/08/12
"""
from django.dispatch import receiver
from django.core.signals import request_finished
from django.db.models.signals import post_save


# @receiver(request_finished)
# def all_log(sender, **kwargs):
#     print(sender, kwargs)
#     print("使用信号记日志...")

# @receiver(post_save, sender=)
# def send_mail(sender, )

# 当创建一条记录MailLog之后就会自动执行发送邮件
"""
@receiver(post_save, sender=MailLog)
def send_mail(sender, instance, **kwargs):
    pass
"""
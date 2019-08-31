# Create your views here.
from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib import auth
from django.contrib.auth.hashers import make_password
import logging
from .forms import RegisterForm, LoginForm
from .models import User, FindPassword
import random
import string
from django.core.mail import send_mail
from question_repo.settings import EMAIL_FROM
logger = logging.getLogger('account')


# Create your views here.

class Register(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        from django.core.cache import cache
        ret = {"status": 400, "msg": "调用方式错误"}
        if request.is_ajax():
            form = RegisterForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                mobile = form.cleaned_data["mobile"]
                mobile_captcha = form.cleaned_data["mobile_captcha"]
                mobile_captcha_reids = cache.get(mobile)
                if mobile_captcha == mobile_captcha_reids:
                    user = User.objects.create(username=username, password=make_password(password))
                    user.save()
                    ret['status'] = 200
                    ret['msg'] = "注册成功"
                    logger.debug(f"新用户{user}注册成功！")
                    user = auth.authenticate(username=username, password=password)
                    if user is not None and user.is_active:
                        auth.login(request, user)
                        logger.debug(f"新用户{user}登录成功")
                    else:
                        logger.error(f"新用户{user}登录失败")
                else:
                    # 验证码错误
                    ret['status'] = 401
                    ret['msg'] = "验证码错误或过期"
            else:
                ret['status'] = 402
                ret['msg'] = form.errors
        logger.debug(f"用户注册结果：{ret}")
        return JsonResponse(ret)


class Login(View):

    def get(self, request):
        # 如果一登录，则直接跳转到index页面
        if request.user.is_authenticated:
            return redirect(reverse('repo: index'))
        form = LoginForm()
        # 设置下一跳转地址
        request.session['next'] = request.GET.get('next', reverse('repo:index'))
        return render(request, 'login.html', {'form': form})

    # Form表单直接提交
    def post(self, request):
        # 表单数据绑定
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            captcha = form.cleaned_data['captcha']
            session_captcha_code = request.session.get('captcha_code', '')
            logger.debug(f'登录提交验证码：{captcha}-{session_captcha_code}')
            # 验证码一致
            if captcha.lower() == session_captcha_code.lower():
                user, flag = form.check_password()
                # user = auth.authenticate(username=username, password=password)
                if flag and user is not None and user.is_active:
                    auth.login(request, user)
                    logger.info(f"{user.username}登录成功")
                    # 跳转到next
                    return redirect(request.session.get("next", '/'))
                msg = "用户名或密码错误"
                logger.error(f"{username}登录失败, 用户名或密码错误")
            else:
                msg = "验证码错误"
                logger.error(f'{username}登陆失败，验证码错误')
        else:
            msg = "表单数据不完整"
            logger.error(form.errors)
            logger.error(msg)
        return render(request, "login.html", {"form": form, "msg": msg})


def logout(request):
    auth.logout(request)
    return redirect('/accounts/login/')


class PasswordForget(View):
    def get(self, request):
        return render(request, "password_forget.html")

    def post(self, request):
        email = request.POST.get("email")
        if email and User.objects.filter(email=email):
            verify_code = "".join(random.choices(string.ascii_lowercase+string.digits, k=128))
            url = f"{request.scheme}://{request.META['HTTP_HOST']}/accounts/password/reset/{verify_code}?email={email}"
            ret = FindPassword.objects.get_or_create(email=email)
            # (<FindPassword: FindPassword object>, True)
            ret[0].verify_code = verify_code
            ret[0].status = False
            ret[0].save()
            email_title = '找回密码验证信息'
            email_body = f'点击下面的链接进行验证，有效时间30分钟\n' \
                f'{url}'
            send_mail(email_title, email_body, EMAIL_FROM, [email])
            return HttpResponse("邮件发送成功，请登录邮箱查看!如果没收到，请到垃圾箱查看是否存在！")
        else:
            msg = "输入的邮箱不存在！"
            return render(request, "password_forget.html", {"msg": msg})


class PasswordReset(View):
    def get(self, request, verify_code):
        import datetime
        create_time_newer = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        email = request.GET.get("email")
        # 邮箱、verify_code、status=False、时间近30分钟
        find_password = FindPassword.objects.filter(status=False, verify_code=verify_code, email=email,
                                                    create_time__gte=create_time_newer)
        # great_then_equal, lte, lt, gt
        if verify_code and find_password:
            return render(request, "password_reset.html")
        else:
            return HttpResponse("链接失效或有误")

    def post(self, request, verify_code):
        import datetime
        create_time_newer = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if password2 == password1:
            try:
                find_password = FindPassword.objects.get(status=False, verify_code=verify_code,
                                                         creat_time__gte=create_time_newer)
                user = User.objects.get(email=find_password.email)
                user.set_password(password1)
                user.save()
                msg = "重置密码成功，请登录"
                find_password.status = True
                find_password.save()
            except Exception as ex:
                # 记日志 ex
                msg = "出错啦"
        else:
            msg = "两次密码不一致"
        return render(request, "password_reset.html", {"msg": msg})
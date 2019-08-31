from django.shortcuts import render
import logging
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View, ListView
from django.contrib import auth
from django.http import JsonResponse
from apps.repo.models import Answers, Questions
logger = logging.getLogger('account')
# Create your views here.


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "uc_profile.html")

    def post(self, request):
        ret_info = {"code": 200, "msg": "修改成功"}
        try:
            if request.POST.get("email"):
                request.user.email = request.POST.get("email")
            if request.POST.get("mobile"):
                request.user.mobile = request.POST.get("mobile")
            if request.POST.get("qq"):
                request.user.qq = request.POST.get("qq")
            if request.POST.get("realname"):
                request.user.realname = request.POST.get("realname")
            request.user.save()
        except Exception as ex:
            ret_info = {"code": 200, "msg": "修改失败"}
        return render(request, "uc_profile.html", {"ret_info": ret_info})


class ChangePasswdView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'uc_change_passwd.html')

    def post(self, request):
        old_password = request.POST.get("oldpassword")
        new_password1 = request.POST.get('newpassword1')
        new_password2 = request.POST.get('newpassword2')

        # 前端验证 new_password1 == new_password2 才能提交
        if new_password1 != new_password2:
            ret_info = {"code": 400, "msg": "新密码不一致"}
        else:
            user = auth.authenticate(username=request.user.username, password=old_password)
            if user:
                user.set_password(new_password1)
                user.save()
                auth.logout(request)
                ret_info = {'code': 200, 'msg': '修改成功'}
            else:
                ret_info = {'code': 400, 'msg': '旧密码不正确'}
        return render(request, 'uc_change_passwd.html', {'ret_info': ret_info})


class AnswerView(LoginRequiredMixin, ListView):
    model = Answers
    template_name = 'uc_answer.html'
    context_object_name = 'my_answers'

    def get_queryset(self):
        return Answers.objects.filter(user=self.request.user)


class ApprovalView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # 'app.权限'
    permission_required = ('repo.can_change_question_status',)
    # 如果权限不够,是做跳转还是403, True=>403(默认False)
    raise_exception = True

    def get(self, request):
        # print(request.user.get_all_permissions())
        questions = Questions.objects.exclude(status=True)
        return render(request, "uc_approval.html", {"questions": questions})


class ApprovalPassView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # 'app.权限'
    permission_required = ('repo.can_change_question_status',)
    # 如果权限不够,是做跳转还是403, True=>403(默认False)
    raise_exception = True

    def get(self, request, id):
        try:
            Questions.objects.filter(id=id).update(status=True)
            ret = {"code": 200, "msg": "成功"}
        except:
            ret = {"code": 500, "msg": "失败"}
        return JsonResponse(ret)
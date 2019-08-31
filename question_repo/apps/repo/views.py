from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, DetailView
from .models import Category, Questions, Answers, UserLog, User
import logging
import json
from django.http import JsonResponse
from django.core import serializers
from django.db import transaction
from django.db.models import Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
logger = logging.getLogger("repo")
# Create your views here.


@login_required
def index(request):
    userlog = UserLog.objects.all().order_by('-create_time')[:10]
    # 最近刷题的同学（取10个）
    recent_user_ids = [item['user'] for item in UserLog.objects.filter(operate=3).values("user").distinct()[:10]]
    recent_user = User.objects.filter(id__in=recent_user_ids)
    # 答题数量及总量
    answer_num = Answers.objects.filter(user=request.user).count()
    question_all = Questions.objects.all().__len__()
    # 用户总量
    user_sum = len(User.objects.all())
    # 答题情况
    # 每个用户答题数量：按用户统计答题数量
    rank = Answers.objects.values('user').annotate(Count('id'))
    rank = sorted(rank, key=lambda item: item['id__count'], reverse=True)
    # 统计每个人的排名(为提升效率，可写入memcache)
    rank_dict = {}
    # 当前排名
    cur_rank = 0
    # 刷题数量
    cur_count = 0
    for index, item in enumerate(rank, start=1):
        # 如果上一名的刷题数据与自己不一样，则更新排名（否则跟上一名同名次）
        if cur_count != item["id__count"]:
            cur_rank = index
        cur_count = item["id__count"]
        rank_dict[item["user"]] = dict(item, **{"rank": cur_rank})
    # 热门算法题目
    hot_questions = Answers.objects.hot_question()
    # 近30天用户刷题排行
    hot_user = Answers.objects.hot_user()

    kwgs = {
        "userlog": userlog,
        "recent_user": recent_user,
        "answer_num": answer_num,
        "question_all": question_all,
        "user_sum": user_sum,
        "rank": rank_dict[request.user.id] if answer_num else {"rank": 0, },
        "hot_questions": hot_questions,
        "hot_user": hot_user,

    }
    return render(request, 'index.html', kwgs)


class QuestionsList(View):
    def get(self, request):
        category = Category.objects.all().values("id", "name")
        grades = Questions.DIF_CHOICE
        search = request.GET.get('search', '')
        kwgs = {"category": category, "grades": grades, "search_key": search}
        return render(request, 'questions.html', kwgs)


class QuestionDetail(LoginRequiredMixin, DetailView):
    model = Questions
    pk_url_kwarg = 'id'
    template_name = "question_detail.html"
    # 默认名：object
    context_object_name = "object"

    # 额外传递my_answer
    def get_context_data(self, **kwargs):
        # kwargs：字典、字典中的数据返回给html页面
        # self.get_object() => 获取当前id的数据（问题）
        question = self.get_object()  # 当前这道题目
        kwargs["my_answer"] = Answers.objects.filter(
            question=question, user=self.request.user)
        return super().get_context_data(**kwargs)

    def post(self, request, id):
        try:
            with transaction.atomic():
                # 没有回答过。create
                # 更新回答。get->update
                # 获取对象，没有获取到直接创建对象
                new_answer = Answers.objects.get_or_create(
                    question=self.get_object(), user=self.request.user)
                # 元组：第一个元素获取/创建的对象， True（新创建）/False（老数据）
                new_answer[0].answer = request.POST.get("answer", "没有提交答案信息")
                new_answer[0].save()
                # serializers.serialize 将 queryset 转换成 json格式
                # json.loads()函数是将json格式数据转换为字典（可以这么理解，json.loads()函数是将字符串转化为字典）
                my_answer = json.loads(serializers.serialize("json", [new_answer[0]]))[0]["fields"]
                print(my_answer)
                # OPERATE = ((1, "收藏"), (2, "取消收藏"), (3, "回答"))
                UserLog.objects.create(user=request.user, operate=3, question=self.get_object())
            msg = "提交成功"
            code = 200
        except Exception as ex:
            logger.error(ex)
            my_answer = {}
            msg = "提交失败"
            code = 500
        result = {"status": code, "msg": msg, "my_answer": my_answer}
        return JsonResponse(result)


class Question(LoginRequiredMixin, View):
    def post(self, request):
        print(request.POST)
        try:
            title = request.POST.get("title")
            category = request.POST.get("category")
            content = request.POST.get("content")
            if category:
                Questions.objects.create(title=title, category_id=category, content=content, contributor=request.user)
            else:
                Questions.objects.create(title=title, content=content, contributor=request.user)
        except Exception as ex:
            logger.error(ex)
            return HttpResponse("提交失败!")
        return HttpResponse("提交成功")


def listing(request):
    contact_list = Questions.objects.all()
    # pagesize = request.GET.get('pagesize')
    paginator = Paginator(contact_list, 25)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'list.html', {'contacts': contacts,})
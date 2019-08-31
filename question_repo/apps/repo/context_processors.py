"""
@file:   context_processors.py
@date:   2019/08/13
"""
# 需要到settings里配置
from apps.repo.models import Answers, Category


def repo_data(request):
    # if request.user.is_authenticated:
    #     user_data = user_answer_data(request.user)
    category = Category.objects.all()
    current_url = request.path
    return locals()

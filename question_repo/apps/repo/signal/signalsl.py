import django.dispatch

# 自定义信号
mysignal = django.dispatch.Signal(providing_args=["arg1", "arg2"])

# 内置的信号是可以自动触发的
# 自定义的信号不能自动触发

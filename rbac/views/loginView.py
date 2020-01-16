from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render
from django.views.generic import TemplateView


# 用户登录视图类
from django.views.generic.base import View

from rbac.models import User
from rbac.service import init_permission


class Login(TemplateView):
    template_name = "login.html"

    def post(self, request):
        data = request.POST
        # 获取用户登录信息
        username = data.get("username")
        password = data.get("password")
        error = ''
        user = User.get_by_user(username)
        if not user or user.status==User.STATUS_DELETE:
            error = '用户名不正确'
        else:
            if check_password(password,user.password):
                request.session["user"] = username  # 将用户名存入session中
                init_permission.init_permission(request, user)  # 调用权限注入函数，注入用户权限
                request.session.set_expiry(0);  #退出浏览器清除session
                return redirect('index.html')
            else:
                error = '密码不正确'
        contex = {'error':error, 'username':username}
        return render(request, 'login.html', context=contex)


class Logout(View):
    def get(self, request):
        # 1. 将session中的用户名、昵称删除
        request.session.flush()
        # 2. 重定向到 登录界面
        return redirect('/login.html')


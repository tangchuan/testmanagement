import re

from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from rbac.models import User


# 获取菜单及头部数据公共类
class CommonViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.session.get('user')
        user = User.get_by_user(username)
        context.update({
            'menus_dict': self.request.session.get("menus_dict"),
            'user':user,
        })
        return context


#首页
class Index(CommonViewMixin, TemplateView):
    template_name = "index.html"


#修改用户信息
class UserInfo(CommonViewMixin, TemplateView):
    template_name = "userinfo.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        context = super().get_context_data()
        user = context["user"]
        if not user:
            return redirect('login')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context["user"]
        if user:
            username = user.username
            email = user.email
            realname = user.realname
            phone = user.phone
            context.update({
                'username': username,
                'email': email,
                'realname': realname,
                'phone': phone
            })

        return context

    def post(self,request):
        errors = []
        success = ''
        context = self.get_context_data()
        user = context["user"]
        if user:
            username = user.username
            email = request.POST.get('email')
            if len(email)==0:
                errors.append('您未输入邮箱地址！')
            elif len(email)>32:
                errors.append('您输入的邮箱长度已超过32个字符了！')
            elif not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
                errors.append('您输入的邮箱格式有误')
            realname = request.POST.get('realname')
            if len(realname)==0:
                errors.append('您未输入姓名！')
            elif len(realname)>150:
                errors.append('您输入的姓名长度已超过150个字符！')
            phone = request.POST.get('phone')
            if len(user.phone)>11:
                errors.append('您输入的电话已超过11个字符！')
            context.update({
                'email': email,
                'realname':realname,
                'phone':phone
            })
            if not errors:
                User.objects.filter(username=username).update(
                    email=email,
                    realname=realname,
                    phone=phone,
                )
                success='用户信息修改成功！'
            context.update({
                'errors': errors,
                'success':success
            })
            return render(request, "userinfo.html", context=context)
        else:
            return redirect('login')


#密码修改
class PasswordChange(CommonViewMixin, TemplateView):
    template_name = 'pswdcg.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        context = super().get_context_data()
        user = context["user"]
        if not user:
            return redirect('login')
        return response

    def post(self,request):
        errors = []
        success = ''
        context = super().get_context_data()
        user = context["user"]
        if user:
            oldpassword = request.POST.get('oldpassword')
            newpassword = request.POST.get('newpassword')
            confirmpassword = request.POST.get('confirmpassword')
            print(oldpassword,newpassword,confirmpassword)
            if not check_password(oldpassword, user.password):
                errors.append('您输入的密码错误！')
            else:
                if newpassword != confirmpassword:
                    errors.append('您输入的两次新密码不一致！')
                elif len(newpassword)>64 or len(newpassword)<6:
                    errors.append('您输入的密码需6—64个字符')
            if not errors:
                user.password = make_password(newpassword)
                user.save()
                success = '您的密码已修改成功！'
            context.update({
                'errors': errors,
                'success':success,
            })
            return render(request, "pswdcg.html", context=context)
        else:
            return redirect('login')
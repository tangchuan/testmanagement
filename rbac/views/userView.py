import json
import re

from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, DetailView

from rbac.models import User, Role
from rbac.views.indexView import CommonViewMixin


class Users(CommonViewMixin, ListView):
    queryset = User.user_list()
    paginate_by = 10
    context_object_name = 'user_list'
    template_name = 'user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roles=User.get_by_role()
        context.update({
            "roles": roles,
        })
        return context

    def get_queryset(self):
        queryset = self.queryset
        role=self.request.POST.get("role")
        username=self.request.POST.get("username")
        realname=self.request.POST.get("realname")
        phone= self.request.POST.get("phone")
        startTime=self.request.POST.get("startTime")
        endTime= self.request.POST.get("endTime")
        if role and role.isdigit():
            queryset = queryset.filter(Q(role=role))
        if username:
            queryset = queryset.filter(Q(username__icontains=username))
        if realname:
            queryset = queryset.filter(Q(realname__icontains=realname))
        if phone:
            queryset = queryset.filter(Q(phone__icontains=phone))
        if startTime:
            queryset = queryset.filter(Q(created_time__gte=startTime))
        if endTime:
            queryset = queryset.filter(Q(created_time__lte=endTime))
        return queryset

    def post(self,request, *args, **kwargs):
        return super(Users, self).get(request, *args, **kwargs)


#新增用户
class AddUser(CommonViewMixin,TemplateView):
    template_name = 'adduser.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "roles":Role.role_list()
        })
        return context

    def post(self, request, *args, **kwargs):
        errors = []
        context = self.get_context_data()
        user = context["user"]
        if user:
            username = request.POST.get('username')
            email = request.POST.get('email')
            realname = request.POST.get('realname')
            phone = request.POST.get('phone')
            roles = request.POST.getlist('role')
            if len(username)>32 or len(username)<1:
                errors.append('您输入的用户账号需在1-32个字符之间')
            elif User.user_list().filter(username=username):
                errors.append('您输入的用户账号已存在')
            if len(email)>32 or len(email)<1:
                errors.append('您输入的邮箱内容需在1-32个字符之间')
            elif not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
                errors.append('您输入的邮箱格式有误')
            if len(realname)>150 or len(realname)<1:
                errors.append('您输入的姓名需在1-150个字符之间')
            if len(phone)>11:
                errors.append('您输入的电话已超过11个字符！')
            elif phone and not phone.isdigit():
                errors.append('您输入的电话不是纯数字！')
            elif User.user_list().filter(phone=phone):
                errors.append('您输入的电话已被其他账户使用！')
            if errors:
                context.update({
                    'errors': errors,
                })
                return render(request, "adduser.html", context=context)
            else:
                password = make_password('123456')
                new_user=User.objects.create(
                    username=username,
                    password=password,
                    email=email,
                    realname=realname,
                    phone=phone
                )
                if(roles):
                    roles_list = Role.role_list().filter(id__in=roles)
                    for role in roles_list:
                        new_user.role.add(role)
                return redirect('user')
        else:
            return redirect('login')


#修改用户
class ChangeUser(CommonViewMixin,DetailView):
    queryset = User.user_list()
    template_name = 'adduser.html'
    context_object_name = 'user_detail'
    pk_url_kwarg = 'user_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role_own = context['user_detail'].role.all()
        context.update({
            "roles":Role.role_list(),
            "role_own":role_own,
        })
        return context

    def post(self, request, *args, **kwargs):
        errors = []
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        user = context["user"]
        if user:
            email = request.POST.get('email')
            realname = request.POST.get('realname')
            phone = request.POST.get('phone')
            roles = request.POST.getlist('role')
            roles_list = Role.role_list().filter(id__in=roles)
            user_id = self.kwargs.get('user_id')
            chang_user = self.queryset.filter(id=user_id)
            if len(email)>32 or len(email)<1:
                errors.append('您输入的邮箱内容需在1-32个字符之间')
            elif not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
                errors.append('您输入的邮箱格式有误')
            if len(realname)>150 or len(realname)<1:
                errors.append('您输入的姓名需在1-150个字符之间')
            if len(phone)>11:
                errors.append('您输入的电话已超过11个字符！')
            elif phone and not phone.isdigit():
                errors.append('您输入的电话不是纯数字！')
            elif User.user_list().filter(phone=phone) and phone!=chang_user.first().phone:
                errors.append('您输入的电话已被其他账户使用！')
            if errors:
                context['user_detail'].email = email
                context['user_detail'].realname = realname
                context['user_detail'].phone = phone
                context["role_own"]= roles_list
                context.update({
                    'errors': errors,
                })
                return render(request, "adduser.html", context=context)
            else:
                chang_user.update(email=email,realname=realname,phone=phone)
                chang_user.first().role.clear()
                if(roles):
                    for role in roles_list:
                        chang_user.first().role.add(role)
                return redirect('user')
        else:
            return redirect('login')


#删除用户
class DeleteUser(CommonViewMixin,TemplateView):

    def post(self, request, *args, **kwargs):
        success = 0
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        user_id =self.kwargs.get('user_id')
        context = self.get_context_data()
        user = context["user"]
        if user:
            User.user_list().filter(id = user_id).update(
                status = User.STATUS_DELETE
            )
            delete_user = User.get_user_by_id(user_id)
            if delete_user and delete_user.status == User.STATUS_DELETE:
                success = 1
        else:
            success = -1
        response.write(json.dumps({'success': success}))
        return response


#重置密码
class ResetUser(CommonViewMixin,TemplateView):

    def post(self, request, *args, **kwargs):
        success = 0
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        user_id =self.kwargs.get('user_id')
        context = self.get_context_data()
        user = context["user"]
        if user:
            reset_password='123456'
            password = make_password(reset_password)
            print(password)
            User.user_list().filter(id = user_id).update(
                password = password
            )
            reset_user = User.get_user_by_id(user_id)
            if reset_user and check_password(reset_password,reset_user.password):
                success = 1
        else:
            success = -1
        response.write(json.dumps({'success': success}))
        return response


#查看用户
class ReadUser(CommonViewMixin,DetailView):
    queryset = User.user_list()
    template_name = 'readuser.html'
    context_object_name = 'user_detail'
    pk_url_kwarg = 'user_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role_own = context['user_detail'].role.all()
        context.update({
            "roles":Role.role_list(),
            "role_own":role_own,
        })
        return context
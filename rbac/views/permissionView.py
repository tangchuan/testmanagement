import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, DetailView

from rbac.models import Permission, Menu, Role
from rbac.views.indexView import CommonViewMixin


class Permissions(CommonViewMixin, ListView):
    queryset = Permission.permission_list()
    paginate_by = 10
    context_object_name = 'permission_list'
    template_name = 'permission.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "menus":Permission.get_by_menus(),
        })
        return context

    def get_queryset(self):
        queryset = self.queryset
        menu=self.request.POST.get("menu")
        permission_name=self.request.POST.get("permission_name")
        parent_permission=self.request.POST.get("parent_permission")
        url= self.request.POST.get("url")
        startTime=self.request.POST.get("startTime")
        endTime= self.request.POST.get("endTime")
        # print(menu,permission_name,parent_permission,url,startTime,endTime)
        if menu and menu.isdigit():
            queryset = queryset.filter(Q(menu=menu))
        if permission_name:
            queryset = queryset.filter(Q(name__icontains=permission_name))
        if parent_permission:
            queryset = queryset.filter(Q(parent__name__icontains=parent_permission))
        if url:
            queryset = queryset.filter(Q(url__icontains=url))
        if startTime:
            queryset = queryset.filter(Q(created_time__gte=startTime))
        if endTime:
            queryset = queryset.filter(Q(created_time__lte=endTime))
        return queryset

    def post(self,request, *args, **kwargs):
        return super(Permissions, self).get(request, *args, **kwargs)


#新增权限
class AddPermission(CommonViewMixin,TemplateView):
    # http_method_names = ['post']
    template_name = 'addpermission.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        permissions = Permission.permission_list().filter(Q(parent=None))
        context.update({
            "permissions":permissions,
            "menus":Menu.menu_list(),
        })
        return context

    def post(self, request, *args, **kwargs):
        errors = []
        context = self.get_context_data()
        user = context["user"]
        if user:
            name = request.POST.get('name')
            type = request.POST.get('type')
            url = request.POST.get('url')
            parent_id = request.POST.get('parent')
            menu_id = request.POST.get('menu')
            menu=None
            parent = None
            if len(name)>6 or len(name)<1:
                errors.append('您输入的权限名需在1-6个字符之间')
            if len(url)>300 or len(url)<2:
                errors.append('您输入的菜单图标内容需在2-300个字符之间')
            if not type:
                errors.append('您的权限类型为空')
            elif type=='1':
                if not menu_id:
                    errors.append(('菜单不能为空'))
                else:
                    menu = Menu.get_by_menu(menu_id)
                    if not menu:
                        errors.append(('您输入的菜单不存在'))
            elif type=='2':
                if not parent_id:
                    errors.append('按钮权限，父级权限不能为空')
                else:
                    parent = Permission.get_permission_by_id(parent_id)
                    if not parent:
                        errors.append('您输入的父级权限不存在')
            if errors:
                context.update({
                    'errors': errors,
                })
                return render(request, "addpermission.html", context=context)
            else:
                Permission.objects.create(name=name,url=url,parent=parent,menu=menu)
                return redirect('permission')
        else:
            return redirect('login')


#修改权限
class ChangePermission(CommonViewMixin,DetailView):
    queryset = Permission.permission_list()
    template_name = 'addpermission.html'
    context_object_name = 'permission_detail'
    pk_url_kwarg = 'permission_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        permissions = Permission.permission_list().filter(Q(parent = None))
        context.update({
            "permissions":permissions,
            "menus":Menu.menu_list(),
        })
        return context

    def post(self, request, *args, **kwargs):
        errors = []
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        user = context["user"]
        permission_id =self.kwargs.get('permission_id')
        name = request.POST.get('name')
        type = request.POST.get('type')
        url = request.POST.get('url')
        menu_id = request.POST.get('menu')
        parent_id = request.POST.get('parent')
        parent = None
        menu = None
        if user:
            if len(name)>5 or len(name)<1:
                errors.append('您输入的权限名需在1-6个字符之间')
            if len(url)>300 or len(url)<2:
                errors.append('您输入的菜单图标内容需在2-300个字符之间')
            if not type:
                errors.append('您的权限类型为空')
            elif type=='1':
                if not menu_id:
                    errors.append(('菜单不能为空'))
                else:
                    menu = Menu.get_by_menu(menu_id)
                    if not menu:
                        errors.append(('您输入的菜单不存在'))
            elif type=='2':
                if not parent_id:
                    errors.append('按钮权限，父级权限不能为空')
                else:
                    parent = Permission.get_permission_by_id(parent_id)
                    if not parent:
                        errors.append('您输入的父级权限不存在')
            if errors:
                permission_detail = {
                    'name':name,
                    'url':url,
                    'menu':menu,
                    'parent':parent,
                }
                context.update({
                    'permission_detail':permission_detail,
                    'errors': errors,
                })
                return render(request, "addpermission.html", context=context)
            else:
                Permission.objects.filter(status=Permission.STATUS_NORMAL, id=permission_id).update(
                    name=name,
                    url=url,
                    menu=menu,
                    parent=parent
                )
                return redirect('permission')
        else:
            return redirect('login')


#删除权限
class DeletePermission(CommonViewMixin,TemplateView):

    def post(self, request, *args, **kwargs):
        success = False
        permission_id =self.kwargs.get('permission_id')
        context = self.get_context_data()
        user = context["user"]
        if user:
            role = Role.role_list().filter(permission=permission_id)
            parent = Permission.permission_list().filter(parent=permission_id)
            if not role and not parent:
                Permission.permission_list().filter(id=permission_id).update(
                    status = Permission.STATUS_DELETE
                )
                permission = Permission.get_permission_by_id(permission_id)
                if permission and permission.status == Permission.STATUS_DELETE:
                    success = True
            response = HttpResponse()
            response['Content-Type'] = "text/javascript"
            response.write(json.dumps({'success':success}))
            return response
        else:
            return redirect('login')
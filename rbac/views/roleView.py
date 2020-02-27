import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, DetailView

from rbac.models import Role, Menu, Permission, User
from rbac.views.indexView import CommonViewMixin


class Roles(CommonViewMixin, ListView):
    queryset = Role.role_list()
    paginate_by = 10
    context_object_name = 'role_list'
    template_name = 'role/role.html'

    def get_queryset(self):
        queryset = self.queryset
        keyword = self.request.POST.get('keyword')
        if not keyword:
            return queryset
        return queryset.filter(Q(title__icontains=keyword))

    def post(self,request, *args, **kwargs):
        return super(Roles, self).get(request, *args, **kwargs)


#新增角色
class AddRole(CommonViewMixin,TemplateView):
    # http_method_names = ['post']
    template_name = 'role/addrole.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buttons={}
        button_permission=Permission.permission_list().filter(~Q(parent=None))
        for permission in button_permission:
            if permission.parent.id in buttons:
                buttons[permission.parent.id]['children'].append({
                    'permission_id': permission.id,
                    'permission_name': permission.name,
                })
            else:
                buttons[permission.parent.id]={
                    'children':[{
                        'permission_id':permission.id,
                        'permission_name':permission.name,
                    }]
                }
        permissions =Permission.permission_list().filter(Q(parent=None))
        permission_tree = {}
        for permission in permissions:
            if permission.id in buttons:
                permission_data={
                    'permission_id':permission.id,
                    'permission_name':permission.name,
                    'children':buttons[permission.id]['children']
                }
            else:
                permission_data={
                    'permission_id':permission.id,
                    'permission_name':permission.name,
                }
            if permission.menu.id in permission_tree:
                permission_tree[permission.menu.id]['children'].append(permission_data)
            else:
                permission_tree[permission.menu.id]={
                    'children':[permission_data]
                }
        tree = {}
        menus = Menu.menu_list()
        for menu in menus:
            if menu.id in permission_tree:
                tree[menu.id]={
                    'menu_id':menu.id,
                    'menu_title':menu.title,
                    'children':permission_tree[menu.id]['children'],
                }
        context.update({
            'tree':tree,
        })
        return context

    def post(self, request, *args, **kwargs):
        errors = []
        status = 0
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        context = self.get_context_data()
        user = context["user"]
        if user:
            name = request.POST.get('name')
            if len(name)>6 or len(name)<1:
                errors.append('您输入的权限名需在1-6个字符之间')
            elif Role.role_list().filter(title=name):
                errors.append("您输入的角色已存在")
            if errors:
                context.update({
                    'errors': errors,
                })
            else:
                role = Role.objects.create(title=name)
                permissions = request.POST.get('permissions')
                if(permissions):
                    permission_list=permissions.split(",")
                    permission_list = list(map(int, permission_list))
                    per = Permission.objects.filter(id__in=permission_list)
                    for obj in per:
                        role.permission.add(obj)
                status=1
        else:
            status = -1
        response.write(json.dumps({
            'errors': errors,
            'status':status,
        }))
        return response


#修改角色
class ChangeRole(CommonViewMixin,DetailView):
    queryset = Role.role_list()
    template_name = 'role/addrole.html'
    context_object_name = 'role_detail'
    pk_url_kwarg = 'role_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pmn_own = context['role_detail'].permission.all()
        buttons = {}
        button_permission = Permission.permission_list().filter(~Q(parent=None))
        for permission in button_permission:
            checkable = False
            if permission in pmn_own:
                checkable = True
            if permission.parent.id in buttons:
                buttons[permission.parent.id]['children'].append({
                    'permission_id': permission.id,
                    'permission_name': permission.name,
                    'checkable':checkable,
                })
            else:
                buttons[permission.parent.id] = {
                    'children': [{
                        'permission_id': permission.id,
                        'permission_name': permission.name,
                        'checkable':checkable,
                    }]
                }
        permissions = Permission.permission_list().filter(Q(parent=None))
        permission_tree = {}
        for permission in permissions:
            checkable = False
            if permission in pmn_own:
                checkable = True
            if permission.id in buttons:
                permission_data = {
                    'permission_id': permission.id,
                    'permission_name': permission.name,
                    'checkable' : checkable,
                    'children': buttons[permission.id]['children']
                }
            else:
                permission_data = {
                    'permission_id': permission.id,
                    'permission_name': permission.name,
                    'checkable': checkable,
                }
            if permission.menu.id in permission_tree:
                permission_tree[permission.menu.id]['children'].append(permission_data)
            else:
                permission_tree[permission.menu.id] = {
                    'children': [permission_data]
                }
        tree = {}
        menus = Menu.menu_list()
        menu_id=pmn_own.values('menu__id').order_by('menu__id').distinct()
        menu_check = Menu.menu_list().filter(id__in=menu_id)
        for menu in menus:
            checkable = False
            if menu in menu_check:
                checkable=True
            if menu.id in permission_tree:
                tree[menu.id] = {
                    'menu_id': menu.id,
                    'menu_title': menu.title,
                    'checkable':checkable,
                    'children': permission_tree[menu.id]['children'],
                }
        context.update({
            'tree': tree,
        })
        return context

    def post(self, request, *args, **kwargs):
        errors = []
        status = 0
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        user = context["user"]
        role_id = self.kwargs.get('role_id')
        role = self.queryset.filter(id=role_id)
        if user:
            name = request.POST.get('name')
            if len(name) > 6 or len(name) < 1:
                errors.append('您输入的权限名需在1-6个字符之间')
            elif Role.role_list().filter(title=name) and name!=role.first().title:
                errors.append("您输入的角色已存在")
            if errors:
                context.update({
                    'errors': errors,
                })
            else:
                role.update(title=name)
                permissions = request.POST.get('permissions')
                role.first().permission.clear()
                if (permissions):
                    permission_list = permissions.split(",")
                    permission_list = list(map(int, permission_list))
                    per = Permission.objects.filter(id__in=permission_list)
                    for obj in per:
                        role.first().permission.add(obj)
                status = 1
        else:
            status = -1
        response.write(json.dumps({
            'errors': errors,
            'status': status,
        }))
        return response


#删除角色
class DeleteRole(CommonViewMixin,TemplateView):

    def post(self, request, *args, **kwargs):
        success = 0
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        role_id =self.kwargs.get('role_id')
        context = self.get_context_data()
        user = context["user"]
        if user:
            user_own = User.user_list().filter(role=role_id)
            if not user_own:
                Role.role_list().filter(id=role_id).update(
                    status = Role.STATUS_DELETE
                )
                role = Role.get_role_by_id(role_id)
                if role and role.status == Role.STATUS_DELETE:
                    success = 1
        else:
            success=-1
        response.write(json.dumps({'success': success}))
        return response


#查看角色
class ReadRole(CommonViewMixin,DetailView):
    queryset = Role.role_list()
    template_name = 'role/readrole.html'
    context_object_name = 'role_detail'
    pk_url_kwarg = 'role_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pmn_own = context['role_detail'].permission.all()
        buttons = {}
        button_permission = Permission.permission_list().filter(~Q(parent=None))
        for permission in button_permission:
            checkable = False
            if permission in pmn_own:
                checkable = True
            if permission.parent.id in buttons:
                buttons[permission.parent.id]['children'].append({
                    'permission_id': permission.id,
                    'permission_name': permission.name,
                    'checkable':checkable,
                })
            else:
                buttons[permission.parent.id] = {
                    'children': [{
                        'permission_id': permission.id,
                        'permission_name': permission.name,
                        'checkable':checkable,
                    }]
                }
        permissions = Permission.permission_list().filter(Q(parent=None))
        permission_tree = {}
        for permission in permissions:
            checkable = False
            if permission in pmn_own:
                checkable = True
            if permission.id in buttons:
                permission_data = {
                    'permission_id': permission.id,
                    'permission_name': permission.name,
                    'checkable' : checkable,
                    'children': buttons[permission.id]['children']
                }
            else:
                permission_data = {
                    'permission_id': permission.id,
                    'permission_name': permission.name,
                    'checkable': checkable,
                }
            if permission.menu.id in permission_tree:
                permission_tree[permission.menu.id]['children'].append(permission_data)
            else:
                permission_tree[permission.menu.id] = {
                    'children': [permission_data]
                }
        tree = {}
        menus = Menu.menu_list()
        menu_id=pmn_own.values('menu__id').order_by('menu__id').distinct()
        menu_check = Menu.menu_list().filter(id__in=menu_id)
        for menu in menus:
            checkable = False
            if menu in menu_check:
                checkable=True
            if menu.id in permission_tree:
                tree[menu.id] = {
                    'menu_id': menu.id,
                    'menu_title': menu.title,
                    'checkable':checkable,
                    'children': permission_tree[menu.id]['children'],
                }
        context.update({
            'tree': tree,
        })
        return context
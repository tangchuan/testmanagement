import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, DetailView

from rbac.models import Menu, Permission
from rbac.views.indexView import CommonViewMixin


#菜单列表
class Menus(CommonViewMixin, ListView):
    queryset = Menu.menu_list()
    paginate_by = 10
    context_object_name = 'menu_list'
    template_name = 'menu/menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "keyword":self.request.POST.get("keyword")
        })
        return context

    def get_queryset(self):
        queryset = self.queryset
        keyword = self.request.POST.get('keyword')
        if not keyword:
            return queryset
        return queryset.filter(Q(title__icontains=keyword))

    def post(self,request, *args, **kwargs):
        return super(Menus, self).get(request, *args, **kwargs)


#新增菜单
class AddMenu(CommonViewMixin,TemplateView):
    # http_method_names = ['post']
    template_name = 'menu/addmenu.html'

    def post(self, request, *args, **kwargs):
        errors = []
        success = ''
        context = self.get_context_data()
        user = context["user"]
        if user:
            title = request.POST.get('title')
            icon = request.POST.get('icon')
            priority = request.POST.get('priority')
            if len(title)>6 or len(title)<1:
                errors.append('您输入的菜单名需在1-6个字符之间')
            if len(icon)>20 or len(icon)<2:
                errors.append('您输入的菜单图标内容需在2-20个字符之间')
            if not priority.isdigit():
                errors.append('优先级请输入数字')
            elif len(priority)>6 or len(priority)<1:
                errors.append('您输入的优先级内容需在1-6个字符之间')
            if errors:
                context.update({
                    'errors': errors,
                })
                return render(request, "menu/addmenu.html", context=context)
            else:
                Menu.objects.create(title=title,icon=icon,priority=priority)
                return redirect('menu')
        else:
            return redirect('login')


#修改菜单
class ChangeMenu(CommonViewMixin,DetailView):
    # http_method_names = ['post']
    queryset = Menu.menu_list()
    template_name = 'menu/addmenu.html'
    context_object_name = 'menu'
    pk_url_kwarg = 'menu_id'

    def post(self, request, *args, **kwargs):
        errors = []
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        user = context["user"]
        menu_id =self.kwargs.get('menu_id')
        title = request.POST.get('title')
        icon = request.POST.get('icon')
        priority = request.POST.get('priority')
        if user:
            if len(title) > 6 or len(title) < 1:
                errors.append('您输入的菜单名需在1-6个字符之间')
            if len(icon) > 20 or len(icon) < 2:
                errors.append('您输入的菜单图标内容需在2-20个字符之间')
            if not priority.isdigit():
                errors.append('优先级请输入数字')
            elif len(priority) > 6 or len(priority) < 1:
                errors.append('您输入的优先级内容需在1-6个字符之间')
            if errors:
                menu = {
                    'title':title,
                    'icon':icon,
                    'priority':priority,
                }
                context.update({
                    'menu':menu,
                    'errors': errors,
                })
                return render(request, "menu/addmenu.html", context=context)
            else:
                Menu.objects.filter(status=Menu.STATUS_NORMAL, id=menu_id).update(
                    title=title,
                    icon=icon,
                    priority=priority,
                )
                return redirect('menu')
        else:
            return redirect('login')


#删除菜单
class DeleteMenu(CommonViewMixin,TemplateView):

    def post(self, request, *args, **kwargs):
        success = False
        menu_id =self.kwargs.get('menu_id')
        context = self.get_context_data()
        user = context["user"]
        if user:
            permission = Permission.permission_list().filter(menu=menu_id)
            if not permission:
                Menu.objects.filter(id=menu_id).update(
                    status = Menu.STATUS_DELETE
                )
                menu = Menu.get_by_menu(menu_id)
                if menu and menu.status == Menu.STATUS_DELETE:
                    success = True
            response = HttpResponse()
            response['Content-Type'] = "text/javascript"
            response.write(json.dumps({'success':success}))
            return response
        else:
            return redirect('login')
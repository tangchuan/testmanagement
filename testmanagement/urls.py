"""testmanagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include

from rbac.views.indexView import Index, UserInfo, PasswordChange
from rbac.views.loginView import Login, Logout
from rbac.views.menuView import Menus, AddMenu, ChangeMenu, DeleteMenu
from rbac.views.permissionView import Permissions, AddPermission, ChangePermission, DeletePermission
from rbac.views.roleView import Roles, AddRole, ChangeRole, DeleteRole, ReadRole
from rbac.views.userView import Users, AddUser, ChangeUser, DeleteUser, ResetUser, ReadUser

urlpatterns = [
    url(r'^$', Index.as_view(), name='index'),
    url(r'^index.html$', Index.as_view(), name='index'),
    url(r'^login.html$', Login.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
    url(r'^userinfo.html$', UserInfo.as_view(), name='userinfo'),
    url(r'^passwordchange.html$', PasswordChange.as_view(), name='passwordchange'),
    url(r'^menu/$', Menus.as_view(), name='menu'),
    url(r'^menu/addmenu.html$', AddMenu.as_view(), name='addmenu'),
    url(r'^menu/change/(?P<menu_id>\d+).html$', ChangeMenu.as_view(), name='changemenu'),
    url(r'^menu/delete/(?P<menu_id>\d+).html$', DeleteMenu.as_view(), name='deletemenu'),
    url(r'^permission/$', Permissions.as_view(), name='permission'),
    url(r'^permission/addpermission.html$', AddPermission.as_view(), name='addpermission'),
    url(r'^permission/change/(?P<permission_id>\d+).html$', ChangePermission.as_view(), name='changepermission'),
    url(r'^permission/delete/(?P<permission_id>\d+).html$', DeletePermission.as_view(), name='deletepermission'),
    url(r'^role/$', Roles.as_view(), name='role'),
    url(r'^role/addrole.html$', AddRole.as_view(), name='addrole'),
    url(r'^role/change/(?P<role_id>\d+).html$', ChangeRole.as_view(), name='changerole'),
    url(r'^role/delete/(?P<role_id>\d+).html$', DeleteRole.as_view(), name='deleterole'),
    url(r'^role/read/(?P<role_id>\d+).html$', ReadRole.as_view(), name='readrole'),
    url(r'^user/$', Users.as_view(), name='user'),
    url(r'^user/adduser.html$', AddUser.as_view(), name='adduser'),
    url(r'^user/change/(?P<user_id>\d+).html$', ChangeUser.as_view(), name='changeuser'),
    url(r'^user/delete/(?P<user_id>\d+).html$', DeleteUser.as_view(), name='deleteuser'),
    url(r'^user/reset/(?P<user_id>\d+).html$', ResetUser.as_view(), name='resetuser'),
    url(r'^user/read/(?P<user_id>\d+).html$', ReadUser.as_view(), name='readuser'),
    url(r'admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
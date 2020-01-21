from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(models.Model):
    """
    用户表
    """
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )
    username = models.CharField(verbose_name='用户名',max_length=32, unique=True)
    password = models.CharField(verbose_name='密码',max_length=128)
    email = models.CharField(verbose_name='邮箱',max_length=32)
    realname = models.CharField(verbose_name='姓名', max_length=150,default='name')
    phone = models.CharField(max_length=11, null=True, unique=True)
    role = models.ManyToManyField("Role")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='状态')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name_plural = "用户表"

    def __str__(self):
        return self.username

    @staticmethod
    def get_by_user(username):
        try:
            user = User.objects.get(username=username)  # 用户名验证
        except User.DoesNotExist:
            user = None
        return user

    @classmethod
    def user_list(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-created_time')

    @classmethod
    def get_by_role(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL).values('role', 'role__title').order_by('role__title').distinct()

    @staticmethod
    def get_user_by_id(id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            user = None
        return user


# 角色表
class Role(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )
    title = models.CharField(max_length=32, verbose_name="角色")
    permission = models.ManyToManyField("Permission", verbose_name="权限")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='状态')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name_plural = "角色表"

    def __str__(self):
        return self.title

    @classmethod
    def role_list(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-created_time')

    @staticmethod
    def get_role_by_id(id):
        try:
            role = Role.objects.get(id=id)
        except Role.DoesNotExist:
            role = None
        return role


# 权限表
class Permission(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )
    name = models.CharField(max_length=32, verbose_name='权限名')
    url = models.CharField(
        max_length=300,
        verbose_name='权限url地址',
        null=True,
        blank=True,
        help_text='是否给菜单设置一个url地址'
    )
    # 指定属于哪个父级权限
    parent = models.ForeignKey(
        'self',
        verbose_name='父级权限',
        null=True,
        blank=True,
        help_text='如果添加的是子权限，请选择父权限',
        on_delete=models.CASCADE
    )

    # 指定属于哪个menu
    menu = models.ForeignKey(to="Menu",verbose_name='对应菜单',blank=True,null=True, on_delete=models.CASCADE)
    status = models.PositiveIntegerField(default=STATUS_NORMAL,choices=STATUS_ITEMS,verbose_name='状态')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "权限表"
        verbose_name_plural = "权限表"
        ordering = ["id"]

    @classmethod
    def permission_list(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-created_time')

    @classmethod
    def get_by_menus(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL,parent=None).values('menu','menu__title').order_by('menu__title').distinct()

    @staticmethod
    def get_permission_by_id(id):
        try:
            permission = Permission.objects.get(id=id)
        except Permission.DoesNotExist:
            permission = None
        return permission

#菜单表
class Menu(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS =(
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )
    title = models.CharField(max_length=32, verbose_name='菜单名')
    icon = models.CharField(max_length=32,verbose_name='菜单图标',default='fa-th-large')

    priority = models.IntegerField(
        verbose_name='显示优先级',
        null=True,
        blank=True,
        help_text='菜单的显示顺序，优先级越小显示越靠前'
    )
    status = models.PositiveIntegerField(default=STATUS_NORMAL,choices=STATUS_ITEMS,verbose_name='状态')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = "菜单表"
        verbose_name_plural = "菜单表"
        ordering = ["priority","id"]  # 根据优先级和id来排序

    @classmethod
    def menu_list(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-created_time')

    @staticmethod
    def get_by_menu(id):
        try:
            menu = Menu.objects.get(id=id)
        except Menu.DoesNotExist:
            menu = None

        return menu
from rbac import models


def init_permission(request, user):
    """
    在登录函数验证通过后，在session中注入用户权限和用户菜单权限。
    :param request: 用户登录请求时的wsgi请求对象
    :param user: 用户登录验证通过后的用户账号名
    :return: none，
    """
    permissions = models.Permission.objects.filter(role__user__username=user).values(
        "pk", "name", "url","parent_id",
        "menu__pk","menu__title", "menu__icon", "menu__priority"
    ).order_by("menu__priority").distinct()

    permissions_list = []  # 定义权限列表
    menus_dict = {}  # 定义菜单列表

    for permission in permissions:  # 遍历权限列表
        # 获取用户权限的数据结构，列表套字典，一个字典代表一个权限
        permissions_list.append({
            "pk": permission["pk"],
            "name": permission["name"],
            "url": permission["url"],
            "parent_id": permission["parent_id"],
        })

        # 获取菜单权限的数据结构，字典套字典，一个字典代表一个菜单
        if permission["menu__pk"]:
            if permission["menu__pk"] in menus_dict:
                menus_dict[permission["menu__pk"]]["children"].append({
                    "pk": permission["pk"],
                    "name": permission["name"],
                    "url": permission["url"],
                    "parent_id": permission["parent_id"],
                })
            else:
                menus_dict[permission["menu__pk"]] = {
                    "pk": permission["menu__pk"],
                    "title": permission["menu__title"],
                    "icon": permission["menu__icon"],
                    "priority": permission["menu__priority"],
                    "children": [{
                        "pk": permission["pk"],
                        "name": permission["name"],
                        "url": permission["url"],
                        "parent_id": permission["parent_id"],
                    }]
                }

        # print("权限列表",permissions_list)
    print("菜单权限",menus_dict)

    # session中注入权限数据
    request.session["permissions_list"] = permissions_list

    # session中注入菜单数据
    request.session["menus_dict"] = menus_dict


# _*_ encoding:utf-8 _*_

import xadmin
from .models import CityDice, Teacher, CourseOrg


class CityDictAdmin(object):
    list_display = ['name', 'desc','add_time']
    search_fields = ['name', 'desc']
    list_filter = ['name', 'desc','add_time']


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_num', 'fav_nums', 'image', 'address', 'city', 'add_time']
    search_fields = ['name', 'desc', 'click_num', 'fav_nums', 'image', 'address', 'city']
    list_filter = ['name', 'desc', 'click_num', 'fav_nums', 'image', 'address', 'city', 'add_time']


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company', 'points', 'fav_nums', 'add_time']
    search_fields = ['org', 'name', 'work_years', 'work_company', 'points', 'fav_nums']
    list_filter = ['org', 'name', 'work_years', 'work_company', 'points', 'fav_nums', 'add_time']


xadmin.site.register(CityDice, CityDictAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(Teacher, TeacherAdmin)



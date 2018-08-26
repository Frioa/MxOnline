# _*_ encoding:utf-8 _*_

import xadmin

from .models import Course, Lesson, Video, CourseResource


class CoursAdmin(object):

    list_display = ['name', 'desc', 'detail','degree','learn_times', 'students', 'fav_nums', 'image', 'click_num']
    search_fields = ['name', 'desc', 'detail','degree', 'students', 'fav_nums', 'image', 'click_num']
    list_filter = ['name', 'desc', 'detail','degree','learn_times', 'students', 'fav_nums', 'image', 'click_num']


class LessonAdmin(object):

    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CoursResourcAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course', 'name', 'download', 'add_time']


xadmin.site.register(Course, CoursAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video,VideoAdmin)
xadmin.site.register(CourseResource,CoursResourcAdmin)
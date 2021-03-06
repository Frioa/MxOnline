# _*_ encoding:utf-8 _*_
import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from .forms import LoginFrom, UserInfoForm,RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse

from .models import UserProfile,EmailVerifyRecord,Banner
from utils.email_send import send_register_email
from utils.minxin_utils import LoginRequiredMinin
from operations.models import UserCourse,UserFavorite,UserMessage
from organization.models import CourseOrg
from courses.models import Course
# Create your views here.


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class AciveUserView(View):
    def get(self,request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request,"active_file.html")
        return render(request, "login.html")


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {'register_form':register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "用户已经存在"})

            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.password = make_password(pass_word)
            user_profile.is_active = False
            user_profile.save()
            send_register_email(user_name, "register")
            return render(request, "login.html", {"msg": "用户名或者密码错误！！"})

        else:
            return render(request, "register.html", {"register_form": register_form})


class LogoutView(View):
    # 用户登出
    def get(self,request):
        logout(request)
        from django.core.urlresolvers import reverse
        return HttpResponseRedirect(reverse("index"))


class LoginView(View):
    def get(self,request):
        login_form = LoginFrom(request.POST)
        return render(request, "login.html", {"login_form":login_form})

    def post(self,request):
        login_form = LoginFrom(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "login.html", {"msg": "用户名未激活！！"})
            else:
                return render(request, "login.html", {"msg": "用户名或者密码错误！！"})
        else:
            return render(request, "login.html", {"login_form":login_form})


class ForgetPwdView(View):
    def get(self,request):
        forget_form = ForgetForm()
        return render(request,"forgetpwd.html",{'forget_form' : forget_form})

    def post(self,request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email","")
            send_register_email(email, "forget")
            return render(request, "send_success.html")
        else:
            return render(request, "forgetpwd.html", {'forget_form': forget_form})


class ResetView(View):
    def get(self,request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email1 = EmailVerifyRecord()
                email1.code = record.code
                email1.email = record.email
                email1.send_type = record.send_type
                email1.send_time = record.send_time
                email1.email_active_code = True
                email1.save()
                email = record.email
                return render(request, "password_reset.html", {"email":email})
        else:
            return render(request,"active_file.html")
        return render(request, "login.html")


class ModifyPwdView(View):
    #修改用户密码
    def post(self,request):
        modify_form = ModifyPwdForm(request.POST)

        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email":email, "msg":"两次输入密码不相同"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()

            return render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email": email, "modify_form": modify_form})


class UserinfoView(LoginRequiredMinin, View):
    #用户个人信息
    def get(self, request):
        return render(request, 'usercenter-info.html',{})

    def post(self,request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
        else:
            pass

class UploadImageView(LoginRequiredMinin, View):
    # 用户修改头像
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            # image = image_form.cleaned_data['image']
            # request.user.image = image
            # request.user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(View):
    #个人中心用户密码
    def post(self,request):
        modify_form = ModifyPwdForm(request.POST)

        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")

            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}', content_type='application/json')

            user = request.user
            user.password = make_password(pwd2)
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')

        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMinin,View):
    # 发送邮箱验证码
    def get(self,request):
        email = request.GET.get('email','')

        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已经存在"}', content_type='application/json')
        send_register_email(email,"update_email")
        return HttpResponse('{"status":"success"}', content_type='application/json')


class UpdateEmail(LoginRequiredMinin,View):
    #修改个人邮箱
    def post(self,request):
        email = request.POST.get('email','')
        code = request.POST.get('code', '')

        existed_records = EmailVerifyRecord.objects.filter(email=email,code=code,send_type="update_email")
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码出错"}', content_type='application/json')


class MyCourseView(LoginRequiredMinin,View):
    #我的课程
    def get(self,request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html',{
            "user_courses":user_courses,
        })


class MyFavOrgView(LoginRequiredMinin,View):
    #我的课程
    def get(self,request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user,fav_type=2)
        for fav_orgs in fav_orgs:
            org_id = fav_orgs.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html',{
            "org_list":org_list,
        })


class MyFavTeacherView(LoginRequiredMinin,View):
    #我收藏的讲师
    def get(self,request):
        teracher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user,fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = CourseOrg.objects.get(id=teacher_id)
            teracher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html',{
            "teracher_list":teracher_list,
        })


class MyFavCourseView(LoginRequiredMinin,View):
    #我收藏的课程
    def get(self,request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user,fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            teacher = Course.objects.get(id=course_id)
            course_list.append(teacher)
        return render(request, 'usercenter-fav-course.html',{
            "course_list":course_list,
        })


class MymessageView(LoginRequiredMinin, View):
    """
    我的消息
    """
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)


        #用户进入个人消息后清空未读消息的记录
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        #对个人消息进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_messages, 5, request=request)

        messages = p.page(page)
        return render(request, 'usercenter-message.html', {
            "messages":messages
        })


class IndexView(View):
    def get(self, request):
        #print(1/0)
        all_banners = Banner.objects.all().order_by('index')
        course = Course.objects.filter(is_banner=False)[:6:]
        banner_courses = Course.objects.filter(is_banner=False)[:3:]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html',{
            'all_banners':all_banners,
            'courses':course,
            'banner_courses':banner_courses,
            'course_orgs':course_orgs
        })


def page_not_found(request):
    #全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    #全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response
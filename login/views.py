from django.shortcuts import render
from django.shortcuts import redirect
from . import models
# Create your views here.
import hashlib


def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


def index(request):
    pass
    return render(request, 'view/index.html')


def login(request):
    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        message = "所有字段都必须填写！"
        if username and password:  # 确保用户名和密码都不为空
            username = username.strip()
            # 用户名字符合法性验证
            # 密码长度验证
            # 更多的其它验证.....
            try:
                user = models.User.objects.get(name=username)
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
        return render(request, 'view/chat.html', {"message": message})
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        print("error1")
        return redirect("/index/")
    if request.method == "POST":
        username = request.POST.get('username', None)
        password1 = request.POST.get('password', None)
        print(password1)
        password2 = request.POST.get('password2', None)
        print(password2)
        email = request.POST.get('email', None)
        sex = request.POST.get('sex', None)
        career = request.POST.get('zhiye', None)
        age = request.POST.get('age', None)
        message = "请检查填写的内容！"
        if password1 != password2:  # 判断两次密码是否相同
            message = "两次输入的密码不同！"
            print("error3")
            return render(request, 'view/index.html')  # , locals())
        else:
            same_name_user = models.User.objects.filter(name=username)
            print("error4")
            if same_name_user:  # 用户名唯一
                message = '用户已经存在，请重新选择用户名！'
                print("error5")
                return render(request, 'view/index.html')#, locals())
            same_email_user = models.User.objects.filter(email=email)
            if same_email_user:  # 邮箱地址唯一
                print("error6")
                message = '该邮箱地址已被注册，请使用别的邮箱！'
                return render(request, 'view/index.html')#, locals())

            # 当一切都OK的情况下，创建新用户
            print("error1")
            new_user = models.User()
            new_user.name = username
            new_user.password = hash_code(password1)
            new_user.email = email
            new_user.sex = sex
            new_user.career = career
            new_user.age = age
            new_user.save()
            return redirect('/index')  # 自动跳转到登录页面
    return render(request, 'view/index.html')  # , locals())


def logout(request):
    pass
    return redirect("/index/")

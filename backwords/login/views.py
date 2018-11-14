from django.shortcuts import render
from django.shortcuts import redirect
from . import models
import datetime
from login import forms
import hashlib
from django.conf import settings

# Create your views here.
# render方法接收request作为第一个参数，
# 要渲染的页面为第二个参数，
# 以及需要传递给页面的数据字典作为第三个参数（可以为空），
# 表示根据请求的部分，以渲染的HTML页面为主体，
# 使用模板语言将数据字典填入，然后返回给用户的浏览器。


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user)
    return code


def send_email(email, code):

        from django.core.mail import EmailMultiAlternatives

        subject = "来自WilliamLee的注册确认邮件"

        text_content = '''感谢注册WilliamLee的个人网站，如果你看到这段信息
        说明你的邮箱有问题'''

        html_content = '''
        <p>感谢注册<a href="http://{}/confirm?code={}" target=blank>WilliamLee
        </a></p>
        <p>请点击链接完成确认！</p>
        '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

        msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


def hash_code(s, salt='xq'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


def index(request):
    pass
    return render(request, 'login/index.html')


# 使用表单类自带的is_valid()方法一步完成数据验证工作；
# 验证成功后可以从表单对象的cleaned_data数据字典中获取表单的具体值；
# 如果验证不通过，
# 则返回一个包含先前数据的表单给前端页面，方便用户修改。
# 也就是说，它会帮你保留先前填写的数据内容，而不是返回一个空表！
def login(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirmed:
                    message = "该用户还未通过邮件确认！"
                    return render(request, 'login/login.html', locals())
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确"
            except:
                message = "用户名不存在"
            return render(request, 'login/login.html',
                          locals())
    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容"
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:
                message = "两次输入的密码不同"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = "用户已存在，请重新选择用户名"
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())
                # 一切成功检查后

                new_user = models.User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)
                message = '请前往注册邮箱，进行邮件确认！'
                return redirect('/login')

    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/index/")
    request.session.flush()
    # 等价于
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect('/index/')


def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已过期！请重新注册'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认， 请使用账户登陆'
        return render(request, 'login/confirm.html', locals())
# class backends.base.SessionBase
#         # 这是所有会话对象的基类，包含标准的字典方法:
#         __getitem__(key)
#             Example: fav_color = request.session['fav_color']
#         __setitem__(key, value)
#             Example: request.session['fav_color'] = 'blue'
#         __delitem__(key)
#             Example: del request.session['fav_color']  # 如果不存在会抛出异常
#         __contains__(key)
#             Example: 'fav_color' in request.session
#         get(key, default=None)
#             Example: fav_color = request.session.get('fav_color', 'red')
#         pop(key, default=__not_given)
#             Example: fav_color = request.session.pop('fav_color', 'blue')
#         # 类似字典数据类型的内置方法
#         keys()
#         items()
#         setdefault()
#         clear()
#
#
#         # 它还有下面的方法：
#         flush()
#             # 删除当前的会话数据和会话cookie。经常用在用户退出后，删除会话。
#
#         set_test_cookie()
#             # 设置一个测试cookie，用于探测用户浏览器是否支持cookies。由于cookie的工作机制，你只有在下次用户请求的时候才可以测试。
#         test_cookie_worked()
#             # 返回True或者False，取决于用户的浏览器是否接受测试cookie。你必须在之前先调用set_test_cookie()方法。
#         delete_test_cookie()
#             # 删除测试cookie。
#         set_expiry(value)
#             # 设置cookie的有效期。可以传递不同类型的参数值：
#         • 如果值是一个整数，session将在对应的秒数后失效。例如request.session.set_expiry(300) 将在300秒后失效.
#         • 如果值是一个datetime或者timedelta对象, 会话将在指定的日期失效
#         • 如果为0，在用户关闭浏览器后失效
#         • 如果为None，则将使用全局会话失效策略
#         失效时间从上一次会话被修改的时刻开始计时。
#
#         get_expiry_age()
#             # 返回多少秒后失效的秒数。对于没有自定义失效时间的会话，这等同于SESSION_COOKIE_AGE.
#             # 这个方法接受2个可选的关键字参数
#         • modification:会话的最后修改时间（datetime对象）。默认是当前时间。
#         •expiry: 会话失效信息，可以是datetime对象，也可以是int或None
#
#         get_expiry_date()
#             # 和上面的方法类似，只是返回的是日期
#
#         get_expire_at_browser_close()
#             # 返回True或False，根据用户会话是否是浏览器关闭后就结束。
#
#         clear_expired()
#             # 删除已经失效的会话数据。
#         cycle_key()
#             # 创建一个新的会话秘钥用于保持当前的会话数据。django.contrib.auth.login() 会调用这个方法。



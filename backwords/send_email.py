import os
from django.core.mail import EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'backwords.settings'

if __name__ == '__main__':
    subject, from_email, to = '来自xq的测试邮件', 'continuedake@sina.com', '1021222470@qq.com'
    text_content = '测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试'
    html_content = '<p>测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试测试</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

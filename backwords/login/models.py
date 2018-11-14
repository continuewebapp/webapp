from django.db import models

# Create your models here.


class User(models.Model):

    gender = (
        ('male', '男'),
        ('female', '女')
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default="男")
    # auto_now_add：
    # 每当对象被创建时，设为当前日期，
    # 常用于保存创建日期(注意，它是不可修改的)。
    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    # 元数据
    class Meta:
        # 排序方式 反序排序 即后注册的先显示
        ordering = ["-c_time"]
        # 用于设置模型对象的直观、人类可读的名称。
        verbose_name = "用户"
        # 与verbose_name 保持一致
        verbose_name_plural = "用户"


# 注册码
class ConfirmString(models.Model):
    # 哈希后的字段码
    code = models.CharField(max_length=256)
    # 注册码一对一关联用户
    user = models.OneToOneField('User', on_delete=True)
    c_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.name + ":   " + self.code

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "'确认码"
        verbose_name_plural = "确认码"

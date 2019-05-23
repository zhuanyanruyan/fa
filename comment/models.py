import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render


class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            '',
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=self.fail_silently,
            html_message=self.text
        )


class Comment(models.Model):  # 不仅仅是评论博客，也可能是动态啊什么的，所以向阅读次数read_statistics 一样，需要关联对象和在对象中用于区分的id
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)  # 创建时自动添加
    # User 通过反向查找（related_name）找到此用户创建的所有评论
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)

    # root 反向查找，能找到一个评论下的所有评论
    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.CASCADE)
    # 回复谁的  User 通过反向查找（related_name）找到此用户发表的评论都有哪些回复（评论）
    reply_to = models.ForeignKey(User, related_name="replies", null=True, on_delete=models.CASCADE)

    def send_mail(self):
        if self.parent is None:
            # 评论我的博客
            subject = '有人评论你的博客'
            email = self.content_object.get_email()
        else:
            # 回复评论
            subject = '有人回复你的评论'
            email = self.reply_to.email
        if email != '':
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = render(None, 'comment/send_mail.html', context).content.decode('utf-8')
            send_mail = SendMail(subject, text, email)
            send_mail.start()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['comment_time']  # 先在这里由小到大排序，最新的回复在下面，但是最新的评论也在下面就不对了，在其他地方改

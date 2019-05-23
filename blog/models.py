from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from read_statistics.models import ReadDetail, ReadNumExpandMethod
'''
用于计数
from django.contrib.contenttypes.models import ContentType
from read_statistics.models import ReadNum
from django.db.models.fields import exceptions
'''


# 博客分类(一篇博客对应一个类型，多个类型的不考虑)
class BlogType(models.Model):
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name


# 博客
class Blog(models.Model, ReadNumExpandMethod):
    title = models.CharField(max_length=50)
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE)
    # content = models.TextField()
    # content = RichTextField()
    content = RichTextUploadingField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # read_num = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now=True)
    read_details = GenericRelation(ReadDetail)

    '''
    # 用于计数
    def get_read_num(self):
        try:
            ct = ContentType.objects.get_for_model(Blog)  # 这里Blog 换成 self 也可以
            readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)
            return readnum.read_num
        except exceptions.ObjectDoesNotExist:
            return 0
    '''

    def get_url(self):
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})

    def get_email(self):
        return self.author.email

    def __str__(self):
        return "Blog:%s" % self.title

    # 定义排序信息，可用于分页，哪些在第一页，哪些在第二页...
    class Meta:
        ordering = ['-created_time']




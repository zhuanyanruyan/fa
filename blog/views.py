from django.shortcuts import render, get_object_or_404
from .models import Blog, BlogType
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
# from datetime import datetime
from read_statistics.utils import read_statistics_once_read

# 评论
#from django.contrib.contenttypes.models import ContentType
#from comment.models import Comment


# 渲染登陆框
# from user.forms import LoginForm

# each_page_blog_numbers = 3
# 用到全局公用设置，改成如下
# settings.EACH_PAGE_BLOG_NUMBERS


def get_blog_list_common_data(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOG_NUMBERS)  # 每十篇进行分页
    page_num = request.GET.get('page', 1)  # 获取url 的页面参数（GET 请求）
    page_of_blogs = paginator.get_page(page_num)

    current_page_num = page_of_blogs.number  # 获取当前页码
    # 获取前后两页
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取日期归档所对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC") #返回的是Datetime的对象列表
    blog_date_dict = {}  # 键值
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                created_time__month=blog_date.month).count()
        blog_date_dict[blog_date] = blog_count

    # 获取博客分类的对应博客数量
    # BlogType.objects.annotate(blog_count=Count('blog'))  # blog_count 不能跟BloyType现有的字段重复
    # 内部用的是sql查询; 关联的外键; blog是类Blog 的小写
    '''
    blog_types = BlogType.objects.all()
    blog_type_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_type_list.append(blog_type)
    '''
    # 获取博客分类的对应博客数量结束（两种方法）
    # context = dict(page_of_blogs=page_of_blogs, blog_types=BlogType.objects.all(), page_range=page_range,
    #             blog_dates=Blog.objects.dates('created_time', 'month', 'DESC'))

    # context = dict(page_of_blogs=page_of_blogs, blog_types=blog_type_list, page_range=page_range,
    #            blog_dates=Blog.objects.dates('created_time', 'month', 'DESC'))

    # context = dict(page_of_blogs=page_of_blogs, blog_types=BlogType.objects.annotate(blog_count=Count('blog')),
    # page_range=page_range, blog_dates=Blog.objects.dates('created_time', 'month', 'DESC'))

    context = dict(page_of_blogs=page_of_blogs, blog_types=BlogType.objects.annotate(blog_count=Count('blog')),
                   page_range=page_range, blog_dates=blog_date_dict)
    return context


def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)

    # context = dict(blogs=Blog.objects.all(), blogs_count=Blog.objects.all().count())
    # context = dict(blogs=Blog.objects.all(), blog_types=BlogType.objects.all())
    # context = dict(page_of_blogs=page_of_blogs, blog_types=BlogType.objects.all(), page_range=page_range, \
    #              blog_dates=Blog.objects.dates('created_time', 'month', 'DESC'))

    return render(request, 'blog/blog_list.html', context)


def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    # context = dict(blogs=Blog.objects.filter(blog_type=blog_type),\
    # blog_types=BlogType.objects.all(),blog_type=blog_type)

    # 双下划线的外键拓展
    # blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    blogs_all_list = Blog.objects.filter(blog_type__id=blog_type_pk)

    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render(request, 'blog/blogs_with_type.html', context)


def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year, month)
    return render(request, 'blog/blogs_with_date.html', context)


def blog_detail(request, blog_pk):
    # 这个处理函数主题是编辑博客的form表单提交，所以评论的表单提交不应该在这里写它的相应的逻辑
    # 评论的表单直接在其相应的forms.py中处理
    blog = get_object_or_404(Blog, pk=blog_pk)
    # 评论
    # blog_content_type = ContentType.objects.get_for_model(blog)
    # comments = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk, parent=None)  # 找到第一层评论
    # end 评论

    '''
    简单计数，未用ContentType 之前
    if not request.COOKIES.get('blog_%s_read' % blog_pk):
        blog.read_num += 1
        blog.save()
    '''
    read_cookie_key = read_statistics_once_read(request, blog)

    context = dict(blog=blog)
    # context['login_form'] = LoginForm()
    # 下面的这种不能降低耦合，用了templatetags,将这部分耦合度降低
    # context['comments'] = comments.order_by('-comment_time')  # 最新的评论在页面最上面

    # blog_content_type.model 得到的是blog对象(Blog类的一个实例)的字符串，因为必须要字符串类型
    # 下面的这种不能降低耦合，用了templatetags,将这部分耦合度降低
    # context['comment_form'] = CommentForm(initial={'content_type': blog_content_type.model, 'object_id': blog_pk,
    #                                               'reply_comment_id': '0'})

    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    response = render(request, 'blog/blog_detail.html', context)   # 响应
    '''
    简单计数，未用ContentType 之前
    response.set_cookie('blog_%s_read' % blog_pk, 'true')   # key,value, 有效期max_age=60或者 expires=datetime
    # 不设置有效期，默认浏览器关闭cookies 失效
    '''
    response.set_cookie(read_cookie_key, 'true')  # 阅读cookie 标记
    return response

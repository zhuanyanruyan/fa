import datetime
from django.shortcuts import render, redirect
from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data, get_7_days_hot_date
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from blog.models import Blog
from django.utils import timezone
from django.core.cache import cache
# from django.contrib.auth import authenticate, login 因为自定义了login，为了避免冲突，引入下面的
'''
from django.contrib import auth
from django.urls import reverse
from .forms import LoginForm, RegForm
from django.contrib.auth.models import User
from django.http import JsonResponse
'''


def get_7_days_hot_blogs():
	today = timezone.now().date()
	date = today - datetime.timedelta(days=7)
	# 通过read_details找到外键关联的对象
	blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date) \
						.values('id', 'title') \
						.annotate(read_num_sum=Sum('read_details__read_num')) \
						.order_by('-read_num_sum')
	return blogs[:7]


def home(request):
	blog_content_type = ContentType.objects.get_for_model(Blog)
	dates, read_nums = get_seven_days_read_data(blog_content_type)
	today_hot_data = get_today_hot_data(blog_content_type)
	yesterday_hot_data = get_yesterday_hot_data(blog_content_type)

	# 获取7天热门博客的缓存数据
	hot_blogs_for_7_days = cache.get('hot_blogs_for_7_days')
	if hot_blogs_for_7_days is None:
		hot_blogs_for_7_days = get_7_days_hot_blogs()
		cache.set('hot_blogs_for_7_days', hot_blogs_for_7_days, 3600)  # 每隔1h缓存一次
		# print('calc')
	# else:
		# print('use cache')
	context = dict(read_nums=read_nums, dates=dates, today_hot_data=today_hot_data, yesterday_hot_data=yesterday_hot_data)
	# context['hot_data_for_7_days'] = get_7_days_hot_date(blog_content_type)
	context['hot_blogs_for_7_days'] = get_7_days_hot_blogs
	return render(request, 'home.html', context)


'''
def login(request):
	username = request.POST.get('username', '')  # 获取不到就为空
	password = request.POST.get('password', '')
	user = auth.authenticate(request, username=username, password=password)
	# request中含有它是从哪个页面进来的信息
	print(86876876786877678687)
	referer = request.META.get('HTTP_REFERER', reverse('home'))  #获取不到 跳到 第二个参数(逆向解析)
	if user is not None:
		auth.login(request, user)
		# Redirect
		print(78979879798798)
		return redirect(referer)
	else:
		return render(request, 'error.html', {'message': '用户名或密码不正确'})
'''

'''  挪到user中去了
def login(request):
	if request.method == 'POST':
		login_form = LoginForm(request.POST)  # 带有数据的loginForm
		if login_form.is_valid():
			user = login_form.cleaned_data['user']
			auth.login(request, user)
			return redirect(request.GET.get('from', reverse('home')))
	else:
		login_form = LoginForm()  # get请求 生成空的loginForm
	context = {}
	context['login_form'] = login_form
	return render(request, 'login.html', context)


def login_for_medal(request):
	login_form = LoginForm(request.POST)
	data = {}
	if login_form.is_valid():
		user = login_form.cleaned_data['user']
		auth.login(request, user)
		data['status'] = 'SUCCESS'
	else:
		data['status'] = 'ERROR'
	return JsonResponse(data)


def register(request):
	if request.method == 'POST':
		reg_form = RegForm(request.POST)
		if reg_form.is_valid():   #是否验证通过 clean
			username = reg_form.cleaned_data['username']
			email = reg_form.cleaned_data['email']
			password = reg_form.cleaned_data['password']
			# 创建用户
			user = User.objects.create_user(username, email, password)
			user.save()
			# 登录用户
			user = auth.authenticate(username=username, password=password)
			auth.login(request, user)
			return redirect(request.GET.get('from', reverse('home')))
	else:
		reg_form = RegForm()
	context = {}
	context['reg_form'] = reg_form
	return render(request, 'register.html', context)
'''

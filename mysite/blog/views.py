from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from .models import Blog, BlogType
from django.db.models import Count
from django.conf import settings
from datetime import datetime
# Create your views here.
each_page_blogs_number = 2

def get_blog_list_common_data(request, blogs_all_list):
    page_num = request.GET.get('page', 1)  #  获取url页面参数
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)  # 每10页进行分页
    page_of_blogs = paginator.get_page(page_num)   #  django 自动识别，如果无效直接返回1
    current_page_num = page_of_blogs.number  # 获取当前页
    # 获取当前页的前后页码各2页
    page_range = list(range(max(current_page_num-2, 1), current_page_num)) + \
                list(range(current_page_num, min(current_page_num+2, paginator.num_pages) + 1))
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
    
    # 获取相应日期对应的博客数量
    blog_dates = Blog.objects.dates('create_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year = blog_date.year ,\
                    create_time__month = blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    # print(context)
    context['blog_types'] = BlogType.objects.annotate(blog_count = Count('blog'))
    context['blog_dates'] = blog_dates_dict
    return context


def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blogs_all_list)
    return render_to_response('blog/blog_list.html', context)

def blog_detail(request, blog_pk):
    '''获取当前博客的详细信息'''
    context = {}
    blog = get_object_or_404(Blog, pk=blog_pk)
    if not request.COOKIES.get('blog_%s_read'%blog_pk):
        blog.reader_num += 1
        blog.save()
    # Blog.object.get(pk = blog_pk) # 获取到具体某一篇博客
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context['blog'] = blog
    response = render_to_response('blog/blog_detail.html', context) # 响应
    response.set_cookie('blog_%s_read'%blog_pk, 'true')  # 如果不设置过期时间，关闭浏览器cookie即失效
    return response

def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type) # filter条件按筛选时只能赋值等号
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render_to_response('blog/blog_with_type.html', context)

def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(create_time__year = year ,create_time__month = month) # filter条件按筛选时只能赋值等号
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' %(year, month)
    return render_to_response('blog/blog_with_date.html', context)

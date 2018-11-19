from stark.service.stark import site, ModelStark
from .models import *


class AuthorForm(ModelStark):
    list_filter = ['name']


site.register(Author, AuthorForm)

site.register(AuthorDetail)


class PublishForm(ModelStark):
    list_filter = ['name']


site.register(Publish, PublishForm)

from django.forms import ModelForm


# #########自己有就用自己的，自己没有就用父类的###########
class BookModelForm(ModelForm):
    class Meta:
        model = Book  # 这块就可以定死了，因为就是给的Book表
        fields = '__all__'
        labels = {
            "title": "书籍名称",
            "price": "价格",
            "publishDate": "出版日期",
            "publish": "出版社"
        }
        error_messages={
            'title':{'required':'书籍名称不能为空'}
        }


class BookConfig(ModelStark):  # 在list页面展示，但是我们想在add页面展示 ，我们自己给他配置一个ModelFormDemo的类
    list_display = ['title', 'publishDate', 'price', 'publish', 'authors']
    search_fields = ['title', 'price']
    list_display_links = []

    def patch_init(self, request, queryset):
        print(queryset)
        queryset.update(price=123)

    patch_init.short_description = "批量初始化"

    actions = [patch_init]
    list_filter = ['title', 'publish', 'authors']

    # 实例化
    modelform_class = BookModelForm


site.register(Book, BookConfig)

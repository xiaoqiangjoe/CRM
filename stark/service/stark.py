from django.conf.urls import url
from django.shortcuts import HttpResponse, redirect, render
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Q
from stark.urls.page import Pagination  # 做分页
from django.db.models.fields.related import ManyToManyField,ForeignKey
from django.forms.models import ModelChoiceField
class ShowList(object):
    def __init__(self, config, date_list, request):
        '''

        :param config:     list_view视图的self，也就是配置类，下面所有的self换成 self.config
        :param date_list:  表单中需要一个date_list，视图函数传过来
        '''
        self.config = config
        self.date_list = date_list
        # 分页实例化，需要哪些参数，传哪些参数  self.pagination = Pagination
        self.request = request
        current_page = int(self.request.GET.get("page", 1))
        data_count = self.date_list.count()
        base_path = self.request.path
        # 实例化
        self.pagination = Pagination(current_page, data_count, base_path, self.request.GET, per_page_num=2,pager_count=11, )
        # 做分页切片
        self.page_data = self.date_list[self.pagination.start:self.pagination.end]
        # 批量操作
        '''
        actions(self.actions得到是一个列表，里面是一个个的函数对象)
         怎么取到函数的名字  __name__

         '''
        self.actions = self.config.new_actions()

    # 构建  批量操作
    def get_actions_dict(self):
        temp = []
        for action in self.actions:
            temp.append({
                'name': action.__name__,  # 取得函数的名字
                'desc': action.short_description  # short_description在配置类里定义取函数的属性
            })
        return temp

    # 构建 filter 过滤  适合一对多，多对多的版本
    '''
    def get_filter_linktags(self):
        # print(self.config.list_filter)          # 用户自己配置的字段['publish', 'authors']
        link_dict = {}
        import copy
        for filter_field in self.config.list_filter:

           #  
           #  print('filter_field',filter_field)    # publish   authors 是字符串形式
           #  print(type(filter_field))             # <class 'str'>?????问如何用str类型字段找到字段对象
           # 
           #  ☆☆☆☆☆☆filter_field_obj = self.config.model._meta.get_field(filter_field)  (有用)☆
           # 
           #  print('filter_field_obj',filter_field_obj)
           #  print('filter_field_obj',type(filter_field_obj))
           #  
           #  # app01.Book.authors|app01.Book.publish (app01下的book表的字段authors和publish)
           #  现在想找字段authors和publish关联的那张表下的所有数据
           #      又知道authors和publish是一对多(ForeignKey)和多对多(ManyToManyField)的关联方式
           #      进入ForeignKey源码我们发现有一个rel的，我们利用他
           #  
           #  print('rel', filter_field_obj.rel)  # <ManyToOneRel: app01.book><ManyToManyRel: app01.book>
           # ☆☆☆☆☆☆☆ print('rel....', filter_field_obj.rel.to.objects.all())(有用)☆
           #  # <QuerySet [<Publish: 沙河出版社>, <Publish: 昌平出版社>]>
           #  # <QuerySet [<Author: 乔>, <Author: 刚>]>
           #  
            params = copy.deepcopy(self.request.GET)
            filter_field_obj = self.config.model._meta.get_field(filter_field)

            data_list = filter_field_obj.rel.to.objects.all()   # QuerySet

            url_filter_id = self.request.GET.get(filter_field,0) # 获取url上传来的值,下面判断用

            temp = []
            if params.get(filter_field):
                del params[filter_field]
                temp.append('<a href="?%s">All</a>'%params.urlencode())
            else:
                temp.append('<a class="active" href="">All</a>')
            for obj in data_list:
                # 给 params 赋值 以 publish和action为键，以‘内容’为值
                params[filter_field] = obj.pk    # 字典
                _url = params.urlencode()        # 序列化
                if int(url_filter_id) == obj.pk :
                    s = '<a class="active" href="?%s">%s</a>'%(_url, str(obj))
                else:
                    s = '<a  href="?%s">%s</a>' % (_url, str(obj))
                temp.append(s)

            link_dict[filter_field] = temp
        return link_dict
        '''''

    # 构建 filter 过滤  适合一对多，多对多, 普通字段的版本
    def get_filter_linktags(self):

        link_dict = {}
        import copy
        for filter_field in self.config.list_filter:
            params = copy.deepcopy(self.request.GET)
            filter_field_obj = self.config.model._meta.get_field(filter_field)
            '''☆☆☆☆☆ 不应该用这个带to的方法来取值了
            data_list = filter_field_obj.rel.to.objects.all()  # QuerySet
            
            '''
            params = copy.deepcopy(self.request.GET)
            filter_field_obj = self.config.model._meta.get_field(filter_field)
            if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj,ManyToManyField):
                data_list = filter_field_obj.rel.to.objects.all()  # QuerySet
            else:
                data_list = self.config.model.objects.all().values('pk',filter_field) #不要写死 ‘title’

            url_filter_id = self.request.GET.get(filter_field, 0)  # 获取url上传来的值,下面判断用
            temp = []
            if params.get(filter_field):
                del params[filter_field]
                temp.append('<a href="?%s">All</a>' % params.urlencode())
            else:
                temp.append('<a class="active" href="">All</a>')

            for obj in data_list:  # obj  字典
                # obj 就不一定是一个queryset
                if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
                    pk = obj.pk
                    text = str(obj)
                    params[filter_field] = pk
                else:  # 就不是queryset，而是一个一个的value—-list
                    pk = obj.get('pk')
                    text = obj.get(filter_field)
                    params[filter_field] = text

                # 给 params 赋值 以 publish和action为键，以‘内容’为值

                _url = params.urlencode()  # 序列化
                if url_filter_id == str(pk) or url_filter_id == text:
                    s = '<a class="active" href="?%s">%s</a>' % (_url, text)
                else:
                    s = '<a  href="?%s">%s</a>' % (_url, text)
                temp.append(s)

            link_dict[filter_field] = temp
        return link_dict

    # 构建表头
    def get_header(self):
        # print('new_list_diaplay',self.get_new_list_display())     #[checkbox ,"__str__", edit ,deletes]
        header_list = []
        for field in self.config.get_new_list_display():
            if callable(field):
                val = field(self.config, header=True)
                header_list.append(val)
            else:
                if field == '__str__':
                    header_list.append(self.config.model._meta.model_name.upper())  # 添加表的名字
                else:
                    val = self.config.model._meta.get_field(field).verbose_name
                    header_list.append(val)
        return header_list
    '''
    # 构建表单数据-------没有显示作者在表里版
    def get_body(self):
        new_data_list = []
        # for obj in self.date_list:   之前在循环所有的数据，现在我们要循环我们分页的数据
        for obj in self.page_data:
            temp = []
            for filed in self.config.get_new_list_display():
                if callable(filed):
                    val = filed(self.config, obj)  # 这里传obj就是为了app01中的stark中用
                else:
                    val = getattr(obj, filed)
                    if filed in self.config.list_display_links:
                        _urls = self.config.get_change_url(obj)
                        val = mark_safe('<a href="%s">%s</a>' % (_urls, val))

                temp.append(val)
            new_data_list.append(temp)
        return new_data_list

      '''

    # 构建表单数据-------显示作者在表里版
    def get_body(self):
        new_data_list = []
        # for obj in self.date_list:   之前在循环所有的数据，现在我们要循环我们分页的数据
        for obj in self.page_data:
            temp = []
            for filed in self.config.get_new_list_display():
                if callable(filed):
                    val = filed(self.config, obj)  # 这里传obj就是为了app01中的stark中用
                else:
                    try:
                        # 通过字段字符串拿到字段对象
                        filed_obj = self.config.model._meta.get_field(filed)
                        if isinstance(filed_obj, ManyToManyField):
                            # ret = getattr(obj, filed)  #类似 self.model.authors缺一个.all()
                            ret = getattr(obj, filed).all()
                            authors_list = []
                            for MTMobj in ret:
                                authors_list.append(str(MTMobj))
                            val='.'.join(authors_list)
                        else:
                            val = getattr(obj, filed)
                            if filed in self.config.list_display_links:
                                _urls = self.config.get_change_url(obj)
                                val = mark_safe('<a href="%s">%s</a>' % (_urls, val))
                    except Exception:
                        val = getattr(obj, filed)

                temp.append(val)
            new_data_list.append(temp)
        return new_data_list

#####################################################################3
class ModelStark(object):
    list_display = ['__str__']
    list_display_links = []
    modelform_class = []
    search_fields = []
    actions = []
    list_filter = []

    def __init__(self, model, site):
        self.model = model
        self.site = site

    # 默认action
    def patch_delete(self, request, queryset):
        queryset.delete()
    patch_delete.short_description = "批量删除"

    # 获取models类的
    def get_models_class(self):
        # 构建一个form表单 传到html
        if not self.modelform_class:
            '''
            如果为空的时候，要是用户自己定制了ModelForm，就用用户自己的
            要是用户没有定制我就用if not
            '''

            from django.forms import ModelForm
            class ModelFormDemo(ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"

            return ModelFormDemo
        else:
            return self.modelform_class

    def get_new_form(self, form):
        for bfiled in form:      #拿到每一个字段
            # from django.forms.boundfield import BoundField
            # print(type(bfiled)) <class 'django.forms.boundfield.BoundField'>进去源码有个field
            # print(bfiled.field) 得到modelForm的字段ModelChoiceField与ModelMultipleChoiceField

            if isinstance(bfiled.field, ModelChoiceField):
                bfiled.is_pop = True   #对象 点属性 = 一个值，以后就可以点这个属性了

                # 构建url 我们不知道是那张表，我们一定是关联字段的表
                # print(bfiled.field.queryset.model)   # app01.models.Publish'  打印出关联的表
                related_app_label = bfiled.field.queryset.model._meta.app_label
                related_model_name = bfiled.field.queryset.model._meta.model_name

                _url=reverse("%s_%s_add"%(related_app_label, related_model_name))
                bfiled.url = _url+"?pop_res_id=%s"%bfiled.name
        return form

    # 视图函数
    def add_view(self, request):  # 要加self, request
        ModelFormDemo = self.get_models_class()
        form = ModelFormDemo()
        # ###处理pop操作######
        '''for bfiled in form:      #拿到每一个字段
            # from django.forms.boundfield import BoundField
            # print(type(bfiled)) <class 'django.forms.boundfield.BoundField'>进去源码有个field
            # print(bfiled.field) 得到modelForm的字段ModelChoiceField与ModelMultipleChoiceField

            if isinstance(bfiled.field, ModelChoiceField):
                bfiled.is_pop = True   #对象 点属性 = 一个值，以后就可以点这个属性了

                # 构建url 我们不知道是那张表，我们一定是关联字段的表
                # print(bfiled.field.queryset.model)   # app01.models.Publish'  打印出关联的表
                related_app_label = bfiled.field.queryset.model._meta.app_label
                related_model_name = bfiled.field.queryset.model._meta.model_name

                _url=reverse("%s_%s_add"%(related_app_label, related_model_name))
                bfiled.url = _url+"?pop_res_id=%s"%bfiled.name
                
        '''

        form = self.get_new_form(form)

        # post 操作
        if request.method == "POST":
            form = ModelFormDemo(request.POST)  # request.POST取出数据，校验后保存
            if form.is_valid():
                obj = form.save()

                # 取 url 是get 请求
                pop_res_id = request.GET.get('pop_res_id')
                if pop_res_id:
                    res = {"pk": obj.pk, "text": str(obj), "pop_res_id": pop_res_id}
                    import json
                    return render(request, "pop.html", {"res": res})
                else:
                    return redirect(self.get_list_url())  # 反向解析  正常在url上输入url
        return render(request, 'add_view.html', locals())

    def delete_view(self, request, id):
        url = self.get_list_url()
        if request.method == "POST":
            self.model.objects.filter(pk=id).delete()
            return redirect(url)
        return render(request, "delete_view.html", locals())

    def change_view(self, request, id):
        ModelFormDemo = self.get_models_class()
        edit_obj = self.model.objects.filter(pk=id).first()

        if request.method == "POST":
            form = ModelFormDemo(request.POST, instance=edit_obj)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, "add_view.html", locals())
        form = ModelFormDemo(instance=edit_obj)  # 因为是编辑页面，框里要有内容，instance = edit_obj， 有id取出edit_obj
        form = self.get_new_form(form)
        return render(request, 'change_view.html', locals())

    # 反向解析路径的函数
    def get_change_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _urls = reverse('%s_%s_change' % (app_label, model_name), args=(obj.pk,))

        return _urls

    def get_delete_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_delete" % (app_label, model_name), args=(obj.pk,))
        return _url

    def get_add_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_add" % (app_label, model_name))
        return _url

    def get_list_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_list" % (app_label, model_name))
        return _url

    #     删除，编辑，复选框----（在访问那个视图都显示）

    def edit(self, obj=None, header=False):
        if header:
            return '操作'
        # ======反向解析方法
        # model_name = self.model._meta.model_name
        # app_label = self.model._meta.app_label
        # _urls = reverse('%s_%s_change' % (app_label, model_name), args=(obj.pk,))
        _urls = self.get_change_url(obj)
        return mark_safe('<a href="%s">编辑</a>' % _urls)

    def deletes(self, obj=None, header=False):
        if header:
            return '操作'
        # model_name = self.model._meta.model_name
        # app_label = self.model._meta.app_label
        # _urls = reverse('%s_%s_delete' % (app_label, model_name), args=(obj.pk,))
        _urls = self.get_delete_url(obj)
        return mark_safe('<a href="%s">删除</a>' % _urls)

    def checkbox(self, obj=None, header=False):
        if header:
            return mark_safe("<input class='check_box' type='checkbox'>")
        return mark_safe("<input class='check_item' type='checkbox' name='selected_pk' value='%s'>" % obj.pk)

    # 构建新的list_display
    def get_new_list_display(self):
        '''
        :return: 新构建的 list_display
        '''
        temp = []
        temp.append(ModelStark.checkbox)
        temp.extend(self.list_display)
        if not self.list_display_links:
            temp.append(ModelStark.edit)
        temp.append(ModelStark.deletes)
        return temp

    # 构建新的new_actions 批量操作
    def new_actions(self):
        temp = []
        temp.append(ModelStark.patch_delete)
        temp.extend(self.actions)
        return temp

    def get_serach_conditon(self, request):
        key_word = request.GET.get("q", '')  # 加一个空字符串
        self.key_word = key_word  # 当前类 下的实例变量

        '''
        先实例化Q---search_connection
        实例化.children....
        or的关系
    
        '''
        search_connection = Q()
        if key_word:
            search_connection.connector = "or"
            for search_field in self.search_fields:
                search_connection.children.append((search_field + "__contains", key_word))  # "__contains"模糊查询
        return search_connection

    def get_filter_conditon(self,request):
        search_connection = Q()
        for filter_field,val in request.GET.items():
            if filter_field in self.list_filter:
                search_connection.children.append((filter_field,val))
        return search_connection

    def list_view(self, request):
        '''
        展示数据 表头与表单
        :param request:
        :return:
        '''
        '''POST请求'''
        if request.method == 'POST':
            # print("POST:", request.POST)  得到了函数命名和选中的数据
            action = request.POST.get('action')
            selected_pk = request.POST.getlist("selected_pk")
            # action()是一个字符串，不能直接执行，所以用反射
            action_func = getattr(self, action)  # self 就是当前配置类
            '''admin 是queryset，我们取出queryset'''
            queryset = self.model.objects.filter(pk__in=selected_pk)
            action_func(request, queryset)

        '''get请求'''
        # 获取serach的Q对象
        search_connection = self.get_serach_conditon(request)
        # 获取filter的Q对象
        filter_connection = self.get_filter_conditon(request)
        # 筛选获取当前表所有数据
        date_list = self.model.objects.all().filter(search_connection).filter(filter_connection)
        # 按照showlist展示页面
        showlist = ShowList(self, date_list, request)  # 传一个self，showlist里面没有,showlist的init接收(config)

        # 构建一个查看的url---匹配href
        add_url = self.get_add_url()
        return render(request, 'list_view.html', locals())

    def get_url_two(self):
        '''
        设计url获取二级分发
        :return: 二级分发的url
        '''
        temp = []
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        temp.append(url(r"^add/", self.add_view, name='%s_%s_add' % (app_label, model_name)))
        temp.append(url(r"^(\d+)/delete/", self.delete_view, name='%s_%s_delete' % (app_label, model_name)))
        temp.append(url(r"^(\d+)/change/", self.change_view, name='%s_%s_change' % (app_label, model_name)))
        temp.append(url(r"^$", self.list_view, name='%s_%s_list' % (app_label, model_name)))
        return temp

    @property
    def urls2(self):
        return self.get_url_two(), None, None


# ================================================================

class StarkSite(object):
    def __init__(self):
        self._registry = {}

    def register(self, model, stark_class=None):
        '''

        :param model:         表名
        :param stark_class:   配置类对象, 可以不传 默认为None
        :return:
        '''
        if not stark_class:
            stark_class = ModelStark
        self._registry[model] = stark_class(model, self)

    # =====================================================================

    def get_url_one(self):
        '''
        设计url获取一级分发
        :return:
        '''
        temp = []
        for model, stark_class_obj in self._registry.items():
            model_name = model._meta.model_name
            app_label = model._meta.app_label

            temp.append(url(r"%s/%s/" % (app_label, model_name), stark_class_obj.urls2))
        return temp

    @property
    def urls(self):
        return self.get_url_one(), None, None


site = StarkSite()


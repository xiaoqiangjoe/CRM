from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class StarkConfig(AppConfig):
    name = 'stark'

    def ready(self):
        '''
        有ready方法，django会执行ready方法
        目的：django在启动的时候就加载stark
        :return:
        '''
        autodiscover_modules('stark')

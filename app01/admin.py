from django.contrib import admin
from .models import *


admin.site.register(Author)
admin.site.register(AuthorDetail)
admin.site.register(Publish)
admin.site.register(Book)
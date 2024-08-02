from django.contrib import admin
from common.models import *


class TargetAdmin(admin.ModelAdmin):
    pass
admin.site.register(Target, TargetAdmin)
class PostWordSegmentationAdmin(admin.ModelAdmin):
    pass
admin.site.register(PostWordSegmentation,PostWordSegmentationAdmin)
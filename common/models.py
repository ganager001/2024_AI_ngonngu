from django.db import models


# class GroupTarget(models.Model):
#     grouptarget_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)

class Target(models.Model):
    target_name = models.CharField(max_length=30, help_text="Tên mục tiêu")
    status = models.CharField(max_length=30)

class TargetChild(models.Model):
    target_name = models.CharField(max_length=30, help_text="Tên mục tiêu")
    last_name = models.CharField(max_length=30)

class Post(models.Model):
    title = models.CharField(max_length=30, help_text="Tên mục tiêu")
    author = models.CharField(max_length=30)
    description = models.CharField(max_length=30)
    content = models.CharField(max_length=30)
    total_likes = models.CharField(max_length=30)
    total_comments = models.CharField(max_length=30)
    total_shares = models.CharField(max_length=30)
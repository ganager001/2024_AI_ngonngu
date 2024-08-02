from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True, null=False, blank=True)

    class Meta:
        abstract = True  # Lớp này không tạo bảng trong cơ sở dữ liệu

class Target(TimeStampedModel):
    target_name = models.CharField(max_length=80, help_text="Tên mục tiêu")

    def __str__(self):
        return self.target_name

class TargetChild(TimeStampedModel):
    target = models.ForeignKey(Target, on_delete=models.CASCADE, blank=False, null=True)
    target_url = models.CharField(max_length=1000, null=True, blank=False, help_text="Đường dẫn mục tiêu")
    category = models.CharField(max_length=100, null=True, blank=False, help_text="Danh mục của mục tiêu")

    def __str__(self):
        return f"{self.target.target_name} - {self.category}"

class Post(TimeStampedModel):
    targetchild = models.ForeignKey(TargetChild, on_delete=models.CASCADE, blank=False, null=True)
    post_url = models.CharField(max_length=1000, null=True, blank=False, help_text="Đường dẫn bài viết")
    author = models.CharField(max_length=50)
    title = models.CharField(max_length=150, help_text="Tên mục tiêu")
    description = models.TextField(null=True, blank=True, help_text="Mô tả")
    content = models.TextField(null=True, blank=True, help_text="Nội dung")
    total_likes = models.IntegerField(default=0, help_text="Lượt thích")
    total_comments = models.IntegerField(default=0, help_text="Lượt bình luận")
    total_shares = models.IntegerField(default=0, help_text="Lượt chia sẻ")

    def __str__(self):
        return self.title

class PostWordSegmentation(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=False, null=True)
    title_segmentation = models.CharField(max_length=150, help_text="Tên mục tiêu")
    description_segmentation = models.TextField(null=True, blank=True, help_text="Mô tả")
    content_segmentation = models.TextField(null=True, blank=True, help_text="Nội dung")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.post.title

class PostPartOfSpeech(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=False, null=True)
    title_partofspeech = models.CharField(max_length=150, help_text="Tên mục tiêu")
    description_partofspeech = models.TextField(null=True, blank=True, help_text="Mô tả")
    content_partofspeech = models.TextField(null=True, blank=True, help_text="Nội dung")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.post.title
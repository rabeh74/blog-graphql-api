from django.contrib import admin

from blog.models import Profile, Post, Tag
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields={"slug":("title",)}
admin.site.register(Profile )
admin.site.register(Post,PostAdmin)
admin.site.register(Tag)


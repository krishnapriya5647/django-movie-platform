from django.contrib import admin
from .models import Category, Movie, Favorite, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name",)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "added_by", "release_date", "rating")
    list_filter = ("category", "release_date")
    search_fields = ("title", "actors")

admin.site.register(Favorite)
admin.site.register(Comment)

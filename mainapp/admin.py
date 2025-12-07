from django.contrib import admin
from .models import Book, TeamMember

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    search_fields = ('title', 'description')  # 🔍 admin panelda qidirish


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'order', 'created_at')
    search_fields = ('name', 'position', 'bio')
    list_filter = ('position', 'created_at')
    list_editable = ('order',)
    fields = ('name', 'position', 'photo', 'bio', 'telegram', 'instagram', 'gmail', 'order')

# usuarios/admin.py
from django.contrib import admin
from .models import SearchLog

@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'term', 'timestamp')
    list_filter = ('user', 'timestamp')
    search_fields = ('term', 'user__username')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
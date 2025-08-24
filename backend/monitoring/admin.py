from django.contrib import admin
from .models import Snapshot, Process

@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = ('id', 'hostname', 'created_at')
    search_fields = ('hostname',)

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('snapshot', 'name', 'pid', 'ppid', 'cpu_percent', 'mem_percent')
    list_filter = ('snapshot__hostname',)
    search_fields = ('name',)

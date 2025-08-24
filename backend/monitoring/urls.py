from django.urls import path
from . import views

urlpatterns = [
    path('process-snapshots/', views.ingest_snapshot, name='ingest'),  # POST
    path('process-snapshots/latest', views.latest_snapshot, name='latest'),  # GET
    path('process-snapshots/list', views.list_snapshots, name='list'),  # GET
    path('process-snapshots/<uuid:pk>', views.get_snapshot, name='detail'),  # GET
    path('process-snapshots/latest-page', views.latest_snapshot_page, name='latest-page'),

]

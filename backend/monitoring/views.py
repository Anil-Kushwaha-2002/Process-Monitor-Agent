from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Snapshot, Process
from .serializers import SnapshotInSerializer, SnapshotOutSerializer
from .auth import APIKeyAuthentication
from django.shortcuts import render

API_KEY = "dev-api-key-please-change"  # must match agent.ini

@api_view(['POST'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([])
@transaction.atomic
def ingest_snapshot(request):
    serializer = SnapshotInSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    snapshot = Snapshot.objects.create(
        hostname=data['hostname'],
        created_at=data.get('created_at') or timezone.now(),
    )

    procs = [Process(
        snapshot=snapshot,
        pid=p['pid'],
        ppid=p['ppid'],
        name=p['name'][:255],
        cpu_percent=p.get('cpu_percent'),
        mem_rss=p.get('mem_rss'),
        mem_percent=p.get('mem_percent'),
    ) for p in data['processes']]

    Process.objects.bulk_create(procs, batch_size=1000)
    return Response({'snapshot_id': str(snapshot.id)}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def latest_snapshot(request):
    hostname = request.query_params.get('hostname')
    qs = Snapshot.objects.all()
    if hostname:
        qs = qs.filter(hostname=hostname)
    snap = qs.order_by('-created_at').prefetch_related('processes').first()
    if not snap:
        return Response({'detail': 'No data'}, status=404)
    return Response(SnapshotOutSerializer(snap).data)

@api_view(['GET'])
def list_snapshots(request):
    hostname = request.query_params.get('hostname')
    limit = int(request.query_params.get('limit', '20'))
    qs = Snapshot.objects.all()
    if hostname:
        qs = qs.filter(hostname=hostname)
    snaps = list(qs.order_by('-created_at')[:limit])
    data = [{
        'id': str(s.id),
        'hostname': s.hostname,
        'created_at': s.created_at,
        'count': s.processes.count(),
    } for s in snaps]
    return Response(data)

@api_view(['GET'])
def get_snapshot(request, pk):
    try:
        snap = Snapshot.objects.prefetch_related('processes').get(pk=pk)
    except Snapshot.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    return Response(SnapshotOutSerializer(snap).data)



def latest_snapshot_page(request):
    snapshot = Snapshot.objects.order_by('-created_at').prefetch_related('processes').first()
    return render(request, 'latest_snapshot.html', {'snapshot': snapshot})
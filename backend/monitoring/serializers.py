from rest_framework import serializers
from .models import Snapshot, Process

class ProcessInSerializer(serializers.Serializer):
    pid = serializers.IntegerField()
    ppid = serializers.IntegerField()
    name = serializers.CharField()
    cpu_percent = serializers.FloatField(required=False, allow_null=True)
    mem_rss = serializers.IntegerField(required=False, allow_null=True)
    mem_percent = serializers.FloatField(required=False, allow_null=True)

class SnapshotInSerializer(serializers.Serializer):
    hostname = serializers.CharField()
    created_at = serializers.DateTimeField(required=False)
    processes = ProcessInSerializer(many=True)

class ProcessOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ('pid','ppid','name','cpu_percent','mem_rss','mem_percent')

class SnapshotOutSerializer(serializers.ModelSerializer):
    processes = ProcessOutSerializer(many=True)

    class Meta:
        model = Snapshot
        fields = ('id','hostname','created_at','processes')

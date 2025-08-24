import uuid
from django.db import models

class Snapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostname = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.hostname} @ {self.created_at.isoformat()}"

class Process(models.Model):
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE, related_name='processes')
    pid = models.IntegerField()
    ppid = models.IntegerField()
    name = models.CharField(max_length=255)
    cpu_percent = models.FloatField(null=True, blank=True)
    mem_rss = models.BigIntegerField(null=True, blank=True)
    mem_percent = models.FloatField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['snapshot', 'pid']),
            models.Index(fields=['snapshot', 'ppid']),
        ]

    def __str__(self):
        return f"{self.name}({self.pid})"

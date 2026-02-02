from django.db import models


class Equipment(models.Model):  #main equipment model db
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class UploadHistory(models.Model): #stores upload histories
    uploaded_at = models.DateTimeField(auto_now_add=True)
    summary = models.JSONField(default=dict)

    def __str__(self):
        return f"Upload {self.id} at {self.uploaded_at}"
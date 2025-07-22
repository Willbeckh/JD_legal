from django.db import models


class SiteSetting(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField()

    def __str__(self):
        return self.key

        # TODO: add this to admin.py to enable editting keys like (last_transcriber_id)

import logging
from hashlib import sha256

from django.db import models
from django.contrib.auth.models import User

from share.models.fields import ZipField, DatetimeAwareJSONField
from share.models.validators import is_valid_jsonld

logger = logging.getLogger(__name__)
__all__ = ('ShareSource', 'RawData', 'NormalizedManuscript', 'NormalizationQueue', 'Normalization')


class ShareSource(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    # Nullable as actual providers will not have users
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    @property
    def is_entity(self):
        return self.user is None

    @property
    def is_user(self):
        return self.user is not None

    def __str__(self):
        return '{}'.format(self.name)


class RawDataManager(models.Manager):

    def store_data(self, doc_id, data, source):
        rd, created = self.get_or_create(
            source=source,
            provider_doc_id=doc_id,
            sha256=sha256(data).hexdigest(),
            defaults={'data': data},
        )

        if created:
            logger.info('Newly created RawData for document {} from {}'.format(doc_id, source))
            NormalizationQueue(data=rd).save()
        else:
            logger.info('Saw exact copy of document {} from {}'.format(doc_id, source))

        rd.save()  # Force timestamps to update
        return rd


class RawData(models.Model):
    id = models.AutoField(primary_key=True)

    source = models.ForeignKey(ShareSource)
    provider_doc_id = models.CharField(max_length=256)

    data = ZipField(blank=False)
    sha256 = models.CharField(max_length=64)

    date_seen = models.DateTimeField(auto_now=True)
    date_harvested = models.DateTimeField(auto_now_add=True)

    objects = RawDataManager()

    def __str__(self):
        return '({}) {} {}'.format(self.id, self.source, self.provider_doc_id)

    @property
    def processsed(self):
        return self.date_processed is not None  # TODO: this field doesn't exist...

    class Meta:
        unique_together = (('provider_doc_id', 'source', 'sha256'),)
        verbose_name_plural = 'Raw data'


class NormalizedManuscript(models.Model):
    id = models.AutoField(primary_key=True)
    raw_data = models.ForeignKey(RawData)
    processed_at = models.DateTimeField(null=True)
    normalized_data = DatetimeAwareJSONField(default={}, validators=[is_valid_jsonld,])

    def __str__(self):
        return '{} processed at {}'.format(self.raw_data.source.name, self.processed_at)

class Normalization(models.Model):
    id = models.AutoField(primary_key=True)
    data = models.ForeignKey(RawData)
    date = models.DateTimeField(auto_now_add=True)


class NormalizationQueue(models.Model):
    data = models.OneToOneField(RawData, primary_key=True)

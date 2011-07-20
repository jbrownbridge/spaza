from django.db import models
from django.contrib.auth.models import User

from datetime import timedelta, datetime
from picklefield.fields import PickledObjectField

# Create your models here.
class USSDSessionManager(models.Manager):
  INACTIVE_TIME_LIMIT = timedelta(minutes=15)

  def recent(self, user):
    try:
      session = super(USSDSessionManager, self) \
        .get_query_set() \
        .get(
          # Session for current user
          user=user,
          # Restore session within timeframe if it ended incorrectly
          updated_at__gte=datetime.now() - self.INACTIVE_TIME_LIMIT,
          # Don't restore sessions that ended correctly
          current_menu__isnull=False)
      return session
    except USSDSession.DoesNotExist, e:
      return USSDSession.objects.create(user=user)

class USSDSession(models.Model):
  INACTIVE_TIME_LIMIT = timedelta(minutes=15)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  user = models.ForeignKey(User, null=True)
  current_menu = PickledObjectField(blank=True)

  objects = USSDSessionManager()

  def __unicode__(self):
    return "%s (%s)" % (self.user, self.pk)


from django.conf import settings
from django.contrib.auth import models as auth_models

import logging

log = logging.getLogger(__name__)

class USSDAuthBackend:
  supports_object_permissions = True
  supports_anonymous_user = True
  supports_inactive_user = True

  def update_user(self, user, save=True):
    if user.username in settings.ADMIN_USERNAMES:
      if not user.is_superuser:
        user.is_superuser = True
        log.info("Authentication promoted user (%s) to superuser" % user)
    else:
      if user.is_superuser:
        user.is_superuser = False
        log.info("Authentication demoted superuser (%s) to user" % user)
      user.set_unusable_password()
    if save:
      user.save()
    return user

  def create_user(self, username=None, password=None):
    user = auth_models.User(username=username, password=password)
    user.is_staff = True
    log.debug("Authentication created new user: %s" % user)
    return self.update_user(user)
  
  def authenticate(self, username=None, password=None):
    try:
      user = auth_models.User.objects.get(username=username)
      # need to check if their facebook profile was disabled 
      # i.e. we disabled their account because they were naughty
      if not user.is_active:
        log.info("Authentication failed for disabled user: %s" % user)
        return None
      if user.is_superuser:
        if not user.check_password(password):
          log.info("Authentication failed for admin user: %s" % user)
          return None
        else:
          log.info("Authentication succeeded for admin user: %s" % user)
    except auth_models.User.DoesNotExist:
      user = self.create_user(username, password)
    self.update_user(user)
    if user:
      log.debug("Authentication succeeded for user: %s" % user)
    return user

  def get_user(self, user_id):
    try:
      return auth_models.User.objects.get(pk=user_id)
    except auth_models.User.DoesNotExist:
      return None


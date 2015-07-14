from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=get_user_model())
def send_confirmation_email(sender, instance, created, raw, **kwargs):
    if created:
        pass

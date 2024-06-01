from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import fosUser, Profile

@receiver(post_save, sender=fosUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=fosUser)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Optionally handle the case where the profile does not exist
        Profile.objects.create(user=instance)

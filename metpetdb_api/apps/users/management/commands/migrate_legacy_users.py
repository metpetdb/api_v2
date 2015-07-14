from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import transaction

from legacy.models import Users as LegacyUser


class Command(BaseCommand):
    help = 'Migrates legacy users to the new data model'

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        User.objects.all().delete()

        old_users = LegacyUser.objects.all()

        for old_user in old_users:
            User.objects.create(
                email=old_user.email,
                name=old_user.name,
                address=old_user.address,
                city=old_user.city,
                province=old_user.province,
                country=old_user.country,
                postal_code=old_user.postal_code,
                institution=old_user.institution,
                reference_email=old_user.reference_email,
                is_active=True if old_user.enabled == 'Y' else False,
                is_contributor=(True if old_user.contributor_enabled == 'Y'
                                     else False),
                professional_url=old_user.professional_url,
                research_interests=old_user.research_interests
            )

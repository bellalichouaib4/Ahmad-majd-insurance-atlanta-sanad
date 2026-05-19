from django.db import migrations
from django.contrib.auth.models import Group, Permission


def create_groups(apps, schema_editor):
    # ADMIN group — all permissions (superuser handles this, but group for clarity)
    admin_group, _ = Group.objects.get_or_create(name='ADMIN')
    # WORKER group — limited
    worker_group, _ = Group.objects.get_or_create(name='WORKER')


def remove_groups(apps, schema_editor):
    Group.objects.filter(name__in=['ADMIN', 'WORKER']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('insurance', '0006_dossier_category'),
    ]
    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]

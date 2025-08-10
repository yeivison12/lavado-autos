from django.db import migrations

def create_worker_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Worker = apps.get_model('workers', 'Worker')

    worker_group, created = Group.objects.get_or_create(name='Trabajadores')
    if created:
        content_type = ContentType.objects.get_for_model(Worker)
        permissions = Permission.objects.filter(content_type=content_type)
        worker_group.permissions.set(permissions)
        worker_group.save()

class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_worker_group),
    ]
from django.db import migrations


def create_perfis(apps, schema_editor):
    Perfil = apps.get_model('core', 'Perfil')
    Perfil.objects.get_or_create(tipo='Profissional de saúde')
    Perfil.objects.get_or_create(tipo='Usuário')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_perfis),
    ]

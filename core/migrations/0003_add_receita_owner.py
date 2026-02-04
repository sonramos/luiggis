from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_create_default_perfis'),
    ]

    operations = [
        migrations.AddField(
            model_name='receita',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receitas', to='core.usuario'),
        ),
    ]

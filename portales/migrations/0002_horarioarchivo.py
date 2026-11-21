# Generated manually for the HorarioArchivo model

import django.db.models.deletion
import portales.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portales', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HorarioArchivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('curso', models.CharField(max_length=25, unique=True)),
                ('archivo', models.FileField(upload_to=portales.models.ruta_horario)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('subido_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'horario en archivo',
                'verbose_name_plural': 'horarios en archivo',
                'ordering': ['curso'],
            },
        ),
    ]

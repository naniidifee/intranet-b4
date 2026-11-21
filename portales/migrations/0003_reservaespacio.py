# Generated manually for the ReservaEspacio model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portales', '0002_horarioarchivo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReservaEspacio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('espacio', models.CharField(choices=[('biblioteca', 'Biblioteca'), ('laboratorio', 'Laboratorio'), ('gimnasio', 'Gimnasio')], max_length=20)),
                ('fecha', models.DateField()),
                ('motivo', models.CharField(max_length=150)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'), ('cancelada', 'Cancelada')], default='pendiente', max_length=10)),
                ('creada', models.DateTimeField(auto_now_add=True)),
                ('revisada_en', models.DateTimeField(blank=True, null=True)),
                ('comentario_admin', models.CharField(blank=True, max_length=200)),
                ('bloque', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservas', to='portales.bloquehorario')),
                ('docente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas_espacios', to=settings.AUTH_USER_MODEL)),
                ('revisada_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'reserva de espacio',
                'verbose_name_plural': 'reservas de espacios',
                'ordering': ['-creada'],
                'constraints': [
                    models.UniqueConstraint(condition=models.Q(('estado', 'aprobada')), fields=('espacio', 'fecha', 'bloque'), name='reserva_aprobada_unica'),
                    models.UniqueConstraint(condition=models.Q(('estado__in', ['pendiente', 'aprobada'])), fields=('docente', 'espacio', 'fecha', 'bloque'), name='reserva_activa_unica_por_docente'),
                ],
            },
        ),
    ]

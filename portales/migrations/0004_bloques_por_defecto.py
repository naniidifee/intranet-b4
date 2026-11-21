from datetime import time

from django.db import migrations

# (tipo, jornada, número, orden, inicio, término)
BLOQUES = [
    ("clase", "manana", 1, 1, time(7, 45), time(8, 30)),
    ("clase", "manana", 2, 2, time(8, 30), time(9, 15)),
    ("recreo", "manana", None, 3, time(9, 15), time(9, 30)),
    ("clase", "manana", 3, 4, time(9, 30), time(10, 15)),
    ("clase", "manana", 4, 5, time(10, 15), time(11, 0)),
    ("recreo", "manana", None, 6, time(11, 0), time(11, 15)),
    ("clase", "manana", 5, 7, time(11, 15), time(12, 0)),
    ("clase", "manana", 6, 8, time(12, 0), time(12, 45)),
    ("almuerzo", "manana", None, 9, time(12, 45), time(13, 30)),
    ("clase", "tarde", 7, 1, time(13, 30), time(14, 15)),
    ("clase", "tarde", 8, 2, time(14, 15), time(15, 0)),
]


def cargar_bloques(apps, schema_editor):
    BloqueHorario = apps.get_model("portales", "BloqueHorario")

    # Si UTP ya creó bloques, no se toca nada.
    if BloqueHorario.objects.exists():
        return

    BloqueHorario.objects.bulk_create([
        BloqueHorario(
            tipo=tipo,
            jornada=jornada,
            numero=numero,
            orden=orden,
            hora_inicio=inicio,
            hora_fin=fin,
        )
        for tipo, jornada, numero, orden, inicio, fin in BLOQUES
    ])


class Migration(migrations.Migration):

    dependencies = [
        ("portales", "0003_reservaespacio"),
    ]

    operations = [
        migrations.RunPython(cargar_bloques, migrations.RunPython.noop),
    ]

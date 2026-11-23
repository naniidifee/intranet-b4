from django.db import models

# Create your models here.

class RegistroEnvioCorreo(models.Model):
    destinatario = models.EmailField()
    asunto = models.CharField(max_length=255)
    enviado_en = models.DateTimeField(auto_now_add=True)
    exitoso = models.BooleanField(default=True)
    error = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-enviado_en"]

    def __str__(self):
        estado = "OK" if self.exitoso else "ERROR"
        return f"[{estado}] {self.destinatario} - {self.asunto}"
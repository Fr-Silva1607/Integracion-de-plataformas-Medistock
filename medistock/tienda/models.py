from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator, RegexValidator, URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from urllib.parse import urlparse


class Producto(models.Model):
    TIPOS_VENTA = [
        ('fisico', 'Físico'),
        ('digital', 'Digital'),
        ('servicio', 'Servicio'),
    ]

    ALLOWED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif')

    nombre_validator = RegexValidator(
        regex=r'^[\w\s\-\']+$',
        message=_('El nombre solo puede contener letras, números, espacios, guiones y apóstrofes.'),
    )

    etiqueta_validator = RegexValidator(
        regex=r'^[\w\s\-\']*$',
        message=_('La etiqueta de precio solo puede contener letras, números, espacios, guiones y apóstrofes.'),
    )

    nombre = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), nombre_validator],
        help_text=_('Nombre del producto. Mínimo 3 caracteres.'),
    )
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(1000)],
        help_text=_('Precio mínimo aceptado: 1000.'),
    )
    imagen_url = models.URLField(
        max_length=1024,
        blank=True,
        null=True,
        validators=[URLValidator(schemes=['http', 'https'])],
        help_text=_('URL de la imagen. Solo se permiten formatos de imagen válidos.'),
    )
    categoria = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        validators=[nombre_validator],
        help_text=_('Categoría del producto.'),
    )
    tipo_venta = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=TIPOS_VENTA,
        help_text=_('Tipo de venta del producto.'),
    )
    etiqueta_precio = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[etiqueta_validator],
        help_text=_('Etiqueta de precio opcional.'),
    )
    cantidad = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=_('Cantidad disponible. No puede ser negativa.'),
    )

    class Meta:
        db_table = 'productos'
        verbose_name = _('Producto')
        verbose_name_plural = _('Productos')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()

        if self.precio is not None and self.precio < 1000:
            raise ValidationError({'precio': _('El precio mínimo permitido es 1000.')})

        if self.imagen_url:
            parsed_url = urlparse(self.imagen_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValidationError({'imagen_url': _('La URL de la imagen no es válida.')})

            if not parsed_url.path.lower().endswith(self.ALLOWED_IMAGE_EXTENSIONS):
                raise ValidationError({
                    'imagen_url': _(
                        'La imagen debe tener una extensión válida: jpg, jpeg, png, gif, webp o avif.'
                    )
                })

        if self.nombre and len(self.nombre.strip()) == 0:
            raise ValidationError({'nombre': _('El nombre no puede estar vacío.')})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

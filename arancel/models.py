from django.db import models

# Función para convertir números a romanos
def int_to_roman(number):
    roman_numerals = {
        1: 'I', 4: 'IV', 5: 'V', 9: 'IX', 10: 'X',
        40: 'XL', 50: 'L', 90: 'XC', 100: 'C',
        400: 'CD', 500: 'D', 900: 'CM', 1000: 'M'
    }
    result = ''
    for value, numeral in sorted(roman_numerals.items(), key=lambda x: x[0], reverse=True):
        while number >= value:
            result += numeral
            number -= value
    return result

class Seccion(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        # Devuelve "Sección I" en lugar de solo el nombre
        return f"Sección {int_to_roman(self.id)}"


class Capitulo(models.Model):
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='capitulos')
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)  # Agrega este campo

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Partida(models.Model):
    capitulo = models.ForeignKey(Capitulo, on_delete=models.CASCADE, related_name='partidas')
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField()
    unidad_medida = models.CharField(max_length=50, blank=True, null=True)
    documento_adicional = models.TextField(blank=True, null=True)
    preferencias_arancelarias = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.codigo


class Subpartida(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='subpartidas')
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField()
    unidad_medida = models.CharField(max_length=50, blank=True, null=True)
    documento_adicional = models.TextField(blank=True, null=True)
    preferencias_arancelarias = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.codigo

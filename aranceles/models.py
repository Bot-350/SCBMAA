from django.db import models

def int_to_roman(number):
    if not isinstance(number, int) or not 0 < number < 4000: return str(number)
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num, i = '', 0
    while number > 0:
        for _ in range(number // val[i]):
            roman_num += syb[i]
            number -= val[i]
        i += 1
    return roman_num

class Seccion(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"SECCIÓN {int_to_roman(self.id)}"

class Capitulo(models.Model):
    id = models.IntegerField(primary_key=True) # Usamos ID manual para coincidir con SQL
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='capitulos')
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"CAPÍTULO {self.codigo}"

class Partida(models.Model):
    id = models.AutoField(primary_key=True)
    capitulo = models.ForeignKey(Capitulo, on_delete=models.CASCADE, related_name='partidas')
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return self.codigo

class Subpartida(models.Model):
    id = models.AutoField(primary_key=True)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='subpartidas')
    codigo = models.CharField(max_length=13, unique=True)
    descripcion = models.TextField()
    ga = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unidad_medida = models.CharField(max_length=50, blank=True, null=True)
    tipo_de_doc = models.CharField(max_length=255, blank=True, null=True)
    entidad_que_emite = models.CharField(max_length=255, blank=True, null=True)
    disposicion_legal = models.CharField(max_length=255, blank=True, null=True)
    can_ace_36_47_ven = models.CharField(max_length=50, blank=True, null=True)
    ace_66_mexico = models.CharField(max_length=50, blank=True, null=True)
    ace_22_chile = models.CharField(max_length=50, blank=True, null=True)
    ace_22_prot = models.CharField(max_length=50, blank=True, null=True)
    # NO AÑADIMOS ice_iehd PORQUE NO ESTÁ EN LA IMAGEN PARA LAS SUBPARTIDAS

    def __str__(self):
        return self.codigo

class Nota(models.Model):
    TIPO_NOTA_CHOICES = [
        ('seccion', 'Nota de Sección'),
        ('capitulo', 'Nota de Capítulo'),
        ('complementaria', 'Nota Complementaria NANDINA'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_NOTA_CHOICES)
    texto = models.TextField()
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='notas', null=True, blank=True)
    capitulo = models.ForeignKey(Capitulo, on_delete=models.CASCADE, related_name='notas', null=True, blank=True)
    
    # Para manejar los puntos a), b), c)
    es_lista = models.BooleanField(default=False)
    titulo_lista = models.CharField(max_length=255, blank=True, null=True) # "Este Capítulo comprende todos los animales vivos, excepto:"

    def __str__(self):
        return f"Nota de {self.get_tipo_display()}"

class ItemNota(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE, related_name='items')
    letra = models.CharField(max_length=5) # 'a)', 'b)', etc.
    texto = models.TextField()

    def __str__(self):
      
        return self.nombre
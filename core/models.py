from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Creem choices per als camps fixos ( Sexe i Nivell )
OPCIONS_SEXE = [
    ('M', 'Masculí'),
    ('F', 'Femení'),
    ('O', 'Other'),
]


class Club(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom del Club", unique=True)
    provincia = models.CharField(max_length=100, verbose_name="Província", blank=True, null=True)
    regio = models.CharField(max_length=100, verbose_name="Comunitat Autònoma", blank=True, null=True)
    pais = models.CharField(max_length=100, default="Espanya", verbose_name="País", blank=True, null=True)

    def __str__(self):
        return self.nom
    
class Jugador(models.Model):
    # Dades bàsiques
    nom_i_cognoms = models.CharField(max_length=200, verbose_name="Nom i Cognoms")
    foto = models.ImageField(upload_to='fotos_jugadors/', blank=True, null=True, verbose_name="Foto")
    
    # Dades d'escacs
    elo_fide = models.IntegerField(default=0, verbose_name="ELOFIDE", null=True, blank=True)
    elo_regio = models.IntegerField(default=0, verbose_name="ELOREG", null=True, blank=True)
    titol = models.CharField(max_length=10, blank=True, null=True, verbose_name="Títol (GM, IM...)")
    categoria = models.CharField(max_length=50, blank=True, null=True, verbose_name="Categoria (Senior,...)")
    id_fide = models.IntegerField(default=0, verbose_name="IDFIDE", null=True, blank=True)
    id_regio = models.IntegerField(default=0, verbose_name="IDREG", null=True, blank=True)

    
    # Dades personals i filtres
    sexe = models.CharField(max_length=1, choices=OPCIONS_SEXE, verbose_name="Sexe", null=True, blank=True)
    data_naixement = models.DateField(verbose_name="Data de naixement", blank=True, null=True ) # Calculem l'edat després
    
    # Relació amb el Club
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Club")
    
    # Qui ha pujat aquest jugador (per si usuaris normals pugen fotos)
    pujat_per = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def edat(self):
        if self.data_naixement:
            today = date.today()
            # Càlcul exacte de l'edat
            return today.year - self.data_naixement.year - (
                (today.month, today.day) < (self.data_naixement.month, self.data_naixement.day)
            )
        return None # Si no té data, retornem None

    def __str__(self):
        return f"{self.nom_i_cognoms} ({self.elo_fide})"

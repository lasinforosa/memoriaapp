import os
import django

# Configurem Django per poder treballar amb la base de dades
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Llegim les variables d'entorn (les has de configurar a Render)
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if username and password:
    try:
        # Mirem si l'usuari ja existeix
        if not User.objects.filter(username=username).exists():
            print(f"Creant superusuari: {username}...")
            User.objects.create_superuser(username, email, password)
            print("Superusuari creat!")
        else:
            print("L'usuari ja existeix, no cal crear-lo.")
    except Exception as e:
        print(f"Error creant superusuari: {e}")
else:
    print("No s'han trobat les variables d'entorn per crear l'admin.")
    
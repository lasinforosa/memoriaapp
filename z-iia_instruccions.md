MemoriaApp: Guia de Desenvolupament i Desplegament
1. Planificació i Entorn Local (Windows 10)
Eines Utilitzades
Editor: Visual Studio Code (VS Code).
Gestor de Paquets: Poetry (millor que pip i venv sols per aïllar projectes).
Llenguatge: Python 3.12+.
Base de Dades Local: SQLite (per defecte a Django).
Passos Inicials
Instal·lació neta: Esborrar versions anteriors de Python. Instal·lar Python marquant "Add to PATH". Instal·lar Poetry.
Creació del projecte:
powershell

mkdir MemoriaApp
cd MemoriaApp
poetry init
poetry add django
poetry shell
django-admin startproject config .
2. Desenvolupament de l'Aplicació (Django)
Estructura de Dades (Models)
App core: Gestiona jugadors i clubs.
Club: Nom, província, regió, país.
Jugador: Nom, foto, ELO (FIDE i Regió), ID, data naixement, sexe, categoria.
Protecció Menors: Lògica al model i vistes per impedir fotos de menors de 18 anys o categories inferiors (S14, S16...).
Funcionalitats Clau
Importació: Ús de django-import-export per carregar CSVs massivament.
Filtres: Ús de django-filter per filtrar per club, ELO, categoria, foto (Sí/No).
Galeria i Detall: Llista de jugadors amb camps calculats (edat) i pàgina de detall amb enllaços externs (FIDE, FCE).
Quiz: Joc de memòria que selecciona jugadors aleatoris (filtrats) i pregunta el nom o club.
Usuaris: Registre, Login, Logout. Els usuaris poden pujar fotos.
3. Preparació per Producció
Canvis a settings.py
DEBUG = False.
ALLOWED_HOSTS: Ha d'incloure el domini i la IP.
STATIC_ROOT: Per recollir fitxers estàtics.
MEDIA_ROOT: Per guardar fotos.
Seguretat: Ús de variables d'entorn (os.environ.get) per SECRET_KEY, DEBUG i DATABASE_URL.
Fitxers Clau
requirements.txt: Generat amb pip freeze > requirements.txt.
.gitignore: Ignorar .venv, db.sqlite3, media/, .env.
4. Infraestructura (Hosting i Domini)
Solució Triada
Servidor (VPS): Hetzner Cloud (Pla CX23, Nuremberg). Ubuntu 22.04. Cost aprox. 4.50€/mes.
Domini: DonDominio (nuvoldescacs.net).
Panell de Control: CloudPanel (Gratuït, instal·lat sobre Ubuntu).
Configuració DNS a DonDominio
Cal crear registres A apuntant a la IP del servidor (ex: 46.225.239.43):

@ -> IP
memoria -> IP
www -> IP
5. Configuració del Servidor (VPS)
Connexió Inicial
bash

ssh root@LA_TEVA_IP
Si error "Host identification changed": ssh-keygen -R LA_TEVA_IP.

Instal·lació CloudPanel
El servidor ha d'estar net (sense Nginx ni MySQL preinstal·lats).

bash

curl -sS https://installer.cloudpanel.io/ce/v2/install.sh | bash
Accés: https://IP_SERVIDOR:8443.

Crear Site al CloudPanel
Add Site -> Domain: nuvoldescacs.net.
Crear usuari del site (ex: nuvol_user).
SSL/TLS -> Let's Encrypt -> Obtain Certificate.
6. Desplegament de l'App Django
Pas 1: Clonar el Codi
bash

cd /home/nuvol_user/htdocs/nuvoldescacs.net
rm -rf public # Esborrar web per defecte
git clone https://github.com/USUARI/memoriaapp.git .
# O move des de temp si cal respectar .well-known
Pas 2: Entorn Virtual i Dependències
bash

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Pas 3: Base de Dades (PostgreSQL)
bash

sudo -u postgres psql
CREATE DATABASE memoriaapp;
CREATE USER memoriauser WITH PASSWORD 'contrasenya';
GRANT ALL PRIVILEGES ON DATABASE memoriaapp TO memoriauser;
ALTER DATABASE memoriaapp OWNER TO memoriauser; # Important per Django
\q
Pas 4: Variables d'Entorn (.env)
Crear fitxer .env a l'arrel del projecte:

text

DJANGO_SECRET_KEY=una_clau_molt_llarga
DJANGO_DEBUG=False
DATABASE_URL=postgres://memoriauser:contrasenya@localhost/memoriaapp
ALLOWED_HOSTS=nuvoldescacs.net,www.nuvoldescacs.net,LA_TEVA_IP
Nota: Afegir from dotenv import load_dotenv i load_dotenv() dalt de tot de settings.py.

Pas 5: Migracions i Estàtics
bash

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
Pas 6: Gunicorn (Servidor d'Aplicació)
Crear servei gunicorn.service:

ini

[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=nuvol_user
Group=nuvol_user
WorkingDirectory=/home/nuvol_user/htdocs/nuvoldescacs.net
ExecStart=/home/nuvol_user/htdocs/nuvoldescacs.net/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 config.wsgi:application

[Install]
WantedBy=multi-user.target
Activar:

bash

systemctl start gunicorn
systemctl enable gunicorn
Pas 7: Nginx (Configuració Final)
Editar /etc/nginx/sites-enabled/nuvoldescacs.net.conf. Dins del bloc server (port 443):

nginx

location /static/ {
    alias /home/nuvol_user/htdocs/nuvoldescacs.net/staticfiles/;
}

location /media/ {
    alias /home/nuvol_user/htdocs/nuvoldescacs.net/media/;
}

location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
Reiniciar: systemctl reload nginx.

7. Flux de Treball Diari (Resum)
Per actualitzar l'app després de canvis al PC:

PC: git add . -> git commit -m "Missatge" -> git push.
VPS (SSH):
bash

cd /home/nuvol_user/htdocs/nuvoldescacs.net
git pull
source venv/bin/activate
pip install -r requirements.txt # Si hi ha noves llibreries
python manage.py migrate # Si hi ha canvis a BBDD
python manage.py collectstatic --noinput # Si hi ha canvis CSS/JS
systemctl restart gunicorn

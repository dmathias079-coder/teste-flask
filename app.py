import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, g
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# --- Configuration et Initialisation ---
app = Flask(__name__)
# La clé secrète est nécessaire pour les messages flash
app.config['SECRET_KEY'] = 'CLE_SECRETE_TRES_LONGUE_ET_UNIQUE'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Extensions de fichiers autorisées (pour la sécurité)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'ogg', 'txt', 'pdf', 'docx'}

# Crée le dossier 'uploads' s'il n'existe pas
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Sécurité du Propriétaire ---
auth = HTTPBasicAuth()

# Définition des utilisateurs (Propriétaire)
USERS = {
    "proprietaire": generate_password_hash("MonMotDePasseSecret123"),  # !!! CHANGEZ CE MOT DE PASSE !!!
}


@auth.verify_password
def verify_password(username, password):
    """Vérifie le nom d'utilisateur et le mot de passe pour l'authentification HTTP basique."""
    if username in USERS and \
            check_password_hash(USERS.get(username), password):
        return username
    return None


# --- Fonctions d'aide ---
def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- A. Route de Téléversement (pour les utilisateurs via QR Code) ---
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Formulaire pour le téléversement de fichiers par l'utilisateur (page de chargement)."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné.')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Nom de fichier vide.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                # Stockage permanent sur le serveur local
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('upload_success', filename=filename))
            except Exception as e:
                flash(f"Erreur lors de la sauvegarde : {e}")
                return redirect(request.url)

    # Affiche la page HTML d'upload (templates/upload.html)
    return render_template('upload.html')


@app.route('/success/<filename>')
def upload_success(filename):
    """Page affichée après un téléversement réussi."""
    return f"""
    <!DOCTYPE html>
    <html lang="fr"><head><title>Succès</title></head><body>
    <h1>🎉 Succès !</h1>
    <p>Le fichier <strong>'{filename}'</strong> a été téléversé avec succès et est stocké de manière permanente.</p>
    <a href="{url_for('upload_file')}">Téléverser un autre fichier</a>
    </body></html>
    """


# --- B. Routes pour le Propriétaire (Gestion et Téléchargement) ---
@app.route('/data-manager')
@auth.login_required  # Sécurité requise
def data_manager():
    """Affiche la liste des fichiers stockés (nécessite l'authentification)."""
    # Ajout de g.app pour que le template puisse accéder à la configuration
    g.app = app

    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        # Trier par date de modification (les plus récents en premier)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x)), reverse=True)
    except FileNotFoundError:
        files = []

    # Le template a besoin d'une fonction pour la taille des fichiers
    def get_file_size(filename):
        return os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return render_template('data_manager.html', files=files, get_file_size=get_file_size)


@app.route('/download/<filename>')
@auth.login_required  # Sécurité requise
def download_file(filename):
    """Permet au propriétaire de télécharger un fichier spécifique."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


# --- C. Route de Démarrage (ou autre route simple) ---
@app.route('/')
def home():
    """Redirection simple de la page d'accueil."""
    return redirect(url_for('upload_file'))


# --- Démarrage du Serveur ---
if __name__ == '__main__':
    # CETTE LIGNE DÉMARRE LE SERVEUR FLASK ET DOIT RESTER EN MARCHE
    print("Démarrage du serveur Flask...")
    app.run(debug=True)
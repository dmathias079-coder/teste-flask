import qrcode
# Correction : import os est correctement placé en haut s'il est nécessaire.
# Pour la simple génération de QR code, il n'est pas nécessaire, mais je le laisse au cas où.
import os
import io

# --- Configuration ---
# ATTENTION : Changez cette URL si vous déployez l'application en ligne !
# Elle doit pointer vers l'URL publique de votre service /upload.
URL_UPLOAD = "http://127.0.0.1:5000/upload"
NOM_FICHIER_QR = "qr_code_televersement.png"


def generate_upload_qr_code(url, filename):
    """
    Génère et sauvegarde un QR code encodant une URL spécifique.
    """
    try:
        # 1. Créer l'objet QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Haute correction d'erreur
            box_size=10,
            border=4,
        )

        # 2. Ajouter les données (l'URL)
        qr.add_data(url)
        qr.make(fit=True)

        # 3. Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")

        # 4. Sauvegarder l'image de manière permanente
        img.save(filename)

        print(f"✅ QR Code généré et sauvegardé avec succès sous : {os.path.abspath(filename)}")
        print(f"L'URL encodée est : {url}")

    except Exception as e:
        print(f"❌ Une erreur s'est produite lors de la génération du QR code : {e}")


# --- Exécution ---
if __name__ == '__main__':
    generate_upload_qr_code(URL_UPLOAD, NOM_FICHIER_QR)

    print("\n--- Rappel important ---")
    print("Pour que ce QR code fonctionne hors de votre machine,")
    print("vous devez lancer votre application Flask (`app.py`) ET la déployer en ligne.")
import qrcode
import os

# Mettez ici le lien de votre application Streamlit 
# (Par exemple, le lien réseau local fourni par Streamlit lorsque vous lancez l'app)
# Ex: "http://192.168.1.15:8501" ou votre lien web public s'il est hébergé en ligne.
URL_APPLICATION = "http://10.43.3.13:8502"

# Dossier où seront sauvegardées les images des QR Codes
DOSSIER_SORTIE = "qrcodes_url_application"
os.makedirs(DOSSIER_SORTIE, exist_ok=True)

print("==================================================")
print("   GÉNÉRATEUR DE QR CODES POUR APPLICATION WEB      ")
print("==================================================")

# Liste de vos zones / catégories ou un QR code général pour l'application
zones = ["Plomberie", "Électricité", "Quincaillerie & Outillage", "Divers"]

for zone in zones:
    # On peut ajouter un paramètre dans l'URL si on veut ouvrir directement la zone (optionnel)
    lien_complet = f"{URL_APPLICATION}" # ou f"{URL_APPLICATION}/?zone={zone}"
    
    # Générer le QR Code contenant le lien URL
    img = qrcode.make(lien_complet)
    
    # Nom du fichier image
    nom_fichier = os.path.join(DOSSIER_SORTIE, f"QR_{zone.replace('&', 'et').replace(' ', '_')}.png")
    img.save(nom_fichier)
    
    print(f"✅ QR Code généré pour la zone '{zone}' -> Fichier : {nom_fichier}")

print(f"\n🎉 Les QR Codes prêts à être imprimés sont dans le dossier '{DOSSIER_SORTIE}' !")
print(f"📌 Ils pointent tous vers l'adresse : {URL_APPLICATION}")
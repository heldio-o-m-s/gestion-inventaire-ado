import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestion de Stock - QR", page_icon="📦", layout="centered")

st.title("📦 Gestion de Stock (Google Sheets)")

# Lien direct d'export CSV de votre Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ik2XHR1hLLFZ39aZqjLnukpYVOAaPrZ1/export?format=csv&gid=1937426268"

@st.cache_data(ttl=5)
def charger_donnees():
    return pd.read_csv(SHEET_URL)

try:
    df = charger_donnees()
    
    # Nettoyage pour garder uniquement les lignes valides
    if 'Code ID' in df.columns:
        df = df.dropna(subset=['Code ID'])

    operation = st.radio("Opération :", ["Mouvement de Stock (Entrée/Sortie)", "Consulter le Stock"], horizontal=True)

    if operation == "Mouvement de Stock (Entrée/Sortie)":
        type_mvt = st.selectbox("Type de mouvement :", ["SORTIE 🔴", "ENTRÉE 🟢"])
        
        cat_liste = ["Toutes les zones"] + list(df['Catégorie'].dropna().unique()) if 'Catégorie' in df.columns else ["Toutes les zones"]
        cat_choisie = st.selectbox("Zone / Catégorie :", cat_liste)
        
        if cat_choisie != "Toutes les zones":
            df_dispo = df[df['Catégorie'] == cat_choisie]
        else:
            df_dispo = df

        articles_dict = dict(zip(df_dispo['Code ID'].astype(str) + " - " + df_dispo['Article / Description'], df_dispo['Code ID']))
        article_selectionne = st.selectbox("Choisir l'article :", list(articles_dict.keys()))
        
        if article_selectionne:
            code_id = articles_dict[article_selectionne]
            ligne = df[df['Code ID'] == code_id].iloc[0]
            
            st.info(f"**Stock actuel :** {ligne['Qté en Stock']} | **Statut :** {ligne['État / Statut']}")
            
            quantite = st.number_input("Quantité :", min_value=1, step=1, value=1)
            
            if st.button("Valider la mise à jour"):
                st.success(f"Opération validée pour l'article ID : {code_id} (Quantité : {quantite})")

    else:
        st.subheader("📋 Liste des articles en stock")
        recherche = st.text_input("🔍 Rechercher un article ou un code :")
        if recherche:
            df_affiche = df[
                df['Article / Description'].astype(str).str.contains(recherche, case=False, na=False) | 
                df['Code ID'].astype(str).str.contains(recherche, case=False, na=False)
            ]
        else:
            df_affiche = df
            
        st.dataframe(df_affiche[['Code ID', 'Article / Description', 'Catégorie', 'Qté en Stock', 'État / Statut']], use_container_width=True)

except Exception as e:
    st.error(f"❌ Erreur de chargement : {e}")

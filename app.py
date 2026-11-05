import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Gestion de Stock - QR", page_icon="📦", layout="centered")

st.title("📦 Gestion de Stock (Google Sheets)")

# Connexion à Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5) # Rafraîchissement automatique toutes les 5 secondes
def charger_donnees():
    # Lit la feuille "Inventaire" de votre fichier Google Sheets
    return conn.read(worksheet="Inventaire", ttl=5)

try:
    df = charger_donnees()
    
    # Nettoyage minimal au cas où il y a des lignes vides au début
    df = df.dropna(subset=['Code ID'])

    operation = st.radio("Opération :", ["Mouvement de Stock (Entrée/Sortie)", "Consulter le Stock"], horizontal=True)

    if operation == "Mouvement de Stock (Entrée/Sortie)":
        type_mvt = st.selectbox("Type de mouvement :", ["SORTIE 🔴", "ENTRÉE 🟢"])
        
        # Zones / Catégories disponibles
        cat_liste = ["Toutes les zones"] + list(df['Catégorie'].dropna().unique())
        cat_choisie = st.selectbox("Zone / Catégorie :", cat_liste)
        
        if cat_choisie != "Toutes les zones":
            df_dispo = df[df['Catégorie'] == cat_choisie]
        else:
            df_dispo = df

        # Sélection de l'article
        articles_dict = dict(zip(df_dispo['Code ID'].astype(str) + " - " + df_dispo['Article / Description'], df_dispo['Code ID']))
        article_selectionne = st.selectbox("Choisir l'article :", list(articles_dict.keys()))
        
        if article_selectionne:
            code_id = articles_dict[article_selectionne]
            ligne = df[df['Code ID'] == code_id].iloc[0]
            
            st.info(f"**Stock actuel :** {ligne['Qté en Stock']} | **Statut :** {ligne['État / Statut']}")
            
            quantite = st.number_input("Quantité :", min_value=1, step=1, value=1)
            
            if st.button("Valider la mise à jour"):
                idx = df[df['Code ID'] == code_id].index[0]
                stock_actuel = int(df.loc[idx, 'Qté en Stock'])
                
                if "SORTIE" in type_mvt:
                    nouveau_stock = max(0, stock_actuel - quantite)
                else:
                    nouveau_stock = stock_actuel + quantite
                    
                df.loc[idx, 'Qté en Stock'] = nouveau_stock
                
                # Recalcul du statut automatique
                if nouveau_stock <= 0:
                    df.loc[idx, 'État / Statut'] = 'Épuisé'
                elif nouveau_stock <= 2:
                    df.loc[idx, 'État / Statut'] = 'Stock Bas'
                else:
                    df.loc[idx, 'État / Statut'] = 'En Stock'
                    
                # ÉCRITURE EN TEMPS RÉEL DANS VOTRE GOOGLE SHEETS
                conn.update(worksheet="Inventaire", data=df)
                st.cache_data.clear()
                
                st.success(f"✅ Google Sheets mis à jour ! Nouveau stock pour '{ligne['Article / Description']}' : **{nouveau_stock}**")
                st.rerun()

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
    st.error(f"❌ Erreur de connexion au Google Sheets : {e}")

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Inventaire QR", page_icon="📦", layout="centered")

FICHIER_EXCEL = "Tableau_Inventaire_Modele.xlsx"

# Fonction pour charger les données avec gestion d'erreur détaillée
@st.cache_data
def charger_donnees():
    # Ouvre le fichier et lit la feuille "Inventaire"
    return pd.read_excel(FICHIER_EXCEL, sheet_name="Inventaire", header=7)

st.title("📦 Gestion de Stock")

try:
    df = charger_donnees()
    st.success("Fichier Excel chargé avec succès !")
except Exception as e:
    st.error(f"❌ Erreur détaillée : {e}")
    st.stop()

# Choix de l'opération
operation = st.radio("Opération :", ["Mouvement de Stock (Entrée/Sortie)", "Consulter le Stock"], horizontal=True)

if operation == "Mouvement de Stock (Entrée/Sortie)":
    type_mvt = st.selectbox("Type de mouvement :", ["SORTIE 🔴", "ENTRÉE 🟢"])
    
    # Filtrer par catégorie
    cat_liste = ["Toutes les zones"] + list(df['Catégorie'].dropna().unique())
    cat_choisie = st.selectbox("Zone / Catégorie :", cat_liste)
    
    if cat_choisie != "Toutes les zones":
        df_dispo = df[df['Catégorie'] == cat_choisie]
    else:
        df_dispo = df

    # Sélection de l'article
    articles_dict = dict(zip(df_dispo['Code ID'] + " - " + df_dispo['Article / Description'], df_dispo['Code ID']))
    article_selectionne = st.selectbox("Choisir l'article :", list(articles_dict.keys()))
    
    if article_selectionne:
        code_id = articles_dict[article_selectionne]
        ligne = df[df['Code ID'] == code_id].iloc[0]
        
        st.info(f"**Stock actuel :** {ligne['Qté en Stock']} | **Statut :** {ligne['État / Statut']}")
        
        quantite = st.number_input("Quantité :", min_value=1, step=1, value=1)
        
        if st.button("Valider la mise à jour"):
            idx = df[df['Code ID'] == code_id].index[0]
            stock_actuel = df.loc[idx, 'Qté en Stock']
            
            if "SORTIE" in type_mvt:
                nouveau_stock = max(0, stock_actuel - quantite)
            else:
                nouveau_stock = stock_actuel + quantite
                
            df.loc[idx, 'Qté en Stock'] = nouveau_stock
            
            # Statut automatique
            if nouveau_stock <= 0:
                df.loc[idx, 'État / Statut'] = 'Épuisé'
            elif nouveau_stock <= 2:
                df.loc[idx, 'État / Statut'] = 'Stock Bas'
            else:
                df.loc[idx, 'État / Statut'] = 'En Stock'
                
            # Sauvegarde Excel
            df.to_excel(FICHIER_EXCEL, sheet_name="Inventaire", index=False)
            st.success(f"✅ Stock mis à jour ! Nouveau stock pour '{ligne['Article / Description']}' : **{nouveau_stock}**")
            st.rerun()

else:
    st.subheader("📋 Liste des articles en stock")
    recherche = st.text_input("🔍 Rechercher un article ou un code :")
    if recherche:
        df_affiche = df[df['Article / Description'].str.contains(recherche, case=False, na=False) | df['Code ID'].str.contains(recherche, case=False, na=False)]
    else:
        df_affiche = df
        
    st.dataframe(df_affiche[['Code ID', 'Article / Description', 'Catégorie', 'Qté en Stock', 'État / Statut']], use_container_width=True)

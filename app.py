import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# -------------------------
# CONFIGURATION DE LA PAGE
# -------------------------
st.set_page_config(page_title="MailShield Pro", page_icon="🛡️", layout="wide")

# Masquer la sidebar et appliquer la police Poppins
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none !important;}
[data-testid="stSidebarNav"] {display: none !important;}
@import url('https://googleapis.com');
html, body, div, p, h1, h2, h3, h4, h5, h6, span {
    font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# CONFIGURATION PAYPAL (À REMPLIR PLUS TARD)
# -------------------------
PAYPAL_CLIENT_ID = "DEMO"  
PAYPAL_PLAN_ID = "DEMO"    

# -------------------------
# GESTION DE L'ACCÈS (SESSION STATE)
# -------------------------
if "est_abonne" not in st.session_state:
    st.session_state.est_abonne = False

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except:
    API_KEY = ""

# -------------------------
# INTERFACE SÉCURISÉE
# -------------------------
st.title("🛡️ MailShield Pro")
st.subheader("Générez des e-mails professionnels de négociation, relance et gestion de litiges sans aucun stress.")

# CAS 1 : L'UTILISATEUR N'A PAS PAYÉ
if not st.session_state.est_abonne:
    st.warning("🔒 Cette application est réservée aux membres de la version Premium.")
    
    col_offre, col_connexion = st.columns(2, gap="large")
    
    with col_offre:
        st.subheader("🚀 Accès Illimité pour 20 $/mois")
        st.write("Ne laissez plus le stress gâcher vos relations professionnelles ou personnelles. Laissez l'IA rédiger vos e-mails délicats avec fermeté et diplomatie.")
        st.write("Le paiement est entièrement sécurisé par **PayPal**.")
        
        if PAYPAL_CLIENT_ID == "DEMO":
            paypal_html = """
            <a href="https://paypal.com" target="_blank" style="text-decoration: none;">
                <div style="background-color: #ffc439; color: #003087; text-align: center; 
                            padding: 12px; font-family: Arial, sans-serif; font-weight: bold; 
                            border-radius: 4px; max-width: 300px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    🟨 S'abonner avec PayPal (Démo)
                </div>
            </a>
            """
        else:
            paypal_html = f"""
            <div id="paypal-button-container-fixed" style="max-width: 350px; margin-top: 20px;"></div>
            <script src="https://paypal.com/sdk/js?client-id={PAYPAL_CLIENT_ID}&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
            <script>
              paypal.Buttons({{
                  style: {{ shape: 'rect', color: 'gold', layout: 'vertical', label: 'subscribe' }},
                  createSubscription: function(data, actions) {{
                    return actions.subscription.create({{ 'plan_id': '{PAYPAL_PLAN_ID}' }});
                  }},
                  onApprove: function(data, actions) {{
                    alert('Abonnement réussi ! ID : ' + data.subscriptionID);
                  }}
              }}).render('#paypal-button-container-fixed');
            </script>
            """
        
        components.html(paypal_html, height=150, scrolling=False)
        
    with col_connexion:
        st.subheader("🔑 Déjà abonné ?")
        st.write("Connectez-vous pour activer vos accès.")
        email = st.text_input("Adresse e-mail")
        mot_de_passe = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter", use_container_width=True):
            if email == "test@client.com" and mot_de_passe == "access20":
                st.session_state.est_abonne = True
                st.success("Accès accordé !")
                st.rerun()
            else:
                st.error("Identifiants incorrects ou abonnement PayPal inactif.")

# CAS 2 : L'UTILISATEUR EST ABONNÉ -> ACCÈS COMPLET
else:
    st.write("✨ **Bienvenue dans votre espace Premium.** Votre bouclier e-mail est activé.")
    if st.button("🚪 Se déconnecter", key="logout"):
        st.session_state.est_abonne = False
        st.rerun()
        
    st.write("---")

    with st.container(border=True):
        col_inputs, col_options = st.columns(2)
        
        with col_inputs:
            situation = st.text_area(
                "Décrivez la situation en quelques mots bruts :", 
                placeholder="Ex: Mon client me doit 1200$ depuis un mois. Il ne répond plus à mes appels alors que le travail est livré."
            )
            details_importants = st.text_input(
                "Détails clés (Optionnel) :", 
                placeholder="Ex: Facture N°2026-04, projet fini le 12 avril."
            )
            
        with col_options:
            type_conflit = st.selectbox("Type de message", [
                "💰 Relance de paiement / Facture impayée",
                "🛑 Refuser une demande (Baisse de prix, délai trop court)",
                "⚖️ Réclamation officielle / Litige fournisseur",
                "📈 Négociation (Demande d'augmentation, réévaluation de contrat)",
                "🤝 Rupture de collaboration (Mettre fin à un contrat proprement)"
            ])
            
            ton = st.selectbox("Niveau de fermeté", [
                "Diplomate & Courtois (Première relance / Conserver la relation)",
                "Ferme & Professionnel (Rappel des règles et des faits)",
                "Strict & Juridique (Dernier avertissement avant poursuites)"
            ])

        generer = st.button("🛡️ Générer l'E-mail Parfait", use_container_width=True)

    if generer:
        if not API_KEY:
            st.error("⚠️ Erreur : La clé GROQ_API_KEY est manquante dans les Secrets du serveur.")
        elif not situation:
            st.error("⚠️ Veuillez décrire brièvement votre situation.")
        else:
            with st.spinner("L'IA de négociation formule votre message..."):
                try:
                    client = Groq(api_key=API_KEY)
                    
                    prompt_systeme = """Tu es un expert mondial en communication de crise, négociation commerciale et psychologie d'entreprise.
                    Ton but est d'écrire des e-mails parfaits pour résoudre des conflits, obtenir des paiements ou fixer des limites strictes, sans jamais paraître agressif mais en restant redoutablement efficace.
                    
                    Tu devez fournir deux choses dans votre réponse :
                    1. **Objet :** Un titre d'e-mail clair, percutant et professionnel.
                    2. **Corps de l'e-mail :** Le message complet avec des crochets [comme ceci] pour les éléments que l'utilisateur doit remplacer (ex: [Votre Nom], [Date]).
                    
                    Respecte scrupuleusement le ton demandé. Ne fais aucune introduction ni conclusion amicale au début ou à la fin de ta réponse, écris directement l'e-mail."""

                    prompt_utilisateur = f"""
                    Situation brute : {situation}
                    Détails importants : {details_importants}
                    Type de conflit : {type_conflit}
                    Niveau de fermeté demandé : {ton}
                    """

                    reponse = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": prompt_systeme},
                            {"role": "user", "content": prompt_utilisateur}
                        ],
                        temperature=0.6
                    )
                    
                    email_genere = reponse.choices[0].message.content
                    st.success("✨ Votre e-mail ultra-professionnel est prêt !")
                    
                    st.markdown(email_genere)
                    
                    st.text_area("Copier le texte brut :", value=email_genere, height=300)

                except Exception as e:
                    st.error(f"Erreur technique Groq : {str(e)}")

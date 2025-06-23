import streamlit as st

st.set_page_config(page_title="🏠 Home - Tennis Elo", layout="wide")

st.title("🎾 Torneo Singolo")
st.markdown("---")

st.markdown("""
Benvenuto nel portale ufficiale del torneo !

Questa dashboard ti permette di seguire l'andamento del torneo, visualizzare classifiche aggiornate, analizzare le performance dei giocatori e consultare il regolamento.

## 📂 Sezioni principali

### 🏆 [Torneo](Torneo)
Accedi a tutti i dati del torneo:
- Visualizza i risultati dei turni giocati
- Consulta la classifica aggiornata in tempo reale
- Esplora i punteggi 

👉 Vai alla pagina **[Torneo](Torneo)**

---

### 📜 [Regolamento](Regolamento)
Scopri come funziona il torneo:
- Regole del formato tutti contro tutti
- Sistema a punti per ogni partita
- Modalità di qualificazione alla fase finale
- Libertà di scelta di **impianto** e **superficie**

👉 Leggi il **[Regolamento completo](Regolamento)**

---

Puoi utilizzare il menu sulla sinistra per navigare tra le sezioni.
""")

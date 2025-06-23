import streamlit as st

## 🔄 Struttura del torneo
st.header("🔄 Struttura del torneo")
st.markdown("""
- Il torneo si svolge con una **formula all'italiana**, ovvero tutti i giocatori si sfidano tra loro una volta (7 partite ciascuno).
- Ogni **turno** corrisponde a una singola partita tra due giocatori, fino al completamento di tutte le 7 partite previste per ogni partecipante.
- Al termine della fase a gironi, si qualificano i primi 4 giocatori in classifica.
  - Le semifinali vedono sfidarsi:  
    🔹 1° classificato contro 4° classificato  
    🔹 2° classificato contro 3° classificato  
  - I vincitori delle semifinali si sfidano nella finale per il titolo.

- **Luogo e superficie delle partite**:  
  I giocatori possono scegliere liberamente dove giocare, su qualsiasi superficie e in qualsiasi impianto.  
  Si accorderanno di volta in volta per definire sede e condizioni delle partite.
""")

## 🧮 Come funziona il sistema a punti
st.header("🧮 Come funziona il sistema a punti")
st.markdown("""
- In ogni partita si assegnano punti ai giocatori in base al risultato dei set:

| Risultato partita | Punti vincitore | Punti sconfitto |
|-------------------|-----------------|-----------------|
| Vittoria 2-0      | 3               | 0               |
| Vittoria 2-1      | 2               | 1               |

- I punti determinano la classifica aggregata dei giocatori durante il torneo.
- Questo sistema premia chi vince con punteggi netti e dà punti anche agli sconfitti che riescono a vincere almeno un set.

---

""")

## 🧪 Esempi concreti
st.subheader("📊 Esempi concreti")

st.markdown("""
#### ✅ Esempio 1: Vittoria 2-0
- Giocatore A batte Giocatore B con punteggio 6-3, 6-2  
👉 A ottiene 3 punti, B 0 punti

#### ✅ Esempio 2: Vittoria 2-1
- Giocatore A batte Giocatore B con punteggio 6-4, 3-6, 7-6  
👉 A ottiene 2 punti, B 1 punto

#### ✅ Esempio 3: Sconfitta 1-2
- Giocatore A perde contro Giocatore B 4-6, 7-5, 3-6  
👉 A ottiene 1 punto, B 2 punti
""")

st.markdown("---")
st.success("Usa la barra laterale per iniziare: seleziona un Turno per esplorare i dati.")

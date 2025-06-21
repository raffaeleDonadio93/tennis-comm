import streamlit as st

st.set_page_config(page_title="🏠 Home - Tennis Elo", layout="wide")

st.title("🎾 Benvenuto nella Tennis Elo Dashboard")
st.markdown("---")

## 🔄 Struttura del torneo
st.header("🔄 Struttura del torneo")
st.markdown("""
- **Round**: rappresentano le fasi principali del torneo (es. `round_1`, `round_2`, ecc.).
- **Turni**: ogni round contiene uno o più turni (es. `turno_1`, `turno_2`, ecc.), ognuno con un set di partite.
""")

## 🧮 Come funziona il sistema Elo
st.header("🧮 Come funziona il sistema Elo")
st.markdown("""
- Tutti i giocatori partono con un **punteggio iniziale di 1500**.
- Dopo ogni partita, il sistema aggiorna i punteggi in base a:
    - il risultato della partita (vittoria/sconfitta)
    - la forza relativa dell'avversario (cioè il suo Elo attuale)
- Il sistema premia le **vittorie contro avversari forti** e penalizza meno le sconfitte contro avversari più forti.

### 📐 Formula usata:
> **Elo_nuovo = Elo_vecchio + K × (Risultato - Probabilità_prevista)**

- `K` è un coefficiente fisso (es. `32`)
- La **Probabilità prevista** è calcolata in base alla differenza tra i punteggi dei due giocatori

---
""")

## 🧪 Esempi concreti
st.subheader("📊 Esempi concreti")

st.markdown("""
#### ✅ Esempio 1: Vittoria contro avversario più forte
- **Giocatore A (1450)** vs **Giocatore B (1550)**
- Vince il giocatore A

👉 Il sistema considerava **molto probabile** la vittoria di B.  
👉 A ottiene **un grande incremento di Elo**, mentre B perde molti punti.

#### ✅ Esempio 2: Vittoria contro avversario più debole
- **Giocatore A (1600)** vs **Giocatore B (1400)**
- Vince il giocatore A

👉 Era un risultato atteso.  
👉 A guadagna **pochi punti Elo**, B ne perde pochi.

#### ⚖️ Esempio 3: Pareggio o vittoria inattesa
- Il sistema Elo tiene conto della **sorpresa del risultato**.
- Una **vittoria inaspettata** genera uno **scarto maggiore** nei punteggi.
""")

st.markdown("---")
st.success("Usa la barra laterale per iniziare: seleziona un Round e un Turno per esplorare i dati Elo.")

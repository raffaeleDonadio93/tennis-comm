import streamlit as st
from streamlit.components.v1 import html
from library import *

# -- Streamlit app --

st.set_page_config(page_title="🎾 Tennis Elo Dashboard", layout="wide")


#rounds = get_rounds()
#round_selected = st.selectbox("Seleziona Round", rounds)
round_selected="round_1"
turni = get_turni(BASE_DIR / round_selected)
turno_selected = st.selectbox("Seleziona Turno", turni)

df_turno = load_turno_csv(round_selected, turno_selected)

if df_turno is None:
    st.error("Dati turno non trovati.")
    st.stop()

# Dividi partite già giocate da quelle future
df_giocate = df_turno[df_turno["Vincitore"].notna() & (df_turno["Vincitore"] != "")]
df_future = df_turno[df_turno["Vincitore"].isna() | (df_turno["Vincitore"] == "")]

tab1, tab2, tab3, tab4 = st.tabs(["Partite Giocate", "Prossime Partite", "Classifica","Fase Finale Provvisoria"])

with tab1:

    if df_giocate.empty:
        st.info("Nessuna partita giocata ancora in questo turno.")
    else:
        for _, row in df_giocate.iterrows():
            vincitore = row['Vincitore']
            p1, p2 = row['Player 1'], row['Player 2']

            # Evidenzia il vincitore
            style_p1 = (
                "font-weight: 800; color: #2e7d32;"  # verde vittoria
                if p1 == vincitore else
                "font-weight: 600; color: #b71c1c;"  # rosso sconfitta
            )

            style_p2 = (
                "font-weight: 800; color: #2e7d32;"
                if p2 == vincitore else
                "font-weight: 600; color: #b71c1c;"
            )

            # Set
            s1 = row['Set 1'] if pd.notna(row['Set 1']) else "-"
            s2 = row['Set 2'] if pd.notna(row['Set 2']) else "-"
            s3 = row['Set 3'] if pd.notna(row['Set 3']) else "-"

            sets = [estrai_punteggio(row[f'Set {i}']) for i in range(1, 4)]

            # Conta i set vinti da ciascun giocatore
            set_vinti_p1 = sum(1 for s1, s2 in sets if s1 is not None and s2 is not None and s1 > s2)
            set_vinti_p2 = sum(1 for s1, s2 in sets if s1 is not None and s2 is not None and s2 > s1)

            # Calcolo dei punti
            if set_vinti_p1 == 2 and set_vinti_p2 == 0:
                punti_p1, punti_p2 = 3, 0
            elif set_vinti_p1 == 2 and set_vinti_p2 == 1:
                punti_p1, punti_p2 = 2, 1
            elif set_vinti_p1 == 1 and set_vinti_p2 == 2:
                punti_p1, punti_p2 = 1, 2
            elif set_vinti_p1 == 0 and set_vinti_p2 == 2:
                punti_p1, punti_p2 = 0, 3
            else:
                punti_p1 = punti_p2 = "-"

            # Format set linee
            set_line_p1 = " ".join(str(s[0]) if s[0] is not None else "-" for s in sets)
            set_line_p2 = " ".join(str(s[1]) if s[1] is not None else "-" for s in sets)

            html_card = f"""
              <div style="width: 100%; display: flex; justify-content: flex-start;"> 
                  <div style="
                      border-radius: 10px;
                      padding: 16px 20px;
                      margin-bottom: 14px;
                      background: linear-gradient(135deg, #fff5b7, #fbd72b);
                      box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
                      font-family: 'Segoe UI', sans-serif;
                      width: 100%;
                      max-width: 500px;
                  ">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 15px; color: #777;">
                      <div>📍 <strong>{row['Luogo']}</strong></div>
                      <div>{row['Data']}</div>
                      <div>{row['Superficie']}</div>
                    </div>
                
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                      <div style="text-align: left;">
                        <div style="{style_p1} font-size: 18px; margin-bottom: 6px;">{p1}</div>
                        <div style="font-size: 16px; margin-bottom: 10px;">{set_line_p1}</div>
                
                        <div style="{style_p2} font-size: 18px; margin-bottom: 6px;">{p2}</div>
                        <div style="font-size: 16px;">{set_line_p2}</div>
                      </div>
                
                      <div style="text-align: right; font-size: 16px; font-weight: bold;">
                        <div style="margin-bottom: 26px;">{punti_p1} pt</div>
                        <div>{punti_p2} pt</div>
                      </div>
                    </div>
                  </div>
                </div>
            """
            html(html_card, height=200)
with tab2:

    if df_future.empty:
        st.info("Non ci sono altre partite in programma per questo turno.")
    else:

        cols = st.columns(len(df_future))

        for idx, (i, row) in enumerate(df_future.iterrows()):
            with cols[idx]:
                st.markdown(
                    f"""
                   <div style="
                  border-radius: 22px;
                  padding: 16px 20px;
                  margin-bottom: 14px;
                  background: linear-gradient(135deg, #fff5b7, #fbd72b);
                  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
                  font-family: 'Segoe UI', sans-serif;
                  width: 100%;
                  max-width: 420px;
              ">
                        <p style="font-weight:bold; font-size:26px;">
                            {row['Player 1']}<br>
                            <span style="font-size:18px; color:#555;">vs</span><br>
                            {row['Player 2']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
with tab3:
    # Calcola la classifica
    df_classifica = calcola_classifica_punti(round_selected, turno_selected)

    # Layout a due colonne: sinistra (classifica) e destra (vuota o per altri contenuti)
    col_sx, col_dx = st.columns([1, 2])  # sinistra stretta, destra più ampia

    with col_sx:

        for idx, row in df_classifica.iterrows():
            posizione = idx + 1
            giocatore = row["Giocatore"]
            punti = row["Punti"]
            partite = row["Partite Giocate"]

            st.markdown(f"""
            <div style="
                border-radius: 16px;
                padding: 16px 20px;
                margin-bottom: 16px;
                background: linear-gradient(135deg, #fff5b7, #fbd72b);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                font-family: 'Segoe UI', sans-serif;
            ">
                <div style="font-size: 18px; font-weight: 700; color: #222;">🔝 {posizione}. {giocatore}</div>
                <div style="margin-top: 6px; font-size: 15px; color: #444;">🏅 <strong>Punti:</strong> {punti}</div>
                <div style="font-size: 15px; color: #666;">🎾 <strong>Partite:</strong> {partite}</div>
            </div>
            """, unsafe_allow_html=True)

    # La col_dx resta vuota o può contenere altri componenti (grafici, partite, etc.)

with tab4:
    df_classifica = calcola_classifica_punti(round_selected, turno_selected)

    if len(df_classifica) >= 4:
        primo = df_classifica.loc[0, "Giocatore"]
        secondo = df_classifica.loc[1, "Giocatore"]
        terzo = df_classifica.loc[2, "Giocatore"]
        quarto = df_classifica.loc[3, "Giocatore"]

        semifinals = [
            {"player1": primo, "player2": quarto},
            {"player1": secondo, "player2": terzo},
        ]


        def match_card(player1, player2, title=""):
            return f"""
                <div style="
                    border-radius: 18px;
                    padding: 16px 20px;
                    margin-bottom: 14px;
                    background: linear-gradient(135deg, #fff5b7, #fbd72b);
                    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
                    font-family: 'Segoe UI', sans-serif;
                    width: 100%;
                    text-align: center;
                ">
                    <h4 style="margin-bottom: 10px; color: #333;">{title}</h4>
                    <p style="font-size: 22px; font-weight: bold; color: #2c3e50;">{player1}</p>
                    <p style="font-size: 18px; color: #999;">vs</p>
                    <p style="font-size: 22px; font-weight: bold; color: #2c3e50;">{player2}</p>
                </div>
                """


        col1, col2 = st.columns(2)
        with col1:
            st.markdown(match_card(semifinals[0]["player1"], semifinals[0]["player2"], "Semifinale 1"),
                        unsafe_allow_html=True)
        with col2:
            st.markdown(match_card(semifinals[1]["player1"], semifinals[1]["player2"], "Semifinale 2"),
                        unsafe_allow_html=True)

        st.markdown(match_card("Vincente SF1", "Vincente SF2", "Finale"), unsafe_allow_html=True)

    else:
        st.info("Aspetta che siano giocate almeno 2 partite nel turno corrente per mostrare le semifinali.")
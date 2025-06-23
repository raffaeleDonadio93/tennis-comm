from pathlib import Path

import pandas as pd

BASE_DIR = Path("operations/output/rounds")


def get_rounds():
    rounds = sorted([d.name for d in BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("round")])
    return rounds

def get_turni(round_dir):
    turni = sorted([f.stem for f in round_dir.glob("turno_*.csv")])
    return turni

def load_turno_csv(round_name, turno_name):
    filepath = BASE_DIR / round_name / f"{turno_name}.csv"
    if not filepath.exists():
        return None
    df = pd.read_csv(filepath)
    for col in ["Elo iniziale 1", "Elo iniziale 2", "Elo 1 Finale", "Elo 2 Finale"]:
        if col not in df.columns:
            if "iniziale" in col:
                df[col] = 1500.0
            else:
                df[col] = pd.NA
    return df

def estrai_giocatori(df):
    return sorted(set(df["Player 1"]).union(df["Player 2"]))

def estrai_punteggio(set_str):
    if pd.isna(set_str) or '-' not in set_str:
        return (None, None)
    try:
        main = set_str.split('-')
        s1 = int(main[0].split('(')[0])
        s2 = int(main[1].split('(')[0])
        return s1, s2
    except:
        return (None, None)

def calcola_classifica_punti(round_name, turno_name):
    round_num = int(round_name.split("_")[1])
    turno_num = int(turno_name.split("_")[1])

    rounds = get_rounds()
    df_all = pd.DataFrame()

    for r in rounds:
        r_num = int(r.split("_")[1])
        if r_num > round_num:
            break
        round_path = BASE_DIR / r
        turni = get_turni(round_path)

        for t in turni:
            t_num = int(t.split("_")[1])
            if r_num == round_num and t_num > turno_num:
                break
            df_turno = load_turno_csv(r, t)
            if df_turno is not None:
                df_all = pd.concat([df_all, df_turno], ignore_index=True)

    # Solo partite giocate
    df_giocate = df_all[df_all["Vincitore"].notna() & (df_all["Vincitore"] != "")]

    punti = {}
    partite_giocate = {}

    for _, row in df_giocate.iterrows():
        p1 = row["Player 1"]
        p2 = row["Player 2"]

        # Estrai set
        def get_set_score(set_str):
            try:
                s1, s2 = set_str.split('-')
                s1 = int(s1.split('(')[0])
                s2 = int(s2.split('(')[0])
                return s1, s2
            except:
                return None, None

        sets = [get_set_score(row[f"Set {i}"]) for i in range(1, 4)]
        s1_wins = sum(1 for s1, s2 in sets if s1 is not None and s2 is not None and s1 > s2)
        s2_wins = sum(1 for s1, s2 in sets if s1 is not None and s2 is not None and s2 > s1)

        # Assegna punti
        if s1_wins == 2 and s2_wins == 0:
            punti_p1, punti_p2 = 3, 0
        elif s1_wins == 2 and s2_wins == 1:
            punti_p1, punti_p2 = 2, 1
        elif s1_wins == 1 and s2_wins == 2:
            punti_p1, punti_p2 = 1, 2
        elif s1_wins == 0 and s2_wins == 2:
            punti_p1, punti_p2 = 0, 3
        else:
            continue  # Partita incompleta o dati mancanti

        for player, punti_da_aggiungere in [(p1, punti_p1), (p2, punti_p2)]:
            punti[player] = punti.get(player, 0) + punti_da_aggiungere
            partite_giocate[player] = partite_giocate.get(player, 0) + 1

    df_classifica = pd.DataFrame({
        "Giocatore": list(punti.keys()),
        "Punti": list(punti.values()),
        "Partite Giocate": [partite_giocate[g] for g in punti.keys()]
    }).sort_values(by="Punti", ascending=False).reset_index(drop=True)

    return df_classifica
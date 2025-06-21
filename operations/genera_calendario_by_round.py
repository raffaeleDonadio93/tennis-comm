import pandas as pd

def round_robin_schedule(players, num_rounds=1):
    """
    Genera un calendario round-robin con turni (giornate) per i match.
    Ogni turno ha partite senza giocatori duplicati.
    Ripete il ciclo per num_rounds volte (rounds).
    """
    if len(players) % 2 != 0:
        players.append("BYE")  # Se dispari, aggiunge un bye

    n = len(players)
    half = n // 2
    schedule = []

    for round_num in range(1, num_rounds + 1):
        # crea lista rotante (circle method)
        rotation = players[1:]
        for turno in range(n - 1):
            pairs = []
            left = players[0]
            right = rotation[-1]
            pairs.append((left, right))

            for i in range(half - 1):
                pairs.append((rotation[i], rotation[-i - 2]))

            # aggiungi partite del turno al calendario
            match_id_base = (round_num - 1) * (n - 1) * half
            for idx, (p1, p2) in enumerate(pairs):
                if p1 != "BYE" and p2 != "BYE":  # salta bye
                    match_id = match_id_base + turno * half + idx + 1
                    schedule.append({
                        "MatchID": match_id,
                        "Round": round_num,
                        "Turno": turno + 1,
                        "Player 1": p1,
                        "Player 2": p2
                    })

            # ruota la lista per il turno successivo
            rotation = [rotation[-1]] + rotation[:-1]

    return pd.DataFrame(schedule)

# Carica giocatori
df_players = pd.read_csv("input/players.csv")
players = df_players["Nome"].tolist()

# Numero di round (ripetizioni del torneo)
num_rounds = 3

df_matches = round_robin_schedule(players, num_rounds)

df_matches.to_csv("output/calendario.csv", index=False)
print("Calendario round-robin con turni e round salvato in output/calendario.csv")

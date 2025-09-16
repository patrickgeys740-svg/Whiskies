# verwerking/data_loader.py

from typing import Tuple
import os

# ✅ Maandenlijst (voor consistentie)
maanden = [
    "September", "Oktober", "November", "December",
    "Januari", "Februari", "Maart", "April",
    "Mei", "Juni"
]

def score(lijn: str):
    """Verwerk 1 regel uit een CSV-bestand tot (naam, puntenlijst, damesaantal)"""
    if ";" in lijn:
        kolommen = lijn.split(";")
    else:
        kolommen = lijn.split(",")

    if len(kolommen) < 20:
        return "geen lid"

    wie = kolommen[0]
    punten_str = kolommen[2:6]
    punten = []

    for p in punten_str:
        try:
            if len(p) > 0 and p.strip().isdigit():
                punten.append(int(p))
            else:
                punten.append(0)
        except Exception:
            print(wie, punten_str)
            print("fout:", lijn)
            input("stop")

    # Verplaats 4e score naar voren als één van de eerste drie 0 is
    if punten[3] != 0 and 0 in punten[0:3]:
        p = punten.index(0)
        punten[p] = punten[3]
        punten[3] = 0

    try:
        dames = sum([int(p.strip()) for p in kolommen[16:20] if len(p.strip()) > 0])
        if len(wie) > 0 and wie[0].upper() != "Z":
            return wie, punten, dames
        else:
            return "geen lid"
    except Exception as e:
        print("dames", lijn)
        return "geen lid"


def verwerk(bestandsnaam: str) -> Tuple[dict, dict]:
    """Leest één CSV-bestand in en retourneert:
    - scores_maand: naam -> scores
    - dames_maand: naam -> aantal dames"""
    scores_maand = {}
    dames_maand = {}

    with open(bestandsnaam, encoding='utf-8') as invoer:
        invoer.readline()  # eerste lijn overslaan
        invoer.readline()  # tweede lijn overslaan
        for lijn in invoer:
            tup = score(lijn)
            try:
                if isinstance(tup, tuple) and len(tup) == 3:
                    wie, punten, dames = tup
                    if len(wie) > 2:
                        # vervang é door _eacute
                        p = wie.find("é")
                        if p >= 0:
                            wie = wie.replace(wie[p:p+1], "_eacute")
                        scores_maand[wie] = punten
                        dames_maand[wie] = dames
            except Exception:
                print("verwerk:", lijn.strip())
                print(tup)
    return scores_maand, dames_maand


def tel_punten(uitslagen: list) -> int:
    """Telt het aantal > 0 scores in een lijst van lijsten"""
    tel = 0
    for punten in uitslagen:
        for p in punten:
            if p > 0:
                tel += 1
    return tel


def verwerk_klassement(jaar: str, laatste_maand: int) -> Tuple[dict, dict]:
    """Verwerkt alle CSV-bestanden tot en met 'laatste_maand' voor opgegeven jaar."""
    maandelijks = {}
    dames = {}
    for i in range(laatste_maand):
        maand = maanden[i]
        pad = os.path.join("data", jaar, f"{maand}.csv")
        scores_maand, dames_maand = verwerk(pad)

        for wie, punten in scores_maand.items():
            if wie not in maandelijks:
                maandelijks[wie] = []
                dames[wie] = []
                for _ in range(i):
                    maandelijks[wie].append([0, 0, 0, 0])
                    dames[wie].append(0)

            gespeeld = tel_punten(maandelijks[wie])
            if gespeeld < 30:
                aantal = min(4, 30 - gespeeld)
                maandelijks[wie].append(punten[0:aantal])
            dames[wie].append(dames_maand[wie])
    return maandelijks, dames

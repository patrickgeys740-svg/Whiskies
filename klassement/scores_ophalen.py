# scores_ophalen.py
# Maakt data/<jaar>/<Maand>.csv vanuit een Excel .xlsm (sheet 'samen')

import os
import sys
import argparse
from typing import Optional

# Vereist: pip install pandas openpyxl
try:
    import pandas as pd
except Exception:
    print("Pandas ontbreekt. Installeer met: pip install pandas")
    sys.exit(1)

try:
    import openpyxl  # noqa: F401
except Exception:
    print("openpyxl ontbreekt. Installeer met: pip install openpyxl")
    sys.exit(1)

SHEET_NAAM = "samen"
MAX_RIJEN = 55
MAANDEN_12 = [
    "Januari", "Februari", "Maart", "April", "Mei", "Juni",
    "Juli", "Augustus", "September", "Oktober", "November", "December"
]

def project_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))

def vind_xlsm(explicit: Optional[str] = None) -> str:
    """Zoek een .xlsm bestand.
    - Als explicit pad is opgegeven, gebruik dat.
    - Anders: zoek in projectroot en 1 map hoger op '*whis*.xlsm' (dekt 'WHisloting.xlsm')."""
    if explicit:
        p = os.path.abspath(explicit)
        if os.path.isfile(p):
            return p
        print(f"[XLSM] Opgegeven bestand niet gevonden: {p}")
        sys.exit(1)

    roots = [project_root(), os.path.dirname(project_root())]
    kandidaten = []
    for root in roots:
        try:
            for naam in os.listdir(root):
                if naam.lower().endswith(".xlsm") and "whis" in naam.lower():
                    kandidaten.append(os.path.join(root, naam))
        except Exception:
            pass

    if not kandidaten:
        print(f"[XLSM] Geen .xlsm gevonden in {roots}. "
              f"Zet je Excel (bv. 'WHisloting.xlsm') in de projectmap of één niveau hoger, "
              f"of gebruik --xlsm PAD.")
        sys.exit(1)

    # kies de meest recente
    kandidaten.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return kandidaten[0]

def lees_sheet(xlsm_pad: str) -> pd.DataFrame:
    try:
        return pd.read_excel(xlsm_pad, sheet_name=SHEET_NAAM, engine="openpyxl")
    except ValueError as e:
        # Toon beschikbare sheets
        try:
            xl = pd.ExcelFile(xlsm_pad, engine="openpyxl")
            print(f"[XLSM] Sheet '{SHEET_NAAM}' niet gevonden. Beschikbare sheets: {xl.sheet_names}")
        except Exception:
            pass
        print(f"[XLSM] Fout bij laden van sheet '{SHEET_NAAM}': {e}")
        sys.exit(1)

def bepaal_maandnaam(df: pd.DataFrame) -> str:
    """Verwacht maandnummer (1..12) in cel [0,0]."""
    try:
        cel = df.iloc[0, 0]
        idx = int(cel)
        if not (1 <= idx <= 12):
            raise ValueError
        return MAANDEN_12[idx - 1]
    except Exception:
        print(f"[DATA] Ongeldige maandwaarde in cel [1,1]: {df.iloc[0,0]!r} (verwacht integer 1..12)")
        sys.exit(1)

def output_pad(jaar: str, maand: str) -> str:
    out_dir = os.path.join(project_root(), "data", jaar)
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, f"{maand}.csv")

def main():
    parser = argparse.ArgumentParser(description="Exporteer CSV uit WHisloting .xlsm")
    parser.add_argument("--jaar", help="Competitiejaar, bv. 2026")
    parser.add_argument("--xlsm", help="Pad naar Excel .xlsm")
    args = parser.parse_args()

    jaar = args.jaar or (input("Welk competitiejaar? (bv. 2026): ").strip() or "2026")
    if not jaar.isdigit():
        print(f"[CLI] Ongeldig jaar: {jaar}")
        sys.exit(1)

    xlsm = vind_xlsm(args.xlsm)
    print(f"[XLSM] Gekozen bestand: {xlsm}")

    df = lees_sheet(xlsm)
    print(f"[XLSM] Sheet '{SHEET_NAAM}' ingeladen. Vorm: {df.shape}")

    maand = bepaal_maandnaam(df)
    print(f"[DATA] Gevonden maand: {maand}")

    csv_pad = output_pad(jaar, maand)
    subset = df.iloc[0:MAX_RIJEN, :]
    subset.to_csv(csv_pad, index=False, encoding="utf-8")
    print(f"[OK] Geschreven: {csv_pad}")

if __name__ == "__main__":
    main()

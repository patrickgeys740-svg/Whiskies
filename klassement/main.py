# main.py
#Geschreven door Patrick, 14 september 2025
import os
import sys
import logging
from glob import glob

from verwerking.data_loader import verwerk_klassement
from html_generator.generator import maak_html, maak_controle_bestand
from pdf_exporter.pdf import maak_pdf, wkhtmltopdf_available

# Configuratie
JAAR = "2025"
DATADIR = os.path.join("data", JAAR)
HTMLDIR = os.path.join("output", JAAR, "html")
PDFDIR = os.path.join("output", JAAR, "pdf")
# bovenaan in main.py
BASE = os.path.dirname(os.path.abspath(__file__))

def data_dir(jaar: str) -> str:
    return os.path.join(BASE, "data", jaar)

def out_html_dir(jaar: str) -> str:
    return os.path.join(BASE, "output", jaar, "html")

def out_pdf_dir(jaar: str) -> str:
    return os.path.join(BASE, "output", jaar, "pdf")

def hulp_file(name: str) -> str:
    return os.path.join(BASE, "hulp", name)


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def detecteer_maanden() -> int:
    """Telt het aantal beschikbare .csv-bestanden in de datamap."""
    if not os.path.exists(DATADIR):
        logging.error(f"Map met data voor {JAAR} bestaat niet: {DATADIR}")
        sys.exit(1)
    bestanden = glob(os.path.join(DATADIR, "*.csv"))
    return len(bestanden)

def zorg_voor_outputmappen():
    os.makedirs(HTMLDIR, exist_ok=True)
    os.makedirs(PDFDIR, exist_ok=True)

def main():
    logging.info(f"Start verwerking voor jaar {JAAR}")
    
    pdf_gewenst = input("Wil je ook PDF's genereren? (Ja/Nee): ").strip().lower() != "nee"
    if pdf_gewenst and not wkhtmltopdf_available():
        logging.warning("wkhtmltopdf is niet gevonden. PDF-generatie wordt overgeslagen.")
        pdf_gewenst = False

    aantal_maanden = detecteer_maanden()
    logging.info(f"{aantal_maanden} maand(en) gevonden in {DATADIR}")

    zorg_voor_outputmappen()

    for i in range(aantal_maanden):
        maand_nr = i + 1
        logging.info(f"HTML genereren voor maand {maand_nr}")
        maak_html(JAAR, maand_nr)
        if pdf_gewenst:
            # Hier gebruiken we maandnaam in de filename (later beschikbaar via helper)
            from verwerking.helpers import maanden
            maand = maanden[i]
            html_file = os.path.join(HTMLDIR, f"{maand}.html")
            maak_pdf(html_file)

    # Controle- en damesbestand
    maak_controle_bestand(JAAR, aantal_maanden)
    if pdf_gewenst:
        dames_file = os.path.join(HTMLDIR, "Dames.html")
        maak_pdf(dames_file)

    logging.info("Klaar met verwerking.")

if __name__ == "__main__":
    main()


# Typ Ja of Nee en druk Enter.

# Kies Ja als je ook PDF’s wil. Jij hebt wkhtmltopdf al werkend ✅.
# (Zorg wel dat pdfkit geïnstalleerd is: pip install pdfkit.)

# Kies Nee als je voorlopig alleen HTML wil.

# Wat gebeurt er daarna?

# Het script telt je CSV’s in:

# C:\Users\patri\OneDrive\klassement\data\2025\


# Zorg dat daar de eerste N maanden op rij staan (vanaf September):
# September.csv, Oktober.csv, November.csv, ...

# Output komt hier:

# HTML → C:\Users\patri\OneDrive\klassement\output\2025\html\

# PDF → C:\Users\patri\OneDrive\klassement\output\2025\pdf\

# Zie je melding “Er ontbreken maanden”?
# Dan mist één van de eerste N CSV’s (bv. September.csv of Oktober.csv).

# Klaar om door te gaan: typ Ja (aanrader) en Enter. Als er iets faalt, plak de fout hier en ik fix ‘m meteen.

#================ voor jaartal varanderen: LIJN 13! =================
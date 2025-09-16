from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
import xlwings as xw
import logging

# Initialiseer Flask app
app = Flask(__name__)

# Logging configureren
logging.basicConfig(level=logging.DEBUG)

# Pad naar het Excel-bestand
BASE_DIR = Path(__file__).resolve().parent
filename = (BASE_DIR / "../Whistloting.xlsm").resolve()
tabblad = "AanwezigReserve"

# Geheugen-opslag voor gescande data (tijdelijk)
scanned_data = []
total_scans = 0

# Controleer of bestand bestaat
if not filename.exists():
    raise FileNotFoundError(f"Excel-bestand niet gevonden op pad: {filename}")

# Lees Excel-gegevens
def read_excel(sheet):
    data = []
    for i, row in enumerate(sheet.range("A3:F100").value, start=3):
        if row[0] is not None:
            barcode = str(row[0]).strip().split('.')[0]
            data.append({
                "barcode": barcode,
                "naam": row[1],
                "volledige_naam": row[3],
                "aantal_cell": row[5],
                "row_number": i
            })
    return data

# Barcode bijwerken in Excel
def update_quantity(barcode, aantal):
    global total_scans
    try:
        with xw.App(visible=False) as excel_app:
            excel_app.display_alerts = False
            excel_app.screen_updating = False

            wb = excel_app.books.open(filename)

            # Controleer of tabblad bestaat
            if tabblad not in [s.name for s in wb.sheets]:
                raise ValueError(f"Tabblad '{tabblad}' bestaat niet in {filename.name}")

            sheet = wb.sheets[tabblad]
            data = read_excel(sheet)

            barcode_found = False
            for item in data:
                if item["barcode"].lower() == barcode.lower():
                    sheet.range(f"F{item['row_number']}").value = aantal
                    naam = item["volledige_naam"]
                    wb.save()
                    scanned_data.append({
                        "barcode": barcode,
                        "naam": naam,
                        "aantal": aantal
                    })
                    total_scans += 1
                    barcode_found = True
                    break

            if not barcode_found:
                logging.warning(f"Barcode niet gevonden: {barcode}")

            wb.close()

    except Exception as e:
        logging.error(f"Fout bij het bijwerken van de barcode: {e}")

# Barcode verwijderen uit Excel
def remove_quantity(barcode, aantal):
    try:
        with xw.App(visible=False) as excel_app:
            excel_app.display_alerts = False
            excel_app.screen_updating = False

            wb = excel_app.books.open(filename)

            if tabblad not in [s.name for s in wb.sheets]:
                raise ValueError(f"Tabblad '{tabblad}' bestaat niet.")

            sheet = wb.sheets[tabblad]
            data = read_excel(sheet)

            for item in data:
                if item["barcode"].lower() == barcode.lower() and item["aantal_cell"] == aantal:
                    sheet.range(f"F{item['row_number']}").value = "A"
                    wb.save()
                    break

            wb.close()

    except Exception as e:
        logging.error(f"Fout bij het verwijderen van de barcode: {e}")

# Hoofdpagina
@app.route('/', methods=['GET', 'POST'])
def index():
    message = None

    if request.method == 'POST':
        barcode = request.form.get('barcode', '').strip()
        aantal = request.form.get('aantal', '').strip()

        if not barcode:
            message = "Barcode is vereist."
        else:
            try:
                aantal = int(aantal)
                update_quantity(barcode, aantal)
                message = f"Barcode {barcode} succesvol bijgewerkt!"
            except ValueError:
                message = "Voer een geldig getal in voor het aantal."
            except Exception as e:
                message = f"Er is een fout opgetreden: {e}"

    return render_template(
        'index.html',
        scanned_data=scanned_data,
        total_scans=total_scans,
        message=message
    )

# Item verwijderen
@app.route('/remove_entry', methods=['POST'])
def remove_entry():
    global scanned_data, total_scans

    barcode = request.form.get('barcode', '').strip()
    aantal = request.form.get('aantal', '').strip()

    try:
        aantal = int(aantal)
    except ValueError:
        return "Ongeldig aantal ingevoerd.", 400

    item_found = False
    for i, item in enumerate(scanned_data):
        if item['barcode'].lower() == barcode.lower() and item['aantal'] == aantal:
            scanned_data.pop(i)
            total_scans -= 1
            remove_quantity(barcode, aantal)
            item_found = True
            break

    if not item_found:
        return "Item niet gevonden.", 404

    return redirect(url_for('index'))

# Placeholder route
@app.route('/save_to_excel', methods=['POST'])
def save_to_excel():
    return "Opslaan naar Excel nog niet geïmplementeerd."

# Start de server
if __name__ == '__main__':
    app.run(debug=True)

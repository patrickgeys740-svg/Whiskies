from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
import xlwings as xw
import logging

app = Flask(__name__)

# Logconfiguratie
logging.basicConfig(level=logging.DEBUG)


# Specifiek relatieve pad naar Whistloting.xlsm
filename = Path("../Whistloting.xlsm")
tabblad = "AanwezigReserve"

# Lijst om ingevoerde gegevens op te slaan
scanned_data = []
total_scans = 0

# Controleer of Excel-bestand bestaat
if not filename.exists():
    raise FileNotFoundError(f"Het Excel-bestand {filename} bestaat niet. Controleer het pad.")

# Functie om gegevens uit het Excel-bestand te lezen
def read_excel(sheet):
    data = []
    for row in sheet.range("A3:F100").value:
        if row[0] is not None:
            barcode = str(row[0]).strip().split('.')[0]
            data.append({
                "barcode": barcode,
                "naam": row[1],
                "volledige_naam": row[3],
                "aantal_cell": row[5],
            })
    return data

# Functie om gegevens naar het Excel-bestand te schrijven
def write_excel(sheet, data):
    for i, item in enumerate(data, start=3):
        if "new_aantal" in item:
            sheet.range(f"F{i}").value = item["new_aantal"]

# Functie om de werkmap te openen en gegevens bij te werken
def update_quantity(barcode, aantal):
    global total_scans
    try:
        with xw.App(visible=False) as app:
            app.display_alerts = False
            app.screen_updating = False
            wb = app.books.open(filename)
            sheet = wb.sheets[tabblad]

            data = read_excel(sheet)
            barcode_found = False
            for item in data:
                if item["barcode"] == barcode:
                    item["new_aantal"] = aantal
                    barcode_found = True
                    naam = item["volledige_naam"]
                    write_excel(sheet, data)
                    wb.save()
                    scanned_data.append({"barcode": barcode, "naam": naam, "aantal": aantal})
                    total_scans += 1
                    break

            if not barcode_found:
                app.logger.warning(f"Barcode niet gevonden: {barcode}")
            wb.save()
    except Exception as e:
        app.logger.error(f"Fout bij het bijwerken van de barcode: {e}")

# Functie om gegevens in Excel te verwijderen en te vervangen door "A"
def remove_quantity(barcode, aantal):
    try:
        with xw.App(visible=False) as app:
            app.display_alerts = False
            app.screen_updating = False
            wb = app.books.open(filename)
            sheet = wb.sheets[tabblad]

            data = read_excel(sheet)
            for item in data:
                if item["barcode"] == barcode and item["aantal_cell"] == aantal:
                    item["new_aantal"] = "A"
                    write_excel(sheet, data)
                    wb.save()
                    break
            wb.save()
    except Exception as e:
        app.logger.error(f"Fout bij het verwijderen van de barcode: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    if request.method == 'POST':
        barcode = request.form.get('barcode', '').strip()
        aantal = request.form.get('aantal', '').strip()

        if not barcode:
            message = "Barcode is vereist."
        try:
            aantal = int(aantal)
            update_quantity(barcode, aantal)
            message = f"Barcode {barcode} succesvol bijgewerkt!"
        except ValueError:
            message = "Voer een geldig getal in voor het aantal."
        except Exception as e:
            message = f"Er is een fout opgetreden: {e}"

    return render_template('index.html', scanned_data=scanned_data, total_scans=total_scans, message=message)

@app.route('/remove_entry', methods=['POST'])
def remove_entry():
    barcode = request.form.get('barcode', '').strip()
    aantal = request.form.get('aantal', '').strip()

    global scanned_data, total_scans

    try:
        aantal = int(aantal)
    except ValueError:
        return "Ongeldig aantal ingevoerd.", 400

    # Zoek en verwijder het item
    item_found = False
    for i, item in enumerate(scanned_data):
        if item['barcode'] == barcode and item['aantal'] == aantal:
            scanned_data.pop(i)
            total_scans -= 1
            remove_quantity(barcode, aantal)
            item_found = True
            break

    if not item_found:
        return "Item niet gevonden.", 404

    return redirect(url_for('index'))

@app.route('/save_to_excel', methods=['POST'])
def save_to_excel():
    return "Opslaan naar Excel nog niet geïmplementeerd."

import webbrowser

if __name__ == '__main__':
    app.run(debug=True)

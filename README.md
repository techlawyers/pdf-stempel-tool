# PDF-Stempel

Ein portables Windows-Programm, das den Dateinamen oben rechts auf die erste Seite einer PDF setzt. Es wird als einzelne EXE verteilt und benötigt auf den Arbeitsplätzen keine Python-Installation.

Die Oberfläche hat eine feste Größe von 600 × 420 Pixeln.

## Verwendung

1. `PDF-Stempel.exe` starten.
2. PDF-Dateien in die Ablagefläche ziehen oder über **Datei auswählen** öffnen.
3. Die gestempelte Kopie liegt neben der Originaldatei und erhält den Zusatz `_gestempelt` im Dateinamen.

Originaldateien werden nicht verändert. Vorhandene gestempelte Kopien werden nicht überschrieben; weitere Kopien erhalten einen Zähler im Dateinamen. Nicht-PDF-Dateien werden übersprungen. Fehler bei einer Datei verhindern die Verarbeitung der übrigen Dateien nicht.

## Windows-EXE erstellen

Voraussetzungen für den Build-Rechner:

- Python 3.11 oder neuer
- pip
- PyInstaller

Abhängigkeiten installieren und die EXE erstellen:

```powershell
pip install -r requirements.txt
py -m pip install pyinstaller
.\build_windows.ps1
```

Die fertige Einzeldatei liegt hier:

```text
dist/PDF-Stempel.exe
```

Die EXE ist für Windows x64 gebaut. Für andere Betriebssysteme oder Prozessorarchitekturen ist ein eigener Build erforderlich.

## PDF-Verarbeitung testen

Die Tests erzeugen ausschließlich temporäre Beispieldateien. Sie prüfen Hoch- und Querformat in einem mehrseitigen PDF, Drehungen um 90, 180 und 270 Grad, den Stempel auf der ersten Seite, den Ausgabeordner, Namenskollisionen und den Erhalt der Originaldatei. Außerdem wird ein späterer Austausch am selben Pfad an einer Wegwerfdatei erprobt.

```powershell
py -m unittest discover -s tests -v
```

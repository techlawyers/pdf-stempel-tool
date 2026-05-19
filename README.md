# PDF Stempel Tool

Ein kleines Windows-Tool fuer die Kanzlei, das PDF-Dateien automatisch mit dem Dateinamen stempelt. Der Stempel wird oben rechts auf die erste Seite gesetzt.

## Funktionen

- PDFs per Doppelklick im Fenster auswaehlen
- PDFs per Drag & Drop ins Fenster ziehen
- PDFs direkt auf die EXE oder eine Verknuepfung ziehen
- Unterstriche im Dateinamen werden im Stempel durch Leerzeichen ersetzt
- Hoch- und Querformat werden anhand der ersten PDF-Seite beruecksichtigt
- Ausgabedateien landen im Ordner `stamped_pdfs` neben der EXE
- Bestehende Dateien werden nicht ueberschrieben; neue Dateien erhalten z.B. `Dokument (2).pdf`
- Fehlerhafte oder nicht lesbare PDFs brechen die Verarbeitung anderer Dateien nicht ab

## Nutzung fuer Mitarbeiter

### Variante 1: Dateien auf das Symbol ziehen

1. PDF-Dateien im Explorer markieren.
2. Die Dateien auf `stempel_tool.exe` oder eine Verknuepfung zur App ziehen.
3. Nach der Verarbeitung erscheint ein kurzer Ergebnisdialog.
4. Die gestempelten PDFs liegen im Ordner `stamped_pdfs` neben der EXE.

### Variante 2: App per Doppelklick starten

1. `stempel_tool.exe` per Doppelklick starten.
2. PDFs ins Fenster ziehen oder ueber `PDFs auswaehlen` auswaehlen.
3. Nach der Verarbeitung erscheint ein kurzer Ergebnisdialog.
4. Die gestempelten PDFs liegen im Ordner `stamped_pdfs` neben der EXE.

## Verwendung mit Python fuer Entwickler

### Voraussetzungen

- Python 3.11 oder neuer
- pip

### Installation

```bash
pip install -r requirements.txt
```

### Start

GUI starten:

```bash
python stempel_tool.py
```

Icon-Drop/CLI-Verarbeitung simulieren:

```bash
python stempel_tool.py "C:\Pfad\zu\Dokument.pdf"
```

## Windows-EXE erstellen

Die Kanzlei-Version wird als PyInstaller-Ordner gebaut. Verwende bewusst nicht `--onefile`, weil Drag & Drop und Antivirenpruefungen mit einem entpackten App-Ordner erfahrungsgemaess robuster sind.

### 1. PyInstaller installieren

```bash
pip install pyinstaller
```

### 2. Build ausfuehren

```bash
py -m PyInstaller --noconsole --onedir --name stempel_tool --icon=stempel_icon.ico stempel_tool.py
```

Alternativ kann unter Windows das Build-Skript verwendet werden:

```powershell
.\build_windows.ps1
```

### 3. Ergebnis verteilen

Die Anwendung liegt danach hier:

```text
dist/stempel_tool/
├─ stempel_tool.exe
├─ ... weitere Dateien
```

Verteile immer den gesamten Ordner `dist/stempel_tool`, z.B. als ZIP-Datei oder kopierten Ordner. Nicht nur die einzelne EXE weitergeben.

## Hinweise

- Der Ordner mit der EXE muss beschreibbar sein, weil dort `stamped_pdfs` angelegt wird.
- Wenn eine PDF nicht gelesen werden kann, wird sie im Ergebnisdialog als Fehler angezeigt.
- Nicht-PDF-Dateien werden uebersprungen.

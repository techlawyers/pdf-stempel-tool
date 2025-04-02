
# 🖋️ PDF Stempel Tool

Ein einfaches Python-Tool mit Drag & Drop-Fenster, das automatisch einen Stempel mit dem Dateinamen auf die erste Seite von PDF-Dateien setzt.

---

## 🔧 Funktionen

- PDF-Dateien per Drag & Drop ins Fenster ziehen
- Stempel des Dateinamens oben rechts auf der ersten Seite
- Erkennt automatisch Hoch- und Querformat
- Unterstriche im Dateinamen werden durch Leerzeichen ersetzt
- Ausgabedateien werden in `stamped_pdfs` gespeichert

---

## ▶️ Verwendung mit Python (für Entwickler)

### Voraussetzungen

- Python 3.11 oder neuer
- pip (Python-Paketmanager)

### Installation

1. Repository klonen oder ZIP herunterladen
2. Abhängigkeiten installieren:

   ```bash
   pip install -r requirements.txt
   ```

3. Tool starten:

   ```bash
   python stempel_tool.py
   ```

---

## 🪟 Erstellung einer Windows `.exe`

Um das Tool als eigenständige Windows-Anwendung weiterzugeben:

### 1. PyInstaller installieren

```bash
pip install pyinstaller
```

### 2. `.exe` erzeugen (mit Icon, ohne Konsole)

```bash
py -m PyInstaller --noconsole --icon=stempel_icon.ico stempel_tool.py
```

> Hinweis: Verwende **nicht `--onefile`**, da Drag & Drop damit oft Probleme macht.

### 3. Ergebnis

Die ausführbare Datei und alle benötigten Komponenten befinden sich im Ordner:

```
dist/stempel_tool/
├─ stempel_tool.exe       ← Diese Datei ausführen
├─ ... (weitere Dateien)
```

Verteile **den gesamten Ordner**, nicht nur die `.exe`.

---

## 📦 Bereitstellung an Kolleg:innen

1. Den Ordner `stempel_tool` z. B. auf den Desktop kopieren
2. `stempel_tool.exe` per Doppelklick starten
3. PDF-Dateien ins Fenster ziehen
4. Gestempelte PDFs erscheinen im Ordner `stamped_pdfs`

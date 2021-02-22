# zfdg_website_scraper
**v1.0 (22.02.2021)**  
*by Thomas Jurczyk*

Dieses Repository enthält die Dokumentation der Analyseergebnisse aus dem Artikel "Vorstellung eines (teil-)automatisierten Verfahrens zur Analyse der Multimodalität von Webseiten" (eingereicht bei [Zeitschrift für digitale Geisteswissenschaften](https://zfdg.de/)) und das im Kontext des Artikels genutzte Programm. Das Programm dient im derzeitigen Zustand nur zur Dokumentation und Nachvollzug der Analyse. Es ist nicht darauf ausgelegt, von anderen Personen, insbesondere solchen, die über keine Programmierkenntnisse verfügen, genutzt zu werden.

## Inhalt des Repository

### Ordner: `Dokumentation`

Dieser Ordner enthält die Ergebnisse der im Artikel besprochenen Analyse. Darunter sind:

1. Die Datei `data_abs_values.csv` mit den absoluten Werten der Features des Webseiten-Samples. Diese Datei dient zum Nachvollzug des Clusterings (vgl. Kapitel 4 des Artikels).
2. Die Screenshots des Text-, Video- und Bild-Feature Clustering aus Kapitel 4.2. d) (im Ordner `Screenshots`).
3. Die während Corpus-Initialisierung heruntergeladenen Daten (vgl. Kapitel 4.1.). Diese Daten befinden sich im Ordner `CorpusData`.
4. Die Dateien `image_data.pickle` und `merged_data_dict.pickle`, welche die Resultate des `DataPreparation()` Schritts enthalten (Kapitel 3.2. und 4.1.).

### Ordner: `Programm`

Dieser Ordner enthält die während die aktuellste im Kontext des Artikels genutzte Version des Programm zu Corpus-Initialisierung und -Analyse. Erneut ist darauf hinzuweisen, dass dieses Programm nicht für eine allgemeine Nutzung gedacht ist.

Der Ordner enthält die folgenden Dateien:

1. Alle im Kontext des Programms genutzten Klassen in den Files `scraper.py` (für die Corpus-Initialisierung, vgl. Kapitel 3.1.), `data_preparation.py` (Datengenerierung, vgl. Kapitel 3.2.) und `analyzer.py` (für die Analyse, vgl. Kapitel 3.3.).
2. Ein Jupyter Notebook (`Main_Program_Notebook.ipynb`), das die interaktive Ausführung des Programms inklusive Auswertung der Daten erlaubt.
3. Einen Ordner mit dem in diesem Programm genutzten Edge-Webdriver.
4. Die `requirements.txt` mit den Abhängigkeiten der in diesem Programm genutzten Bibliotheken und Frameworks.

Für Kritik und Anmerkungen bin ich immer dankbar!

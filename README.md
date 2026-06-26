# MSHV — logsync

Outil **FR / EN / NL** pour garder les journaux **WSJT-X** et **MSHV** synchronisés,
afin que l'affichage « déjà contacté » (*worked-before*) soit cohérent quel que soit
le programme utilisé.
*A **FR / EN / NL** tool to keep the WSJT-X and MSHV logs in sync. ·
Een **FR / EN / NL** tool om de WSJT-X- en MSHV-logboeken synchroon te houden.*

---

## Français

### Pourquoi
Quand on utilise tantôt MSHV, tantôt WSJT-X, chaque QSO n'est enregistré que par le
programme actif. Les deux journaux divergent, et le worked-before de l'un ignore ce
que l'autre a fait. Logsync calcule l'**union dédoublonnée** des deux journaux et
redonne à chacun ce qui lui manque.

### Deux versions disponibles
**Version Windows (.exe) — la plus simple, aucune installation**
Télécharger `logsync.exe` dans la section **[Releases](../../releases)**, le placer
dans un dossier, double-cliquer. Pas besoin de Python.
*(Au premier lancement, Windows SmartScreen peut afficher un avertissement car l'exe
n'est pas signé : « Informations complémentaires » → « Exécuter quand même ».)*

**Version Python (.py) — légère**
Nécessite **Python 3** (avec Tkinter, inclus dans l'installateur de python.org —
cocher « Add python.exe to PATH »). Télécharger `logsync_gui.py` et
`run_logsync_gui.bat`, les placer dans un même dossier, double-cliquer sur
`run_logsync_gui.bat`.

### Utilisation
1. Avec les boutons **Parcourir**, choisir le dossier des logs MSHV
   (`mshvlog.edim`, `mshvlog.adi`) et celui des logs WSJT-X
   (`wsjtx.log`, `wsjtx_log.adi`), puis **Enregistrer config**.
2. **Fermer MSHV et WSJT-X.**
3. Cliquer **Analyser** (n'écrit rien) pour vérifier les chiffres.
4. Cliquer **Fusionner** : sauvegarde horodatée automatique de chaque fichier,
   puis mise à jour des deux côtés.
5. Dans WSJT-X : *Settings → Colors → Rescan ADIF Log* pour rafraîchir les couleurs.

La langue de l'interface se change à tout moment avec le sélecteur **FR / EN / NL**
en haut de la fenêtre (le choix est mémorisé).

### Comment ça marche
- **Clé de dédoublonnage** : indicatif + date + heure (à la minute) + bande
  (déduite de la fréquence) + mode.
- Construit un **master** = union dédoublonnée du log actif MSHV (`mshvlog.edim`)
  et du log WSJT-X (`wsjtx.log`).
- Réécrit `wsjtx_log.adi`, complète `wsjtx.log`, complète `mshvlog.edim`.
- **Idempotent** : relancer n'ajoute jamais de doublon.
- Le miroir d'export `mshvlog.adi` n'est **pas** utilisé comme source : ainsi un QSO
  supprimé dans MSHV ne réapparaît pas.
- **Sauvegardes automatiques** horodatées avant toute écriture.

### Avertissement
Outil personnel fourni sans garantie. Faire des sauvegardes de ses logs reste
recommandé. Toujours lancer **MSHV et WSJT-X fermés** pendant la fusion.

### Auteur
Daniel — **ON7VZ**

---

## English

### Why
When you use MSHV sometimes and WSJT-X other times, each QSO is recorded only by the
active program. The two logs diverge, and the worked-before of one ignores what the
other did. Logsync computes the **deduplicated union** of both logs and gives each
side what it is missing.

### Two available versions
**Windows version (.exe) — simplest, nothing to install**
Download `logsync.exe` from the **[Releases](../../releases)** section, put it in a
folder, double-click. No Python required.
*(On first launch, Windows SmartScreen may warn because the exe is unsigned:
"More info" → "Run anyway".)*

**Python version (.py) — lightweight**
Requires **Python 3** (with Tkinter, included in the python.org installer — tick
"Add python.exe to PATH"). Download `logsync_gui.py` and `run_logsync_gui.bat`, put
them in the same folder, double-click `run_logsync_gui.bat`.

### Usage
1. Using the **Browse** buttons, select the MSHV log folder
   (`mshvlog.edim`, `mshvlog.adi`) and the WSJT-X log folder
   (`wsjtx.log`, `wsjtx_log.adi`), then **Save config**.
2. **Close MSHV and WSJT-X.**
3. Click **Analyse** (writes nothing) to check the numbers.
4. Click **Merge**: automatic timestamped backup of each file, then both sides are
   updated.
5. In WSJT-X: *Settings → Colors → Rescan ADIF Log* to refresh the colours.

The interface language can be switched at any time with the **FR / EN / NL** selector
at the top of the window (the choice is remembered).

### How it works
- **Deduplication key**: callsign + date + time (to the minute) + band
  (derived from frequency) + mode.
- Builds a **master** = deduplicated union of the active MSHV log (`mshvlog.edim`)
  and the WSJT-X log (`wsjtx.log`).
- Rewrites `wsjtx_log.adi`, completes `wsjtx.log`, completes `mshvlog.edim`.
- **Idempotent**: rerunning never adds duplicates.
- The `mshvlog.adi` export mirror is **not** used as a source, so a QSO deleted in
  MSHV does not come back.
- **Automatic timestamped backups** before any write.

### Warning
Personal tool provided without warranty. Backing up your logs is still recommended.
Always run **MSHV and WSJT-X closed** during the merge.

### Author
Daniel — **ON7VZ**

---

## Nederlands

### Waarom
Wanneer je nu eens MSHV en dan weer WSJT-X gebruikt, wordt elke QSO alleen door het
actieve programma opgeslagen. De twee logboeken lopen uiteen, en de worked-before van
het ene negeert wat het andere heeft gedaan. Logsync berekent de **ontdubbelde
samenvoeging** van beide logboeken en geeft elk logboek wat het mist.

### Twee versies beschikbaar
**Windows-versie (.exe) — eenvoudigst, niets te installeren**
Download `logsync.exe` uit de sectie **[Releases](../../releases)**, plaats het in een
map, dubbelklik. Geen Python nodig.
*(Bij de eerste start kan Windows SmartScreen waarschuwen omdat de exe niet
ondertekend is: "Meer informatie" → "Toch uitvoeren".)*

**Python-versie (.py) — licht**
Vereist **Python 3** (met Tkinter, inbegrepen in het installatieprogramma van
python.org — vink "Add python.exe to PATH" aan). Download `logsync_gui.py` en
`run_logsync_gui.bat`, plaats ze in dezelfde map, dubbelklik op `run_logsync_gui.bat`.

### Gebruik
1. Kies met de knoppen **Bladeren** de map met de MSHV-logs
   (`mshvlog.edim`, `mshvlog.adi`) en die met de WSJT-X-logs
   (`wsjtx.log`, `wsjtx_log.adi`), en klik op **Config opslaan**.
2. **Sluit MSHV en WSJT-X.**
3. Klik op **Analyseren** (schrijft niets) om de cijfers te controleren.
4. Klik op **Samenvoegen**: automatische back-up met tijdstempel van elk bestand,
   daarna worden beide kanten bijgewerkt.
5. In WSJT-X: *Settings → Colors → Rescan ADIF Log* om de kleuren te verversen.

De taal van de interface kan op elk moment gewijzigd worden met de keuzeknop
**FR / EN / NL** bovenaan het venster (de keuze wordt onthouden).

### Hoe het werkt
- **Ontdubbelsleutel**: callsign + datum + tijd (op de minuut) + band
  (afgeleid uit de frequentie) + mode.
- Bouwt een **master** = ontdubbelde samenvoeging van het actieve MSHV-logboek
  (`mshvlog.edim`) en het WSJT-X-logboek (`wsjtx.log`).
- Herschrijft `wsjtx_log.adi`, vult `wsjtx.log` aan, vult `mshvlog.edim` aan.
- **Idempotent**: opnieuw uitvoeren voegt nooit duplicaten toe.
- De exportspiegel `mshvlog.adi` wordt **niet** als bron gebruikt: zo komt een in
  MSHV verwijderde QSO niet terug.
- **Automatische back-ups** met tijdstempel vóór elke schrijfbewerking.

### Waarschuwing
Persoonlijk hulpmiddel, zonder garantie geleverd. Back-ups van je logboeken blijven
aanbevolen. Voer de samenvoeging altijd uit met **MSHV en WSJT-X gesloten**.

### Auteur
Daniel — **ON7VZ**

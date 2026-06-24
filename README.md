# MSHV
Logsync — Synchronisation des logs WSJT-X et MSHV

Outil FR / EN pour maintenir les journaux WSJT-X et MSHV mutuellement à jour, afin que l'affichage « déjà contacté » (worked-before) soit cohérent quel que soit le programme utilisé.

Pourquoi

Quand on utilise tantôt MSHV, tantôt WSJT-X, chaque QSO n'est enregistré que par le programme actif. Les deux journaux divergent, et le worked-before de l'un ignore ce que l'autre a fait. Logsync calcule l'union dédoublonnée des deux journaux et redonne à chacun ce qui lui manque.

Deux versions disponibles

Version Windows (.exe) — la plus simple, aucune installation Télécharger logsync.exe dans la section Releases, le placer dans un dossier, double-cliquer. Pas besoin de Python. (Au premier lancement, Windows SmartScreen peut afficher un avertissement car l'exe n'est pas signé : « Informations complémentaires » → « Exécuter quand même ».)

Version Python (.py) — légère Nécessite Python 3 (avec Tkinter, inclus dans l'installateur standard de python.org — cocher « Add python.exe to PATH »). Télécharger logsync_gui.py et run_logsync_gui.bat, les placer dans un même dossier, double-cliquer sur run_logsync_gui.bat.

Utilisation

    1. Avec les boutons Parcourir, choisir le dossier des logs MSHV (mshvlog.edim, mshvlog.adi) et celui des logs WSJT-X (wsjtx.log, wsjtx_log.adi), puis Enregistrer config.
    2. Fermer MSHV et WSJT-X.
    3. Cliquer Analyser (n'écrit rien) pour vérifier les chiffres.
    4. Cliquer Fusionner : sauvegarde horodatée automatique de chaque fichier, puis mise à jour des deux côtés.
    5. Dans WSJT-X : Settings → Colors → Rescan ADIF Log pour rafraîchir les couleurs.
    
La langue de l'interface se change à tout moment avec le sélecteur FR / EN en haut de la fenêtre (le choix est mémorisé).

Comment ça marche

    • Clé de dédoublonnage : indicatif + date + heure (à la minute) + bande (déduite de la fréquence) + mode.
    • Construit un master = union dédoublonnée des trois sources (wsjtx.log, mshvlog.adi, mshvlog.edim).
    • Réécrit wsjtx_log.adi, complète wsjtx.log, complète mshvlog.edim.
    • Idempotent : relancer n'ajoute jamais de doublon.
    • Sauvegardes automatiques horodatées avant toute écriture.
    
Avertissement

Outil personnel fourni sans garantie. Faire des sauvegardes de ses logs reste recommandé. Toujours lancer MSHV et WSJT-X fermés pendant la fusion.

Auteur

Daniel — ON7VZ

Logsync — Synchronizing WSJT-X and MSHV logs

A FR / EN tool to keep the WSJT-X and MSHV logs mutually up to date, so that the "worked-before" highlighting is consistent whichever program you use.

Why

When you use MSHV sometimes and WSJT-X other times, each QSO is recorded only by the active program. The two logs diverge, and the worked-before of one ignores what the other did. Logsync computes the deduplicated union of both logs and gives each side what it is missing.

Two available versions

Windows version (.exe) — simplest, nothing to install Download logsync.exe from the Releases section, put it in a folder, double-click. No Python required. (On first launch, Windows SmartScreen may warn because the exe is unsigned: "More info" → "Run anyway".)

Python version (.py) — lightweight Requires Python 3 (with Tkinter, included in the standard python.org installer — tick "Add python.exe to PATH"). Download logsync_gui.py and run_logsync_gui.bat, put them in the same folder, double-click run_logsync_gui.bat.

Usage

    1. Using the Browse buttons, select the MSHV log folder (mshvlog.edim, mshvlog.adi) and the WSJT-X log folder (wsjtx.log, wsjtx_log.adi), then Save config.
    2. Close MSHV and WSJT-X.
    3. Click Analyse (writes nothing) to check the numbers.
    4. Click Merge: automatic timestamped backup of each file, then both sides are updated.
    5. In WSJT-X: Settings → Colors → Rescan ADIF Log to refresh the colours.
    
The interface language can be switched at any time with the FR / EN selector at the top of the window (the choice is remembered).

How it works

    • Deduplication key: callsign + date + time (to the minute) + band (derived from frequency) + mode.
    • Builds a master = deduplicated union of the three sources (wsjtx.log, mshvlog.adi, mshvlog.edim).
    • Rewrites wsjtx_log.adi, completes wsjtx.log, completes mshvlog.edim.
    • Idempotent: rerunning never adds duplicates.
    • Automatic timestamped backups before any write.
    
Warning

Personal tool provided without warranty. Backing up your logs is still recommended. Always run MSHV and WSJT-X closed during the merge.

Author

Daniel — ON7VZ

# MSHV
Logsync — Synchronisation des logs WSJT-X et MSHV

Outil FR/EN pour maintenir les journaux WSJT-X et MSHV mutuellement à jour, afin que l'affichage « déjà contacté » (worked-before) soit cohérent quel que soit le programme utilisé.

Pourquoi

Quand on utilise tantôt MSHV, tantôt WSJT-X, chaque QSO n'est enregistré que par le programme actif. Les deux journaux divergent, et le worked-before de l'un ignore ce que l'autre a fait. Logsync calcule l'union dédoublonnée des deux journaux et redonne à chacun ce qui lui manque.

Prérequis

    • Windows
    • Python 3 (avec Tkinter, inclus dans l'installateur standard de python.org — cocher « Add python.exe to PATH » à l'installation)
    
Installation

Télécharger logsync_gui.py et run_logsync_gui.bat, les placer dans un même dossier, puis double-cliquer sur run_logsync_gui.bat.

Utilisation

    1. Choisir, avec les boutons Parcourir, le dossier des logs MSHV (mshvlog.edim, mshvlog.adi) et celui des logs WSJT-X (wsjtx.log, wsjtx_log.adi), puis Enregistrer config.
    2. Fermer MSHV et WSJT-X.
    3. Cliquer Analyser (n'écrit rien) pour vérifier les chiffres.
    4. Cliquer Fusionner : sauvegarde horodatée automatique de chaque fichier, puis mise à jour des deux côtés.
    5. Dans WSJT-X : Settings → Colors → Rescan ADIF Log pour rafraîchir les couleurs.
    
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

Logsync — Synchronizing WSJT-X and MSHV Logs

A tool FR/EN to keep WSJT-X and MSHV logs mutually up-to-date, ensuring consistent "worked-before" information regardless of the program used.

Why? 

When using either MSHV or WSJT-X, each QSO is recorded only by the active program. The two logs diverge, and the "worked-before" information in one log ignores what the other has done. Logsync calculates the unified, duplicated logs and restores the missing information to each.

Prerequisites

• Windows

• Python 3 (with Tkinter, included in the standard python.org installer — check "Add python.exe to PATH" during installation)

Installation

Download logsync_gui.py and run_logsync_gui.bat, place them in the same folder, then double-click on run_logsync_gui.bat.

Usage

1. Using the Browse buttons, select the MSHV log folder (mshvlog.edim, mshvlog.adi) and the WSJT-X log folder (wsjtx.log, wsjtx_log.adi), then Save config.
2. Close MSHV and WSJT-X.
3. Click Analyze (does not write anything) to check the numbers.
4. Click Merge: automatic timestamped saving of each file, then updating both. 5. In WSJT-X: Settings → Colors → Rescan ADIF Log to refresh the colors.

How it works

• Deduplication key: callsign + date + time (to the minute) + band (derived from frequency) + mode.
• Builds a master log = deduplicated union of the three sources (wsjtx.log, mshvlog.adi, mshvlog.edim).
• Rewrites wsjtx_log.adi, completes wsjtx.log, and completes mshvlog.edim.
• Idempotent: rerunning never adds duplicates.
• Automatic time-stamped backups before any writing.

Warning

This is a personal tool provided without warranty. Backing up your logs is still recommended. Always run MSHV and WSJT-X closed during the merge.

Author
Daniel — ON7VZ

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logsync_gui.py  -  Fusion des logs WSJT-X <-> MSHV   (ON7VZ)
============================================================

Interface graphique (Tkinter, aucune installation supplementaire).

Au premier lancement : choisis tes deux dossiers avec "Parcourir...".
  - Dossier MSHV  : contient mshvlog.edim et mshvlog.adi
  - Dossier WSJT-X: contient wsjtx.log et wsjtx_log.adi
Les chemins sont memorises dans config.ini (a cote du programme).

IMPORTANT : ferme MSHV ET WSJT-X avant de cliquer "Fusionner".
            (le programme ecrit directement dans leurs logs)

Deux boutons :
  - Analyser  : lit les logs, montre ce qui serait fait. N'ECRIT RIEN.
  - Fusionner : aligne les deux programmes sur le master complet.
       * sauvegarde automatique horodatee de mshvlog.edim et wsjtx_log.adi
       * reecrit wsjtx_log.adi = master complet
       * ajoute dans mshvlog.edim les QSO qui lui manquent
       (case a cocher : si decochee, produit un delta_pour_mshv.adi a
        importer a la main au lieu d'ecrire le .edim directement)

Cle de dedoublonnage : CALL + DATE + HEURE(minute) + BANDE(via frequence) + MODE
"""

import os
import re
import sys
import shutil
import configparser
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    TK_OK = True
except Exception:
    TK_OK = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.ini")

# --- frequence -> bande (longueur d'onde ADIF) ---
BAND_TABLE = [
    (1.8, 2.0, "160M"), (3.5, 4.0, "80M"), (5.2, 5.5, "60M"),
    (7.0, 7.3, "40M"), (10.1, 10.15, "30M"), (14.0, 14.35, "20M"),
    (18.0, 18.168, "17M"), (21.0, 21.45, "15M"), (24.8, 25.0, "12M"),
    (28.0, 29.7, "10M"), (50.0, 54.0, "6M"), (70.0, 71.0, "4M"),
    (144.0, 148.0, "2M"), (430.0, 440.0, "70CM"),
]
# bande ADIF -> notation MSHV (.edim) = MHz bas de bande
BAND_MSHV = {
    "160M": "1.8M", "80M": "3.5M", "60M": "5M", "40M": "7M", "30M": "10M",
    "20M": "14M", "17M": "18M", "15M": "21M", "12M": "24M", "10M": "28M",
    "6M": "50M", "4M": "70M", "2M": "144M", "70CM": "430M",
}
# mode -> code interne .edim
MODE_CODE = {
    "NON": "0", "SSB": "1", "CW": "2", "FM": "6", "MSK144": "17",
    "JT65A": "18", "PI4": "21", "FT8": "22", "FT4": "24", "Q65A": "25",
    "FT2": "29",
}
# code .edim -> mode
EDIM_MODE = {v: k for k, v in MODE_CODE.items()}


def band_from_freq(freq_mhz):
    try:
        f = float(freq_mhz)
    except (TypeError, ValueError):
        return None
    for lo, hi, name in BAND_TABLE:
        if lo <= f <= hi:
            return name
    return None


def canon_mode(mode, submode):
    mode = (mode or "").upper()
    submode = (submode or "").upper()
    if mode == "MFSK":
        return submode if submode in ("FT4", "FT2") else "FT4"
    return mode


def qso_key(q):
    return (q["call"], q["date"], q["time"][:4], q["band"], q["mode"])


def _mk(call, date, time, band, mode, submode="", freq="", date_off="",
        time_off="", grid="", rst_s="", rst_r="", comment=""):
    if len(time) == 4:
        time = time + "00"
    return {
        "call": call.upper().strip(), "date": date.strip(), "time": time.strip(),
        "date_off": (date_off or date).strip(), "time_off": (time_off or time).strip(),
        "band": band, "mode": mode, "submode": submode, "freq": freq,
        "grid": grid.strip().upper(), "rst_s": rst_s.strip(), "rst_r": rst_r.strip(),
        "comment": comment.strip(),
    }


# ---------------------------------------------------------------- parseurs

def parse_wsjtx_csv(path):
    out = []
    if not os.path.isfile(path):
        return out, "ABSENT"
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            c = ln.rstrip("\r\n").split(",")
            if len(c) < 10:
                continue
            date = c[0].replace("-", "")
            if len(date) != 8 or not c[4]:
                continue
            mode_raw = c[7].upper()
            submode = "FT4" if mode_raw == "MFSK" else ""
            out.append(_mk(c[4], date, c[1].replace(":", ""),
                           band_from_freq(c[6]) or c[6], canon_mode(mode_raw, submode),
                           submode, c[6], c[2].replace("-", ""), c[3].replace(":", ""),
                           c[5], c[8], c[9]))
    return out, "OK"


def _adi_field(rec, name):
    m = re.search(r"(?i)<" + name + r":(\d+)(?::[^>]*)?>", rec)
    if not m:
        return ""
    return rec[m.end():m.end() + int(m.group(1))]


def parse_mshv_adi(path):
    out = []
    if not os.path.isfile(path):
        return out, "ABSENT"
    data = open(path, "r", encoding="utf-8", errors="replace").read()
    for rec in re.split(r"(?i)<eor>", data):
        if "<call" not in rec.lower():
            continue
        call = _adi_field(rec, "call")
        date = _adi_field(rec, "qso_date")
        if len(date) != 8 or not call:
            continue
        submode = _adi_field(rec, "submode")
        freq = _adi_field(rec, "freq")
        out.append(_mk(call, date, _adi_field(rec, "time_on"),
                       band_from_freq(freq) or _adi_field(rec, "band").upper(),
                       canon_mode(_adi_field(rec, "mode"), submode), submode, freq,
                       _adi_field(rec, "qso_date_off"), _adi_field(rec, "time_off"),
                       _adi_field(rec, "gridsquare"), _adi_field(rec, "rst_sent"),
                       _adi_field(rec, "rst_rcvd"), _adi_field(rec, "comment")))
    return out, "OK"


def parse_mshv_edim(path):
    out = []
    if not os.path.isfile(path):
        return out, "ABSENT"
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("["):
                continue
            c = ln.split(";")
            if len(c) < 11:
                continue
            date = c[0]
            call = c[4]
            if len(date) != 8 or not call:
                continue
            mode = EDIM_MODE.get(c[5], c[5])
            submode = "FT4" if mode == "FT4" else ("FT2" if mode == "FT2" else "")
            freq_mhz = ""
            try:
                if c[10]:
                    freq_mhz = "%.6f" % (float(c[10]) / 1000.0)
            except ValueError:
                freq_mhz = ""
            out.append(_mk(call, date, c[1], band_from_freq(freq_mhz) or c[9].upper(),
                           mode, submode, freq_mhz, c[2], c[3], c[8], c[6], c[7],
                           c[11] if len(c) > 11 else ""))
    return out, "OK"


# ---------------------------------------------------------------- fusion

def richness(q):
    return sum(1 for k in ("grid", "rst_s", "rst_r", "freq", "comment") if q.get(k))


def build_master(*lists):
    master = {}
    for lst in lists:
        for q in lst:
            k = qso_key(q)
            if k not in master:
                master[k] = dict(q)
            else:
                cur = master[k]
                for f in ("grid", "rst_s", "rst_r", "freq", "comment", "date_off", "time_off"):
                    if not cur.get(f) and q.get(f):
                        cur[f] = q[f]
                if richness(q) > richness(cur):
                    merged = dict(q)
                    for f in ("grid", "rst_s", "rst_r", "freq", "comment"):
                        if not merged.get(f) and cur.get(f):
                            merged[f] = cur[f]
                    master[k] = merged
    return master


# ---------------------------------------------------------------- emission ADIF

def _f(name, val):
    val = "" if val is None else str(val)
    return "<%s:%d>%s" % (name, len(val), val)


def qso_to_adif(q, station_call, my_grid):
    p = []
    if station_call:
        p.append(_f("STATION_CALLSIGN", station_call))
    if my_grid:
        p.append(_f("MY_GRIDSQUARE", my_grid))
    p.append(_f("CALL", q["call"]))
    if q.get("grid"):
        p.append(_f("GRIDSQUARE", q["grid"]))
    if q["mode"] in ("FT4", "FT2"):
        p.append(_f("MODE", "MFSK"))
        p.append(_f("SUBMODE", q["mode"]))
    else:
        p.append(_f("MODE", q["mode"]))
    if q.get("rst_s"):
        p.append(_f("RST_SENT", q["rst_s"]))
    if q.get("rst_r"):
        p.append(_f("RST_RCVD", q["rst_r"]))
    p.append(_f("QSO_DATE", q["date"]))
    p.append(_f("TIME_ON", q["time"]))
    p.append(_f("QSO_DATE_OFF", q["date"]))
    p.append(_f("TIME_OFF", q.get("time_off") or q["time"]))
    p.append(_f("BAND", q["band"]))
    if q.get("freq"):
        p.append(_f("FREQ", q["freq"]))
    if q.get("comment"):
        p.append(_f("COMMENT", q["comment"]))
    p.append("<EOR>")
    return "".join(p)


def write_adif(path, qsos, station_call, my_grid, title):
    qsos = sorted(qsos, key=lambda q: (q["date"], q["time"], q["call"]))
    with open(path, "w", encoding="utf-8", newline="\r\n") as fh:
        fh.write("%s\n<ADIF_VER:5>3.1.0\n<PROGRAMID:8>logsync\n<EOH>\n" % title)
        for q in qsos:
            fh.write(qso_to_adif(q, station_call, my_grid) + "\n")


# ---------------------------------------------------------------- emission EDIM

def freq_to_khz(freq_mhz):
    try:
        return str(int(round(float(freq_mhz) * 1000.0)))
    except (TypeError, ValueError):
        return ""


def qso_to_edim_line(q):
    """Construit une ligne .edim (29 champs) au format MSHV.
    Champs connus 0..11 ; le reste vide ou defaut, MSHV recalcule la distance."""
    mode_code = MODE_CODE.get(q["mode"], "")
    if not mode_code:
        return None  # mode non gerable en .edim, on ignore
    band = BAND_MSHV.get(q["band"], q["band"])
    khz = freq_to_khz(q.get("freq"))
    ss = q["time"][4:6] if len(q["time"]) >= 6 else "00"
    f = [""] * 29
    f[0] = q["date"]
    f[1] = q["time"][:4]
    f[2] = q.get("date_off") or q["date"]
    f[3] = (q.get("time_off") or q["time"])[:4]
    f[4] = q["call"]
    f[5] = mode_code
    f[6] = q.get("rst_s", "")
    f[7] = q.get("rst_r", "")
    f[8] = q.get("grid", "")
    f[9] = band
    f[10] = khz
    f[11] = q.get("comment", "")
    f[17] = "0"      # cont_id
    f[18] = ss       # enum_sec_sta
    f[19] = "0"      # trmN
    f[20] = ss       # enum_sec_end
    # f[21] dist vide -> MSHV recalcule
    return ";".join(f)


def append_edim(path, qsos):
    """Ajoute les QSO a la fin du .edim existant (contenu existant intact)."""
    lines = []
    for q in sorted(qsos, key=lambda x: (x["date"], x["time"], x["call"])):
        ln = qso_to_edim_line(q)
        if ln is not None:
            lines.append(ln)
    if not lines:
        return 0
    # s'assurer que le fichier existant se termine par un saut de ligne
    data = b""
    if os.path.isfile(path):
        with open(path, "rb") as fh:
            data = fh.read()
    needs_nl = bool(data) and not data.endswith(b"\n")
    with open(path, "ab") as fh:
        if needs_nl:
            fh.write(b"\r\n")
        fh.write(("\r\n".join(lines) + "\r\n").encode("utf-8"))
    return len(lines)


def timestamped_backup(path):
    if not os.path.isfile(path):
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = "%s.backup-%s" % (path, stamp)
    shutil.copy2(path, bak)
    return bak


# ---------------------------------------------------------------- emission CSV (wsjtx.log)

def _csv_dt(d, t):
    d = (d or "")
    t = (t or "")
    date = "%s-%s-%s" % (d[0:4], d[4:6], d[6:8]) if len(d) >= 8 else d
    if len(t) >= 6:
        time = "%s:%s:%s" % (t[0:2], t[2:4], t[4:6])
    elif len(t) >= 4:
        time = "%s:%s:00" % (t[0:2], t[2:4])
    else:
        time = t
    return date, time


def qso_to_csv_line(q, n_fields):
    d_on, t_on = _csv_dt(q["date"], q["time"])
    d_off, t_off = _csv_dt(q.get("date_off") or q["date"], q.get("time_off") or q["time"])
    try:
        freq = "%.6f" % float(q.get("freq"))
    except (TypeError, ValueError):
        freq = q.get("freq", "")
    base = [d_on, t_on, d_off, t_off, q["call"], q.get("grid", ""), freq,
            q["mode"], q.get("rst_s", ""), q.get("rst_r", "")]
    while len(base) < n_fields:
        base.append("")
    return ",".join(base[:max(n_fields, len(base))])


def detect_csv_fields(path):
    n = 17
    if os.path.isfile(path):
        last = None
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                ln = ln.rstrip("\r\n")
                if ln:
                    last = ln
        if last:
            n = last.count(",") + 1
    return n if n in (14, 17) else 17


def append_csv(path, qsos):
    if not qsos:
        return 0
    n = detect_csv_fields(path)
    lines = [qso_to_csv_line(q, n)
             for q in sorted(qsos, key=lambda x: (x["date"], x["time"], x["call"]))]
    data = b""
    if os.path.isfile(path):
        with open(path, "rb") as fh:
            data = fh.read()
    needs_nl = bool(data) and not data.endswith(b"\n")
    with open(path, "ab") as fh:
        if needs_nl:
            fh.write(b"\r\n")
        fh.write(("\r\n".join(lines) + "\r\n").encode("utf-8"))
    return len(lines)


# ================================================================ GUI

class App:
    def __init__(self, root):
        self.root = root
        root.title("logsync  -  Fusion WSJT-X / MSHV   (ON7VZ)")
        root.geometry("760x560")

        self.v_mshv = tk.StringVar()
        self.v_wsjtx = tk.StringVar()
        self.v_call = tk.StringVar(value="ON7VZ")
        self.v_grid = tk.StringVar(value="JO10WQ")
        self.v_edim_direct = tk.BooleanVar(value=True)

        self._build_ui()
        self._load_config()

    def _build_ui(self):
        pad = {"padx": 6, "pady": 4}
        frm = ttk.LabelFrame(self.root, text="Configuration")
        frm.pack(fill="x", padx=10, pady=8)

        ttk.Label(frm, text="Dossier MSHV (mshvlog.edim / .adi) :").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.v_mshv, width=58).grid(row=0, column=1, **pad)
        ttk.Button(frm, text="Parcourir...", command=self._browse_mshv).grid(row=0, column=2, **pad)

        ttk.Label(frm, text="Dossier WSJT-X (wsjtx.log / _log.adi) :").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.v_wsjtx, width=58).grid(row=1, column=1, **pad)
        ttk.Button(frm, text="Parcourir...", command=self._browse_wsjtx).grid(row=1, column=2, **pad)

        sub = ttk.Frame(frm)
        sub.grid(row=2, column=0, columnspan=3, sticky="w", **pad)
        ttk.Label(sub, text="Indicatif :").pack(side="left")
        ttk.Entry(sub, textvariable=self.v_call, width=10).pack(side="left", padx=(2, 14))
        ttk.Label(sub, text="Locator :").pack(side="left")
        ttk.Entry(sub, textvariable=self.v_grid, width=10).pack(side="left", padx=2)
        ttk.Button(sub, text="Enregistrer config", command=self._save_config).pack(side="left", padx=20)

        act = ttk.Frame(self.root)
        act.pack(fill="x", padx=10)
        ttk.Button(act, text="Analyser  (ne modifie rien)", command=self.do_analyse).pack(side="left", padx=4)
        ttk.Button(act, text="FUSIONNER", command=self.do_fusionner).pack(side="left", padx=4)
        ttk.Checkbutton(act, text="Ecrire directement dans MSHV (.edim)",
                        variable=self.v_edim_direct).pack(side="left", padx=10)

        self.txt = scrolledtext.ScrolledText(self.root, wrap="word", height=22)
        self.txt.pack(fill="both", expand=True, padx=10, pady=8)
        self.log("Choisis tes deux dossiers, puis clique sur \"Analyser\".")
        self.log("Avant \"Fusionner\" : FERME MSHV et WSJT-X.\n")

    # ---- utilitaires UI
    def log(self, msg=""):
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")
        self.root.update_idletasks()

    def clear(self):
        self.txt.delete("1.0", "end")

    def _browse_mshv(self):
        d = filedialog.askdirectory(title="Dossier des logs MSHV")
        if d:
            self.v_mshv.set(os.path.normpath(d))

    def _browse_wsjtx(self):
        d = filedialog.askdirectory(title="Dossier des logs WSJT-X")
        if d:
            self.v_wsjtx.set(os.path.normpath(d))

    # ---- config
    def _load_config(self):
        if not os.path.isfile(CONFIG_PATH):
            return
        cfg = configparser.ConfigParser()
        cfg.read(CONFIG_PATH, encoding="utf-8")
        self.v_mshv.set(cfg.get("paths", "mshv_log_dir", fallback=""))
        self.v_wsjtx.set(cfg.get("paths", "wsjtx_log_dir", fallback=""))
        self.v_call.set(cfg.get("station", "call", fallback="ON7VZ"))
        self.v_grid.set(cfg.get("station", "grid", fallback="JO10WQ"))

    def _save_config(self):
        cfg = configparser.ConfigParser()
        cfg["paths"] = {"mshv_log_dir": self.v_mshv.get().strip(),
                        "wsjtx_log_dir": self.v_wsjtx.get().strip()}
        cfg["station"] = {"call": self.v_call.get().strip(),
                          "grid": self.v_grid.get().strip()}
        with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
            cfg.write(fh)
        self.log("Config enregistree dans %s\n" % CONFIG_PATH)

    # ---- coeur
    def _paths(self):
        m = self.v_mshv.get().strip()
        w = self.v_wsjtx.get().strip()
        return (os.path.join(m, "mshvlog.adi"), os.path.join(m, "mshvlog.edim"),
                os.path.join(w, "wsjtx.log"), os.path.join(w, "wsjtx_log.adi"))

    def _read_all(self):
        p_adi, p_edim, p_csv, p_wadi = self._paths()
        ad, s_ad = parse_mshv_adi(p_adi)
        ed, s_ed = parse_mshv_edim(p_edim)
        wx, s_wx = parse_wsjtx_csv(p_csv)
        return ad, ed, wx, (s_ad, s_ed, s_wx)

    def _check_paths(self):
        if not self.v_mshv.get().strip() or not self.v_wsjtx.get().strip():
            messagebox.showwarning("Dossiers manquants",
                                   "Choisis d'abord les deux dossiers (boutons Parcourir).")
            return False
        return True

    def do_analyse(self):
        if not self._check_paths():
            return
        self.clear()
        ad, ed, wx, st = self._read_all()
        s_ad, s_ed, s_wx = st
        if "ABSENT" in st:
            self.log("PROBLEME : certains fichiers sont introuvables.")
            self.log("  mshvlog.adi  : %s" % s_ad)
            self.log("  mshvlog.edim : %s" % s_ed)
            self.log("  wsjtx.log    : %s" % s_wx)
            self.log("Verifie les deux dossiers.")
            return
        edim_keys = set(qso_key(q) for q in ed)
        wsjtx_keys = set(qso_key(q) for q in wx)
        master = build_master(ad, ed, wx)
        delta_mshv = [master[k] for k in set(master) - edim_keys]
        add_wsjtx = [master[k] for k in set(master) - wsjtx_keys]
        from collections import Counter
        mc = Counter(k[4] for k in master)
        self.log("=== ANALYSE (rien n'a ete modifie) ===\n")
        self.log("WSJT-X  wsjtx.log    : %d QSO" % len(wsjtx_keys))
        self.log("MSHV    mshvlog.adi  : %d QSO" % len(ad))
        self.log("MSHV    mshvlog.edim : %d QSO (log actif)" % len(edim_keys))
        self.log("")
        self.log("MASTER (union) : %d QSO  [%s]" %
                 (len(master), ", ".join("%s=%d" % (m, n) for m, n in sorted(mc.items(), key=lambda x: -x[1]))))
        self.log("")
        self.log("Si tu fusionnes :")
        self.log("  -> MSHV  mshvlog.edim  recevra : %d QSO" % len(delta_mshv))
        self.log("  -> WSJT-X wsjtx_log.adi passera a : %d QSO" % len(master))
        self.log("  -> WSJT-X wsjtx.log    recevra : %d QSO" % len(add_wsjtx))

    def do_fusionner(self):
        if not self._check_paths():
            return
        if not messagebox.askyesno(
                "Confirmer la fusion",
                "MSHV et WSJT-X doivent etre FERMES.\n\n"
                "Le programme va :\n"
                "  - sauvegarder mshvlog.edim et wsjtx_log.adi (copie horodatee)\n"
                "  - reecrire wsjtx_log.adi avec le master complet\n"
                "  - %s\n\nContinuer ?" %
                ("ajouter les QSO manquants dans mshvlog.edim"
                 if self.v_edim_direct.get() else
                 "produire delta_pour_mshv.adi (import manuel dans MSHV)")):
            return

        self.clear()
        p_adi, p_edim, p_csv, p_wadi = self._paths()
        ad, ed, wx, st = self._read_all()
        if "ABSENT" in st:
            self.log("Abandon : fichiers introuvables. Lance d'abord Analyser.")
            return
        call = self.v_call.get().strip()
        grid = self.v_grid.get().strip()
        edim_keys = set(qso_key(q) for q in ed)
        csv_keys = set(qso_key(q) for q in wx)
        master = build_master(ad, ed, wx)
        delta_mshv = [master[k] for k in set(master) - edim_keys]
        delta_csv = [master[k] for k in set(master) - csv_keys]

        self.log("=== FUSION ===\n")
        try:
            # 1) WSJT-X .adi : sauvegarde + reecriture complete
            bak_w = timestamped_backup(p_wadi)
            if bak_w:
                self.log("Sauvegarde wsjtx_log.adi : %s" % os.path.basename(bak_w))
            write_adif(p_wadi, list(master.values()), call, grid,
                       "logsync master export (pour WSJT-X)")
            self.log("wsjtx_log.adi reecrit : %d QSO" % len(master))

            # 1b) WSJT-X .log (CSV) : sauvegarde + ajout des QSO manquants
            bak_c = timestamped_backup(p_csv)
            if bak_c:
                self.log("Sauvegarde wsjtx.log : %s" % os.path.basename(bak_c))
            n_csv = append_csv(p_csv, delta_csv)
            self.log("wsjtx.log : %d QSO ajoutes" % n_csv)
            self.log("")

            # 2) MSHV
            if self.v_edim_direct.get():
                bak_e = timestamped_backup(p_edim)
                if bak_e:
                    self.log("Sauvegarde mshvlog.edim : %s" % os.path.basename(bak_e))
                n = append_edim(p_edim, delta_mshv)
                self.log("mshvlog.edim : %d QSO ajoutes (total ~%d)" % (n, len(master)))
            else:
                out = os.path.join(self.v_mshv.get().strip(), "delta_pour_mshv.adi")
                write_adif(out, delta_mshv, call, grid, "logsync delta (a importer)")
                self.log("delta_pour_mshv.adi cree (%d QSO)" % len(delta_mshv))
                self.log("=> dans MSHV : Log > Add ADIF To Log > delta_pour_mshv.adi")
        except Exception as e:
            self.log("\nERREUR : %s" % e)
            messagebox.showerror("Erreur", str(e))
            return

        self.log("\nTermine. Rouvre MSHV et WSJT-X (dans WSJT-X : Settings >")
        self.log("Colors > Rescan ADIF Log pour rafraichir les couleurs).")
        messagebox.showinfo("Fusion terminee",
                            "Les logs sont alignes.\nN'oublie pas le \"Rescan ADIF Log\" dans WSJT-X.")


def main():
    if not TK_OK:
        print("Tkinter introuvable : reinstalle Python en cochant 'tcl/tk'.")
        return
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

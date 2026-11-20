#!/usr/bin/env python3
"""Hook PreToolUse (Bash) : applique réellement les règles « deny » de Claude Code.

Les règles `deny` de settings.json se contournent en enveloppant la commande
(`bash -c "…"`, `env X=1 …`, `/usr/bin/…`, `a && b`, `python3 -c "…"`). Ce hook relit
ces règles et bloque la commande si l'une d'elles apparaît dans n'importe quel segment,
y compris enveloppé. Il ne fait que bloquer : il n'autorise jamais rien.

Sources : ~/.claude/settings.json et ~/.claude/settings.local.json, plus le
.claude/settings*.json du projet courant. Règles lues : `Bash(<motif>)` ; `*` = n'importe quoi,
`x:*` = `x` suivi de n'importe quoi.

Prudence assumée : la règle entière (ex. « rm -rf », pas seulement « rm ») suffit à bloquer, si elle
apparaît dans du code exécuté : argument d'un interpréteur (`python3 -c`, `node -e`, `awk`…), d'un
lanceur (`find -exec`, `ssh`, `watch`…), ou corps d'un heredoc envoyé à un interpréteur ou écrit
dans un script (.sh, .py, .js…). Comme simple donnée (`echo`, `grep`, message de commit, heredoc
écrit dans un .md), il ne bloque pas. Limite : un fichier de données écrit puis exécuté sous un
autre nom n'est pas suivi.
Code de sortie 2 = commande bloquée (raison sur stderr, renvoyée à l'agent) ; 0 = laissée passer.
"""
import json
import os
import re
import shlex
import sys

INTERPRETEURS = re.compile(r"(python[\d.]*|node|nodejs|deno|bun|perl|ruby|php|lua|Rscript|osascript|pwsh"
                           r"|bash|sh|zsh|dash|ksh|fish|awk|gawk|mawk)")
LANCEURS = {"find", "watch", "ssh", "parallel", "flock", "su", "runuser", "setsid", "chroot", "unshare", "nsenter",
            "strace", "ltrace", "systemd-run", "at", "batch", "script", "docker", "podman", "kubectl"}
EXT_SCRIPT = re.compile(r">\s*\S+\.(sh|bash|zsh|py|js|mjs|cjs|ts|pl|rb|php)\b")
ENVELOPPES = {"sudo", "env", "command", "builtin", "exec", "nohup", "time", "nice", "xargs", "timeout", "stdbuf"}


def fichiers_reglages(cwd):
    maison = os.path.expanduser("~/.claude")
    fichiers = [os.path.join(maison, "settings.json"), os.path.join(maison, "settings.local.json")]
    if cwd:
        fichiers += [os.path.join(cwd, ".claude", n) for n in ("settings.json", "settings.local.json")]
    return fichiers


def motifs_interdits(cwd):
    motifs = []
    for fichier in fichiers_reglages(cwd):
        try:
            with open(fichier, encoding="utf-8") as f:
                deny = (json.load(f).get("permissions") or {}).get("deny") or []
        except (OSError, ValueError):
            continue
        for regle in deny:
            m = re.fullmatch(r"Bash\((.*)\)", regle.strip()) if isinstance(regle, str) else None
            if m:
                motifs.append(re.sub(r":\*$", " *", m.group(1).strip()))
    return motifs


def en_regex(motif):
    morceaux = [re.escape(p) for p in motif.split("*")]
    texte = ".*".join(morceaux).replace(r"\ ", r"\s+")
    # « x * » couvre aussi « x » seul.
    texte = re.sub(r"\\s\+\.\*$", r"(\\s.*)?", texte)
    return re.compile(r"^" + texte + r"$", re.S)


def en_regex_code(motif):
    """La règle entière, cherchée n'importe où dans un texte de code (« x * » : x suivi d'une fin de mot)."""
    texte = ".*".join(re.escape(p) for p in motif.split("*")).replace(r"\ ", r"\s+")
    texte = re.sub(r"\\s\+\.\*$", r"(?![\\w-])", texte)
    return re.compile(r"(?<![\w./-])" + texte, re.S)


def segments(commande, profondeur=0):
    """Découpe en commandes simples, en déroulant bash -c, $( ), ` `, et les enveloppes."""
    if profondeur > 5:
        return [commande]
    resultat = []
    for interne in re.findall(r"\$\(([^()]*)\)|`([^`]*)`", commande):
        resultat += segments(interne[0] or interne[1], profondeur + 1)
    for brut in re.split(r"\|\||&&|[;|&\n()]", commande):
        brut = brut.strip()
        if not brut:
            continue
        try:
            mots = shlex.split(brut)
        except ValueError:
            mots = brut.split()
        while mots and (re.fullmatch(r"[A-Za-z_]\w*=.*", mots[0]) or os.path.basename(mots[0]) in ENVELOPPES):
            mots.pop(0)
            while mots and (mots[0].startswith("-") or re.fullmatch(r"\d+[smhd]?", mots[0])):
                mots.pop(0)
        if not mots:
            continue
        mots[0] = os.path.basename(mots[0])
        if mots[0] in {"bash", "sh", "zsh", "dash"} and "-c" in mots[1:-1]:
            resultat += segments(mots[mots.index("-c") + 1], profondeur + 1)
            continue
        resultat.append(" ".join(mots))
    return resultat


def programme(segment):
    return segment.split()[0] if segment.split() else ""


def execute_du_code(segment):
    p = programme(segment)
    return bool(INTERPRETEURS.fullmatch(p)) or p in LANCEURS


def separer_heredocs(commande):
    """Retire les corps de heredoc qui ne sont que des données ; renvoie (commande, corps de code)."""
    lignes, gardees, codes, i = commande.split("\n"), [], [], 0
    while i < len(lignes):
        ligne = lignes[i]
        gardees.append(ligne)
        i += 1
        m = re.search(r"<<-?\s*(['\"]?)(\w+)\1", ligne)
        if not m:
            continue
        corps = []
        while i < len(lignes) and lignes[i].strip() != m.group(2):
            corps.append(lignes[i])
            i += 1
        fin = lignes[i] if i < len(lignes) else ""
        i += 1
        sans_marqueur = ligne[:m.start()] + ligne[m.end():]
        if EXT_SCRIPT.search(ligne) or any(execute_du_code(s) for s in segments(sans_marqueur)):
            gardees += corps + [fin]
            codes.append("\n".join(corps))
        else:
            gardees.append(fin)
    return "\n".join(gardees), codes


def raison_blocage(commande, motifs):
    commande, codes = separer_heredocs(commande)
    segs = segments(commande)
    # Le découpage en segments coupe le code d'un interpréteur (aux « ; » et parenthèses) : dès qu'un
    # segment exécute du code, toute la commande (heredocs de données retirés) est traitée comme du code.
    textes_de_code = ([commande] if any(execute_du_code(s) for s in segs) else []) + codes
    for motif in motifs:
        regex = en_regex(motif)
        for seg in segs:
            if regex.match(seg):
                return f"« {seg} » correspond à la règle deny « Bash({motif}) »."
        programme = motif.split()[0] if motif.split() else ""
        code = en_regex_code(motif) if programme and "*" not in programme else None
        if code and any(code.search(t) for t in textes_de_code):
            return f"la règle « Bash({motif}) » apparaît dans du code exécuté."
    return None


def principal():
    try:
        entree = json.load(sys.stdin)
    except ValueError:
        return 0
    if entree.get("tool_name") != "Bash":
        return 0
    commande = (entree.get("tool_input") or {}).get("command") or ""
    raison = raison_blocage(commande, motifs_interdits(entree.get("cwd")))
    if raison:
        print(f"Commande bloquée par le hook bloquer-commandes-interdites : {raison} "
              "Ne pas contourner ; demander à l'utilisateur.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(principal())

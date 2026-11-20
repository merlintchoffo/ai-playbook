#!/usr/bin/env python3
"""Hook PreToolUse (Bash) : applique réellement les règles « deny » de Claude Code.

Les règles `deny` de settings.json se contournent en enveloppant la commande
(`bash -c "…"`, `env X=1 …`, `/usr/bin/…`, `a && b`, `python3 -c "…"`). Ce hook relit
ces règles et bloque la commande si l'une d'elles apparaît dans n'importe quel segment,
y compris enveloppé. Il ne fait que bloquer : il n'autorise jamais rien.

Sources : ~/.claude/settings.json et ~/.claude/settings.local.json, plus le
.claude/settings*.json du projet courant. Règles lues : `Bash(<motif>)` ; `*` = n'importe quoi,
`x:*` = `x` suivi de n'importe quoi.

Prudence assumée : le nom d'un programme interdit écrit comme mot isolé, n'importe où dans la
commande (par exemple dans un script `python3 -c`), suffit à bloquer.
Code de sortie 2 = commande bloquée (raison sur stderr, renvoyée à l'agent) ; 0 = laissée passer.
"""
import json
import os
import re
import shlex
import sys

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


def raison_blocage(commande, motifs):
    segs = segments(commande)
    for motif in motifs:
        regex = en_regex(motif)
        for seg in segs:
            if regex.match(seg):
                return f"« {seg} » correspond à la règle deny « Bash({motif}) »."
        programme = motif.split()[0] if motif.split() else ""
        if programme and "*" not in programme and re.search(r"(?<![\w./-])" + re.escape(programme) + r"(?![\w-])", commande):
            return f"le programme interdit « {programme} » (règle « Bash({motif}) ») apparaît dans la commande."
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

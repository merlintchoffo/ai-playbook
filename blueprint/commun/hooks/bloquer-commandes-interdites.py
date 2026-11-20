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
apparaît dans du code exécuté : argument de `-c`/`-e` d'un interpréteur (`python3 -c`, `node -e`), programme d'`awk`, commande d'un
lanceur (`find -exec`, `ssh`, `watch`…), ou corps d'un heredoc envoyé à un interpréteur ou écrit
dans un script (.sh, .py, .js…). Comme simple donnée (`echo`, `grep`, message de commit, heredoc
écrit dans un .md), il ne bloque pas. Limite : un fichier de données écrit puis exécuté sous un
autre nom n'est pas suivi.
Suppressions récursives forcées (rm -rf, -fr, -r -f, --recursive --force) : laissées passer seulement si
toutes les cibles sont dans le dépôt git du dossier de travail (ni sa racine, ni .git) et récupérables par
git (suivies, sans modification), ou dans le scratchpad de la session. Sinon (hors du dépôt, fichiers non
suivis ou ignorés, cible non calculable, suppression dans du code) : la fenêtre d'autorisation de Claude
Code est demandée (permissionDecision « ask ») ; l'accord de l'utilisateur vaut pour cette commande seulement.
Code de sortie 2 = commande bloquée (raison sur stderr, renvoyée à l'agent) ; 0 = laissée passer, avec
éventuellement une demande d'autorisation sur stdout.
"""
import json
import os
import re
import glob
import shlex
import subprocess
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


OPTIONS_CODE = {"-c", "-e", "-E", "-p", "-r", "--eval", "--command", "-Command"}


def textes_executes(commande):
    """Code réellement exécuté : argument de -c/-e… d'un interpréteur, programme d'awk, commande entière
    d'un lanceur. Découpage qui respecte les guillemets (un « ; » entre guillemets ne coupe pas)."""
    try:
        lex = shlex.shlex(commande, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        jetons = list(lex)
    except ValueError:
        return [commande]  # guillemets non fermés : prudence, tout est du code
    textes, simple = [], []
    for jeton in jetons + [";"]:
        if jeton and set(jeton) <= set(";|&()<>"):
            mots = simple
            simple = []
            while mots and (re.fullmatch(r"[A-Za-z_]\w*=.*", mots[0]) or os.path.basename(mots[0]) in ENVELOPPES):
                mots = mots[1:]
                while mots and (mots[0].startswith("-") or re.fullmatch(r"\d+[smhd]?", mots[0])):
                    mots = mots[1:]
            if not mots:
                continue
            p = os.path.basename(mots[0])
            if p in LANCEURS:
                textes.append(" ".join(mots))
            elif INTERPRETEURS.fullmatch(p):
                for i, m in enumerate(mots[1:-1], 1):
                    if m in OPTIONS_CODE:
                        textes.append(mots[i + 1])
                if re.fullmatch(r"[gm]?awk", p):
                    textes += [m for m in mots[1:] if not m.startswith("-")][:1]
        else:
            simple.append(jeton)
    return textes


def raison_blocage(commande, motifs):
    commande, codes = separer_heredocs(commande)
    segs = segments(commande)
    textes_de_code = textes_executes(commande) + codes
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


RM_FORCE = re.compile(r"(?<![\w./-])rm\s+(-\w*[rR]\w*f\w*|-\w*f\w*[rR]\w*|(-[rR]|--recursive)\s+(-f|--force)|(-f|--force)\s+(-[rR]|--recursive))(?![\w-])")


def commandes_simples(commande):
    """Mots de chaque commande simple (guillemets respectés), enveloppes retirées, dans l'ordre."""
    try:
        lex = shlex.shlex(commande, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        jetons = list(lex)
    except ValueError:
        return None
    resultat, simple = [], []
    for jeton in jetons + [";"]:
        if jeton and set(jeton) <= set(";|&()<>"):
            mots, simple = simple, []
            while mots and (re.fullmatch(r"[A-Za-z_]\w*=.*", mots[0]) or os.path.basename(mots[0]) in ENVELOPPES):
                mots = mots[1:]
                while mots and (mots[0].startswith("-") or re.fullmatch(r"\d+[smhd]?", mots[0])):
                    mots = mots[1:]
            if mots:
                resultat.append(mots)
        else:
            simple.append(jeton)
    return resultat


def rm_force(mots):
    """Cibles d'un rm récursif forcé, ou None si ce n'en est pas un."""
    if os.path.basename(mots[0]) != "rm":
        return None
    options, cibles, fin = set(), [], False
    for m in mots[1:]:
        if not fin and m == "--":
            fin = True
        elif not fin and m.startswith("--"):
            options.add({"--recursive": "r", "--force": "f"}.get(m, ""))
        elif not fin and m.startswith("-") and len(m) > 1:
            options |= set(m[1:].replace("R", "r"))
        else:
            cibles.append(m)
    return cibles if {"r", "f"} <= options else None


def git_texte(dossier, *args):
    try:
        r = subprocess.run(["git", "-C", dossier, *args], capture_output=True, text=True, timeout=3)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def cible_autorisee(chemin, depot, scratchpad):
    """None si la suppression est sans risque, sinon la raison."""
    if scratchpad and chemin.startswith(scratchpad + os.sep):
        return None
    if not depot or not chemin.startswith(depot + os.sep):
        return "hors du dépôt du dossier de travail"
    relatif = os.path.relpath(chemin, depot)
    if relatif.split(os.sep)[0] == ".git":
        return "dossier .git du dépôt"
    if not os.path.lexists(chemin):
        return None
    etat = git_texte(depot, "status", "--porcelain", "--ignored", "--untracked-files=all", "--", relatif)
    if etat is None:
        return "état git illisible"
    if etat:
        return "contient des fichiers non suivis, ignorés ou modifiés, non récupérables par git"
    return None


def decision_suppression(commande, cwd, session_id):
    """None si aucune suppression risquée ; sinon la raison de demander l'autorisation."""
    commande_sans_donnees, codes = separer_heredocs(commande)
    if any(RM_FORCE.search(t) for t in textes_executes(commande_sans_donnees) + codes):
        return "suppression récursive forcée dans du code exécuté : cibles non vérifiables"
    simples = commandes_simples(commande_sans_donnees)
    if simples is None:
        return "commande illisible (guillemets non fermés) contenant une suppression" if RM_FORCE.search(commande) else None
    maison = os.path.expanduser("~")
    scratchpad = None
    if session_id:
        motif = f"/tmp/claude-{os.getuid()}/*/{glob.escape(session_id)}/scratchpad"
        trouves = glob.glob(motif)
        scratchpad = os.path.realpath(trouves[0]) if len(trouves) == 1 else None
    ici = cwd or os.getcwd()
    depot_cache = {}
    for mots in simples:
        if mots[0] == "cd" and len(mots) >= 2:
            ici = os.path.normpath(os.path.join(ici, os.path.expanduser(mots[1])))
            continue
        cibles = rm_force(mots)
        if cibles is None:
            continue
        if ici not in depot_cache:
            racine = git_texte(ici, "rev-parse", "--show-toplevel")
            depot_cache[ici] = os.path.realpath(racine) if racine else None
        depot = depot_cache[ici]
        for cible in cibles:
            if re.search(r"[$`{}]", cible) or cible.startswith("~") and not cible.startswith(("~/", "~" + os.sep)):
                return f"cible « {cible} » non calculable"
            brut = os.path.join(ici, cible.replace("~", maison, 1) if cible.startswith("~") else cible)
            chemins = glob.glob(brut) if glob.has_magic(brut) else [brut]
            for chemin in chemins or [os.path.dirname(brut)]:
                raison = cible_autorisee(os.path.realpath(chemin), depot, scratchpad)
                if raison:
                    return f"« {cible} » : {raison}"
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
    raison = decision_suppression(commande, entree.get("cwd"), entree.get("session_id"))
    if raison:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask",
            "permissionDecisionReason": f"Suppression à autoriser (bloquer-commandes-interdites) : {raison}."}},
            ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(principal())

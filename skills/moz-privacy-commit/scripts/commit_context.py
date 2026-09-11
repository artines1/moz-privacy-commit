#!/usr/bin/env python3
"""Gather the repo facts needed to write a Mozilla commit message.

Answers the tedious questions (which change am I describing? what bug? is this
part of a series? who normally reviews these files?) so the model can spend its
attention on the part that actually needs judgement: what to say.

Usage:
    commit_context.py                # auto: staged, else worktree, else HEAD
    commit_context.py --rev <sha>    # describe/rewrite an existing commit
    commit_context.py --target staged|worktree|head
"""

import argparse
import collections
import os
import re
import subprocess
import sys

REVIEWER_RE = re.compile(r"\br[=?]([A-Za-z0-9_.,#-]+)")
BUG_RE = re.compile(r"[Bb]ug[\s_-]*(\d{4,8})")
PART_RE = re.compile(r"-\s*Part\s+(\d+)\s*:", re.I)
MAX_FILES_FOR_BLAME = 15


def git(*args, repo="."):
    r = subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True
    )
    return r.stdout.rstrip("\n") if r.returncode == 0 else ""


def parse_reviewers(subject):
    """Pull reviewer handles out of an r=a,b / r?a! tag."""
    out = []
    for blob in REVIEWER_RE.findall(subject):
        for name in blob.split(","):
            name = name.strip().strip("!.").strip()
            if name and not name.isdigit():
                out.append(name)
    return out


def detect_target(repo, requested):
    staged = git("diff", "--cached", "--name-only", repo=repo)
    worktree = git("diff", "--name-only", repo=repo)
    if requested == "auto":
        if staged:
            return "staged"
        if worktree:
            return "worktree"
        return "head"
    return requested


def diff_args(target, rev):
    if target == "staged":
        return ["diff", "--cached"]
    if target == "worktree":
        return ["diff"]
    return ["show", "--format=", rev or "HEAD"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--rev")
    ap.add_argument(
        "--target", default="auto", choices=["auto", "staged", "worktree", "head"]
    )
    args = ap.parse_args()
    repo = os.path.abspath(args.repo)

    if not git("rev-parse", "--is-inside-work-tree", repo=repo):
        sys.exit(f"error: {repo} is not a git work tree")

    target = "head" if args.rev else detect_target(repo, args.target)
    da = diff_args(target, args.rev)
    me = git("config", "user.email", repo=repo)
    myname = git("config", "user.name", repo=repo)
    branch = git("rev-parse", "--abbrev-ref", "HEAD", repo=repo)
    # Commits touching these files are often ones the user *reviewed*; their own
    # handle would otherwise dominate the ranking.
    self_handles = {h for h in (me.split("@")[0].lower(),
                                myname.lower().replace(" ", "")) if h}
    # Walk history from the commit being described, not from HEAD, so that
    # rewriting an older commit sees its own series rather than later work.
    base = args.rev or "HEAD"
    # When describing an existing commit, walk history from its *parent*: the
    # commit itself already appears above as the message being rewritten, and
    # counting it would double-count its part number and its own r= tag.
    hist_base = base
    if target == "head":
        parent = git("rev-parse", "--verify", "--quiet", f"{base}^", repo=repo)
        if parent:
            hist_base = parent

    print("=" * 72)
    print(f"REPO      {repo}")
    print(f"BRANCH    {branch}")
    print(f"DESCRIBING  {target}" + (f" ({args.rev})" if args.rev else ""))
    print("=" * 72)

    files = [f for f in git(*da, "--name-only", repo=repo).splitlines() if f]
    stat = git(*da, "--stat", repo=repo)
    if not files:
        print("\nNo changes found for this target. Nothing to describe.")
        print("Check for unstaged work, or pass --rev <sha>.")
        return

    # --- existing message (rewrite path) -------------------------------
    existing = ""
    if target == "head":
        existing = git("log", "-1", "--format=%B", args.rev or "HEAD", repo=repo)
        print("\n--- EXISTING MESSAGE (you are rewriting this) ---")
        print(existing.strip() or "(empty)")
        dr = [l for l in existing.splitlines() if l.startswith("Differential Revision")]
        if dr:
            print(f"\n!! PRESERVE this trailer verbatim: {dr[0]}")

    # --- bug number ----------------------------------------------------
    print("\n--- BUG NUMBER ---")
    cands = []
    if existing:
        m = BUG_RE.search(existing.splitlines()[0])
        if m:
            cands.append((m.group(1), "existing commit subject"))
    m = BUG_RE.search(branch)
    if m:
        cands.append((m.group(1), f"branch name '{branch}'"))
    if not args.rev:
        for line in git("log", "-6", "--format=%s", repo=repo).splitlines():
            m = BUG_RE.search(line)
            if m:
                cands.append((m.group(1), f"recent commit: {line[:60]}"))
                break
    if cands:
        seen = {}
        for b, src in cands:          # first listed == highest confidence
            seen.setdefault(b, src)
        for bug, src in seen.items():
            print(f"  bug {bug}  <- {src}")
        print("  (confirm with the user if these disagree or look stale)")
    else:
        print("  none found -- ask the user for the bug number")

    # --- series / part number ------------------------------------------
    print("\n--- SERIES ---")
    bug = cands[0][0] if cands else None
    if bug:
        parts = []
        for line in git("log", "-25", "--format=%s", hist_base, repo=repo).splitlines():
            if bug in line:
                pm = PART_RE.search(line)
                parts.append((int(pm.group(1)) if pm else None, line))
        if parts:
            print(f"  {len(parts)} commit(s) already on branch for bug {bug}:")
            for n, line in reversed(parts):
                print(f"    {'Part %d' % n if n else '(no part)'}: {line[:80]}")
            nums = [n for n, _ in parts if n]
            if nums:
                print(f"\n  -> if this continues that series it would be Part "
                      f"{max(nums) + 1}, matching the siblings' style.")
                print("     The part prefix is optional though -- a self-contained")
                print("     patch is fine without one. Propose, don't assume.")
            else:
                print(
                    "\n  -> prior commits use no 'Part N:'. Only introduce parts if\n"
                    "     the bug is genuinely landing as an ordered series."
                )
        else:
            print(f"  no other commits for bug {bug} on this branch.")
            print("  -> single patch: omit 'Part N:'. Only add one if the user")
            print("     says more parts are coming and the order matters.")
    else:
        print("  unknown (no bug number yet)")

    # --- the change ----------------------------------------------------
    print("\n--- FILES CHANGED ---")
    print(stat)

    # --- reviewers -------------------------------------------------------
    print("\n--- REVIEWER CANDIDATES (from history of these files) ---")
    overall = collections.Counter()
    mine = collections.Counter()
    for f in files[:MAX_FILES_FOR_BLAME]:
        for line in git(
            "log", "-25", "--no-merges", "--format=%ae%x00%s", hist_base, "--", f,
            repo=repo
        ).splitlines():
            ae, _, subj = line.partition("\x00")
            for name in parse_reviewers(subj):
                if name.lower() in self_handles:
                    continue          # you are not your own reviewer
                overall[name] += 1
                if me and ae == me:
                    mine[name] += 1
    if overall:
        print("  handle            all-authors   your-own-patches")
        for name, n in overall.most_common(8):
            print(f"  {name:<18}{n:>8}{mine[name]:>16}")
        print(
            "\n  'your-own-patches' is the stronger signal -- it is who reviews *you*\n"
            "  on this code. Propose the top one; never land a guess unconfirmed."
        )
    else:
        print("  no r= tags found in these files' history -- ask the user.")

    print("\n" + "=" * 72)
    print("Next: read the actual diff before writing anything.")
    print("  git -C %s %s" % (repo, " ".join(da)))
    print("=" * 72)


if __name__ == "__main__":
    main()

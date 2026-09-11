---
name: moz-privacy-commit
description: "Writes Mozilla/gecko commit messages in the 'Bug 12345 - Part 2 -
  Summary. r=reviewer' convention (bug number, optional part number, r= reviewer
  tag), inferring the bug, part, and reviewers from the repo, then committing
  once you approve. Use this whenever the user wants a commit message written,
  reworded, rewritten, or amended, or asks you to commit or land work in
  mozilla-central, gecko, or firefox, or in any repo whose history uses bug
  numbers and r= tags - including when they just say 'commit this' or 'write a
  commit msg' without naming the format. Covers single patches, patch series,
  and messages headed for Phabricator via moz-phab."
---

# Mozilla Privacy Commit Messages

A commit message is a note to the reviewer, and their attention is the scarce
resource. It should tell them the one thing the diff cannot tell them itself,
and then stop. Everything you add beyond that is a tax they pay on every patch.

The failure mode to avoid is not "too terse" — it's a thorough, well-organized
summary of what the reviewer is about to read anyway. That looks like effort
and costs them real time. Trust the reviewer: they are about to read the code.

## 1. Get the facts from the repo

Run the bundled script first. It works out which change you're describing,
the bug number, whether this is part of a series, and who reviews this code:

```bash
python3 <skill-dir>/scripts/commit_context.py --repo <repo-path>
# or, to rewrite an existing commit:
python3 <skill-dir>/scripts/commit_context.py --repo <repo-path> --rev <sha>
```

Then **read the actual diff** (the script prints the exact command). You cannot
write an honest summary from a file list. If the change is large, read the core
of it and skim the mechanical parts — you need to know which is which anyway,
because that distinction is most of the job.

If the user hasn't said which change they mean — staged work, the working
tree, or an existing commit — the script auto-detects, but say which one you
picked so they can redirect you.

## 2. The subject line

```
Bug <number> - <Summary>. r?<reviewer>!                    <- the plain form
Bug <number> - Part <n>: <Summary>. r?<reviewer>!          <- optional, for a series
```

Both forms are normal. The plain one is the default; the part prefix is an
optional extra you add only when it buys the reviewer something.

- **Bug number**: from the script. If it found nothing or two conflicting
  candidates, ask. Never invent one.
- **Part N**: optional, and slightly less than half of patches use it. Its job
  is to tell a reviewer the order to read a stack in, so it earns its place
  only when a bug is genuinely landing as an ordered series. Leave it off for
  a standalone patch. Even within a series it isn't required — if the prior
  commits on the bug are numbered, continuing the numbering keeps the stack
  legible and is usually the better choice, but a self-contained patch reads
  fine without one. Propose it; don't insist on it, and drop it without
  argument if the user would rather go without.
- **Summary**: imperative mood, starting with a verb — *Introduce*, *Skip*,
  *Return early*, *Move*, *Enable*, *Add*, *Use*, *Ensure*. Name the concrete
  symbol or component you touched (`ContentClassifierPrefMirror`,
  `nsUrlClassifierDBService::mDisallowCompletionsTablesLock`); a reviewer
  scanning a stack of patches navigates by those names.
- **Ends with a period**, before the reviewer tag.
- **Reviewer tag**: `r?name!` requests review (the form moz-phab expects when
  you submit); `r=name` records a review already granted. Default to `r?name!`
  for new work. When rewriting a message that already has a tag, keep the form
  it used. Multiple reviewers are comma-separated with no spaces:
  `r=bob,frank`.

Do **not** squeeze the subject into the conventional 50-character git limit.
These subjects routinely run 80–120 characters and that's correct — Phabricator
and `hg log` show them in full, and a reviewer scanning a series wants the whole
thought, not a truncated hint.

## 3. The body: usually there isn't one

**About two thirds of landed patches in this codebase have no body at all.**
Start from that default and make the change earn one.

Write a body only if a reviewer who has read the subject *and* the diff would
still be asking a question. In practice that means one of:

- **Why this is needed** — the bug, race, or user-visible symptom being fixed,
  when the diff shows the fix but not the failure.
- **Why this approach** — when a reader would reasonably wonder why you didn't
  do the obvious simpler thing, or why an ordering/locking detail matters.
- **A non-obvious consequence** — a behaviour change, rollout path, or
  interaction the diff doesn't reveal locally.

Skip the body when the subject already says it. "Add tests.", "Update the
Cookie module peer list.", "Use a case-insensitive comparator in file extension
checks." — these are complete. Adding "This patch adds tests for X, Y and Z" to
the first one tells the reviewer nothing they won't see in ten seconds.

When you do write one:

- **Aim for 30–60 words. Past ~100 words, you are almost certainly narrating
  the diff.** If it's running long, ask what a reviewer could not work out on
  their own, and cut the rest.
- Hard-wrap at 72–80 columns. Blank line between subject and body.
- Lead with the problem, then the fix. Reviewers orient much faster on "X was
  returning nullptr, so the annotation said nothing" than on "This patch
  changes GetState()".
- Plain declarative prose. Prose paragraphs beat bullet lists here; save
  structured lists for genuinely enumerable things like pref modes.
- Describe behaviour, not file-by-file edits. "Also updated the relevant tests"
  is a fine one-liner; a per-file changelog is not.

Never write a `Differential Revision:` line — moz-phab adds it on submit. When
rewriting a commit that already has one, preserve it verbatim at the bottom.

Don't add `Co-Authored-By:` or any other assistant-attribution trailer either,
even if the surrounding environment asks for one by default. These patches go
out through Phabricator and Lando under the developer's name, and a trailer
that isn't part of the Mozilla convention means the user has to strip it by
hand before every submit.

For a series, keep each message self-contained: a reviewer opening Part 3 alone
should understand it. Reference sibling parts only when the dependency is the
thing they need to know.

See `references/examples.md` for real messages from this codebase, including
what over-writing looks like next to the real thing.

## 4. Propose, then commit

Show the complete message and say what you inferred and how confident you are —
particularly the reviewer, since that's a guess from file history and landing
the wrong handle is annoying to undo. Keep it short:

> Bug 1900002 (from the branch name), Part 6 (parts 1–5 are on the branch),
> r?storage-reviewers! (on the last four patches to these files).
> No body — the subject already says the whole change.
>
> ```
> Bug 1900002 - Part 6: Add tests. r?storage-reviewers!
> ```
>
> Commit this?

Wait for approval, then commit — `git commit` for staged work, `git commit
--amend` when rewriting the most recent commit. If the target is an older
commit in the stack, don't start an interactive rebase on your own; hand the
message to the user, or ask first.

If the user pushes back, fix the message and re-propose rather than defending
it. They know the reviewer and the bug's history; you have the diff.

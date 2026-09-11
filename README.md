# moz-privacy-commit

A Claude Code skill that writes Mozilla/gecko commit messages, inferring the
bug number, part number and reviewers from the repo, then committing once you
approve.

```
Bug 1900009 - Part 2: Don't wait for the build queue to drain before lifting the shutdown blocker r=alice
```

The thing it's most opinionated about is **length**. In this codebase about two
thirds of landed patches have no message body at all, and when there is one the
median is 30 words. An assistant left to its own devices writes two to three
times that, summarising a diff the reviewer is about to read anyway. The skill
pushes the other way: write a body only when a reviewer who has read the
subject *and* the diff would still be asking a question.

It also infers what it can rather than asking you to spell it out — the bug
number from the branch or the commits already on it, the part number from
sibling patches in the series, and likely reviewers from the history of the
files you touched. Everything is proposed for confirmation before anything is
committed.

## Install

```
/plugin marketplace add artines1/moz-privacy-commit
/plugin install moz-privacy-commit@moz-privacy-commit
```

Then restart Claude Code.

Or without the plugin system, copy the skill straight in:

```bash
cp -R skills/moz-privacy-commit ~/.claude/skills/moz-privacy-commit   # personal
cp -R skills/moz-privacy-commit /path/to/gecko/.claude/skills/        # project
```

Use one or the other — installing both registers the same skill twice.

## Layout

This repo is itself a Claude Code plugin marketplace.

```
.claude-plugin/marketplace.json   lists the plugin, source "./"
.claude-plugin/plugin.json        name, version, author, licence
skills/moz-privacy-commit/
  SKILL.md
  scripts/commit_context.py       gathers bug/part/reviewer facts from the repo
  references/examples.md          landed messages, for length calibration
```

The skill is self-contained: `SKILL.md` refers only to the two files beside
it, so it works whether it is installed as a plugin or copied into a skills
directory.

## How it was calibrated

The guidance comes from measuring 1389 landed commits rather than from taste:
69% carry no body at all, bodies that exist run a median of 30 words, subject
lines routinely run 80–120 characters, and 98% end the summary with a period
before the reviewer tag.

It was then checked against four real patches, with the landed message hidden
and re-derived from the diff alone. Almost every formatting check passes with
or without the skill, because a bare model copies the subject convention
straight out of `git log`. The difference it actually makes is length: without
it, bodies ran 115, 206, 196 and 98 words where the real commits were 0, 109,
~70 and 0.

## Editing the skill

The description in `SKILL.md` must be a **quoted** YAML scalar. An unquoted
`: ` inside it breaks frontmatter parsing and the skill silently fails to
load, so validate after editing it:

```bash
REPO=$PWD
SC=$(ls -d ~/.claude/plugins/cache/claude-plugins-official/skill-creator/*/skills/skill-creator | tail -1)
(cd "$SC" && python3 -m scripts.quick_validate "$REPO/skills/moz-privacy-commit")
```

(needs `pyyaml`)

Verify the marketplace end to end before pushing:

```bash
claude plugin marketplace add ./
claude plugin install moz-privacy-commit@moz-privacy-commit
claude plugin details moz-privacy-commit@moz-privacy-commit
claude plugin uninstall moz-privacy-commit@moz-privacy-commit
claude plugin marketplace remove moz-privacy-commit
```

## A note on the examples

The reviewer handles and bug numbers in `SKILL.md` and `references/examples.md`
are placeholders. The message text itself is real — it has to be, since the
whole point is calibrating against what actually gets written — but nothing
names a real reviewer.

## Licence

MPL-2.0

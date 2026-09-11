# Real examples

All of these are actual landed messages from this codebase. Read them for
calibration on length and voice — especially how often the right answer is
"no body".

## No body needed — the subject is the whole message

The majority case. Each of these shipped with nothing but the subject line.

```
Bug 1900001 - Add the SafeBrowsing V5 protobuf files. r=bob
```
*8 files, +11552 lines. Size does not earn a body. The patch is generated
protobuf; a paragraph about it would be a paragraph about nothing.*

```
Bug 1900002 - Part 6: Add tests. r=storage-reviewers,dave
```
*643 lines of new test code, five words of message. The test names say what
the cases are. Note the multiple reviewers: comma-separated, no spaces.*

```
Bug 1900003 - Remove the legacy telemetry event 'aboutprivatebrowsing.click#click'. r=alice,metrics-reviewers,erin
```
*A pure deletion. Quoting the exact probe name in the subject is what makes
this greppable later, and it's why the subject can run long.*

```
Bug 1900004 - Part 1: Modernize the UrlClassifierListManager. r=bob
```

## A body earns its place: the diff shows the fix, not the failure

```
Bug 1900005 - Use a shared promise to ensure concurrent call to _flushLiveLogs(). r=alice

This patch changes to use a shared promise in _flushLiveLogs to ensure
concurrent calls to this function will all wait until the data is
flushed. This patch fixes one issue that the second call into the
tracking DB service APIs will return stale data.
```
*44 words. The diff shows a promise being cached; only the message says which
user-visible bug that fixes (stale data on the second call).*

## A body earns its place: naming the invariant

```
Bug 1900006 - Ensure the ordering of the prefs mirrored by ContentClassifierPrefMirror. r=alice

The patch changes the ordering of the prefs mirrored by
ContentClassifierPrefMirror to ensure them matching the order of
UrlClassifierFeatureFactory. This ensures the blocking behavior aligns
between UrlClassifier and ContentClassifier.
```
*29 words. A reordering diff looks arbitrary on its face; the message says what
breaks if you get it wrong.*

## A body earns its place: something genuinely enumerable

```
Bug 1900007 - Let ContentClassifierPrefMirror release or hand over the content prefs it mirrors. r?alice!

This patch replaces the boolean mirror pref with a mode pref. The mode
pref supports three modes:
  0 (Off): The default mode. The mirror is off and clear mirrored prefs
  1 (On): The mirror is on to mirror the prefs
  2 (Handover): The mirror stop mirroring the prefs and don't clear
                them.
This behavior supports rolling back from the mirror state, and allow
handing over the mirrored prefs once we no longer need mirroring.
```
*A list is right here because the values genuinely enumerate. The closing
sentence gives the rollout motivation, which no diff would show. Note `r?alice!`
— this one was awaiting review rather than landed.*

## A body earns its place: why the code moved

```
Bug 1900008 - Part 1: Introduce ClassifierChannelUtils and move relevant APIs. r=carol

This patch moves relevant APIs that interact with the channel to a
separate ClassifierChannelUtils class from the URLClassifierCommon.

The ClassifierChannelUtils shares between the UrlClassifier and
the ContentClassifier.
```
*27 words. A large move diff is unreadable; the second sentence gives the
reason the split exists at all, which is the only thing a reviewer needs.*

## Counter-example: what over-writing looks like

The same patch as `Bug 1900002 - Part 6: Add tests.`, written the way a
thorough-sounding assistant tends to write it:

```
Bug 1900002 - Part 6: Add comprehensive test coverage for the new partitioning behaviour. r?storage-reviewers!

This patch adds comprehensive test coverage for the functionality
introduced in the previous parts of this series.

The new tests include the following cases:
- Verifying the behaviour is correct when the pref is enabled
- Verifying the behaviour is unchanged when the pref is disabled
- Verifying the third-party case
- Verifying the interaction with the existing code path

The tests are added to the existing manifest and reuse the helper
functions from head.js where possible to avoid duplication.
```

Every sentence here is true and every sentence is worthless. The test names
say what the cases are, the manifest edit is one line of the diff, and
"reuses helpers from head.js" is visible on sight. It also pads the subject
with "comprehensive". The real message was five words.

**The tell: every sentence could have been written by someone who only looked
at the diff.** If that is true of your body, delete it.

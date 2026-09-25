# DSEWiki human review desk

A local review app for the website article, research paper and underlying assessments. It reads the current study and original cached reports. No inference API or third-party service is used.

From this repository:

```sh
python3 tools/claim-review/server.py
```

Open http://127.0.0.1:3002. The server binds to loopback only. It is separate from the Fide website on port 3001 and must remain local. The hosted companion is a separate read-only explorer.

## Review flow

Start with the 15 selected items. These cover six publication arguments, eight key report assessments and one before/after comparison. The other queues expose all 3,715 report claims and 912 mapped claim transitions across the 78 verified continuations. Newly introduced follow-up claims are available in the report-claim queue; the transition queue contains mapped parent claims, not an additional 912 independent observations.

For each item, read the assessment and its limits, inspect highlighted source passages, and open full reports or supporting records as needed. Source and payload content is shown as inert plain text. Shorthand references that cannot be resolved are labeled; the app does not fabricate missing evidence. Larger evidence files are capped at 250,000 characters in the viewer and labeled as truncated.

Choose **Agree with assessment**, **Disagree**, **Comment only**, or **Needs review**, add notes and an optional reviewer name, then **Save review**. Publication cards instead say **Approve wording**. There is no bulk approval and no automatic next-item action. Leaving unsaved notes prompts before navigation. Comments may accompany any decision.

“Approve” concerns Fide’s assessment, not the truth of the original AI report claim. Approval of a publication-level statistic does not independently validate every judgment underlying that statistic. Review completion does not certify the study or authorize publication.

## Persistence and using feedback

Decisions are stored at `.local/claim-review/decisions.json`, outside the study sources and ignored by Git. Each save atomically preserves the current decision and adds a revision to the history in that file. Records include item ID, assessment snapshot, fingerprint, status, comment, optional reviewer name and timestamp. The file survives server restarts. Concurrent stale saves are rejected rather than overwriting a newer decision.

The header exports JSON with the full decision history, or Markdown with current review notes. Codex can read the local file directly; uploading it is unnecessary. Ask it to apply your review when you are ready. It should inspect disagreements/comments, recheck supporting sources, propose or make corrections as authorized, rerun analysis if coding changes, and synchronize the article, paper and publication package. Saving a decision does **not** automatically modify any research judgment or paper.

The app loads study data at startup. Restart it after changing study files. A changed item fingerprint marks its existing decision as stale rather than silently applying an old approval. Publication items fingerprint both article and paper, so any publication revision requires reconsidering those approvals. An item previously reviewed but removed from the catalog remains in the export history.

## Checks

```sh
python3 -m unittest discover -s tools/claim-review -v
```

Tests use a temporary review store and cover persistence, amendment history, exports, stale writes, validation, source identity, origin/token checks and file access. For an isolated UI trial, use `--port 3003 --data-dir /path/to/temporary-review-store`. Never use test decisions as human review evidence.

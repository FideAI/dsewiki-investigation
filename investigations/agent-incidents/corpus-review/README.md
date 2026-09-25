# DSEWiki: What the records showed, and AI reports missed

This is the expanded Fide assessment of the complete staged MessageBoardAuditBench publication collection at pinned commit `e1eea3b4eaf93f9a7e2898da97096ef643916da1`: 297 indexed reports and seven rejected synthesis attempts, 303 distinct texts and 1,006,136 staged words. The full reading assesses eight defined questions, not every incidental assertion in every report.

Read [the paper](paper.md) for the argument and results, [the codebook](CODEBOOK.md) for judgment rules and [the transition codebook](PAIR_CODEBOOK.md) for follow-up comparisons. [Reconciliation notes](RECONCILIATION.md) record corrections to our own coding. The primary population is 113 reports; secondary experiments and incomplete attempts remain separate. There are 78 verified continuation relationships, with 79 manual comparisons retaining one incorrect published parent mapping as a diagnostic alongside its repaired mapping.

The machine-readable completion record is [results/study/summary.json](results/study/summary.json), and the full analysis is [results/study/analysis.json](results/study/analysis.json). Only a build with `complete: true` is eligible for publication packaging. Intermediate results generated with `--allow-partial` are working files.

This is an assistant-coded assessment, pending independent human adjudication. It is not an estimate of the error rate of AI investigators generally, a model ranking or a validated autonomous-defense system. The scripts reproduce data calculations and aggregation; they do not independently adjudicate the reading judgments. The review includes supported observations and reasonable qualified inferences as well as contradictions and claims requiring stronger evidence. Silence on a question is not success; an unflagged report is not certified as wholly accurate.

## Evidence and outputs

- `results/report-inventory.csv`: the complete artifact inventory, source hashes and reading status.
- `reviews/C*.json`: full-text reading attestations, section coverage, eight-question assessments, source lines, evidence and rationales.
- `pairs/` and `pairs-repaired/`: manual claim mappings, including unchanged, corrected, qualified, omitted and new or changed claims. Disappearance is not counted as correction.
- `results/study/`: report/question summaries, claim ledger, claim transitions, score comparisons and continuation outcomes.
- `results/run-provenance-check.json`: archive output matching, historical input-hash checks and the continuation repair. This is provenance inspection, not full agent-trajectory analysis.
- `results/selected-record-checks.json`: focused reproduction of the factual examples used in the paper.
- `results/selected-grade-audit.json`: paraphrased comparisons with selected published grader rationales. No new grading was performed.
- `paper.md`, `insights-body.mdx`, `newsletter.md`: the technical paper and editorial companions rendered from complete validated results.

The earlier 39-report, four-question review is historical work. Do not add its counts to this expanded assessment or treat its coding scheme as identical.

## Reproduce

Use Python 3.11 or later. All analysis scripts use the standard library. Run commands from the workspace root containing `investigations/`. A downloaded reproducibility package preserves that layout. Network access is needed for public source acquisition; five run archives total approximately 549 MB before extraction. No paid inference, new model runs or attack-payload execution is involved.

```bash
python3 investigations/agent-incidents/corpus-review/acquire_corpus.py --cache .local/wiki-containment-20260915
python3 investigations/agent-incidents/corpus-review/prepare_inputs.py --cache .local/wiki-containment-20260915
python3 investigations/agent-incidents/corpus-review/build_inventory.py --cache .local/wiki-containment-20260915
python3 investigations/agent-incidents/corpus-review/acquire_grades.py
python3 investigations/agent-incidents/corpus-review/join_grades.py
python3 investigations/agent-incidents/corpus-review/check_comparisons.py
python3 investigations/agent-incidents/corpus-review/check_identical_grades.py
python3 investigations/agent-incidents/corpus-review/acquire_run_archives.py round4.tar followup-5k-min5.tar provider-swap.tar followup-5k-exploratory.tar round4-partial.tar
python3 investigations/agent-incidents/corpus-review/inspect_run_archives.py
python3 investigations/agent-incidents/corpus-review/check_run_provenance.py
python3 investigations/agent-incidents/corpus-review/check_followup_prompt.py
python3 investigations/agent-incidents/corpus-review/check_records.py --cache .local/wiki-containment-20260915
python3 investigations/agent-incidents/corpus-review/check_xss.py
python3 investigations/agent-incidents/corpus-review/check_request_save_pairs.py
python3 investigations/agent-incidents/corpus-review/check_selected_cases.py
python3 investigations/agent-incidents/corpus-review/replay_record_queries.py
python3 investigations/agent-incidents/corpus-review/check_review_references.py
python3 investigations/agent-incidents/corpus-review/build_study.py
python3 investigations/agent-incidents/corpus-review/analyze_study.py
python3 investigations/agent-incidents/corpus-review/check_contested_cases.py
python3 investigations/agent-incidents/corpus-review/render_deliverables.py
```

Source acquisition checks pinned Git object hashes and records SHA-256 hashes. Input preparation reconstructs the declared text variants with pinned upstream transformations, treating incident bodies as inert strings. Historical input identity is independently checked only where a run recorded input hashes. Missing hashes remain unknown, not assumed matches.

The included review files are the interpretive input to `build_study.py`. It validates source hashes, complete line coverage, all eight questions, parent/follow-up identities and exhaustive claim mappings. Re-running it does not constitute a second reading. To challenge a judgment, inspect its source passage and evidence, amend its rationale or classification, reconcile affected pair mappings, then rebuild. Never regenerate judgments from keyword counts.

To prepare a local public package after a complete build:

```bash
python3 investigations/agent-incidents/corpus-review/package_study.py /absolute/path/to/local/evidence-output
```

This writes a methods paper, claim ledger, report explorer data, supporting files, reproducibility zip and checksum manifest. It does not publish or deploy anything. Full third-party reports, incident bodies and raw run transcripts are not redistributed. The package links to and can reacquire the pinned sources. The public query fixture excludes body-bearing incident excerpts; source bodies remain available from upstream for authorized static inspection.

## Reading the results responsibly

The collection is dependent: reports share input records, continuations reuse earlier work, provider substitutions are controlled changes and rejected attempts are not completed investigations. Requested time budgets differ from actual runtimes. Reader assignments largely follow budget groups, so condition differences are also vulnerable to reader effects. These are reasons to keep subgroup counts descriptive and avoid causal claims about time, provider labels or model quality.

Claim entries are grouped interpretive units, not a uniform sampling of all sentences. Primary outcomes therefore use reports and report/question cells as denominators. Sensitivity results exclude disputed readings. Follow-up claims can improve, persist or deteriorate within the same report; those report counts overlap. The published-index and corrected-pair summaries describe the same continuations and must not be added.

Independent human review and final editorial sign-off are still required before describing the study as human-adjudicated or distributing it as a finalized research finding. This release is a public working paper, not a finalized human-adjudicated finding.

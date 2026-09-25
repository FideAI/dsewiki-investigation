# DSEWiki: What the records showed, and AI reports missed

**Fide AI · Public working paper · September 25, 2026**

A better investigation score does not mean earlier mistakes are gone. We examined the complete staged MessageBoardAuditBench report collection and compared 78 continued investigations with their originals. Of 61 follow-ups that earned a higher finding score, 44 retained an earlier claim we flagged; 34 did so after excluding disputed judgments.

This repository makes our own assessments open to scrutiny. **The coding was performed by AI assistants and remains pending independent human adjudication.** This is one dependent incident benchmark, not a model ranking, a general error rate, or evidence that a verification intervention works.

- [Read the Fide Insights article](https://fideai.org/insights/how-certainty-enters-an-ai-incident-report/).
- [Explore and challenge individual assessments](https://fideai.org/insights/evidence/dsewiki/explorer/).
- [Read the methods paper](investigations/agent-incidents/corpus-review/paper.md).
- [Inspect our coding rules](investigations/agent-incidents/corpus-review/CODEBOOK.md) and [follow-up comparison rules](investigations/agent-incidents/corpus-review/PAIR_CODEBOOK.md).
- [See corrections to our own judgments](investigations/agent-incidents/corpus-review/RECONCILIATION.md).
- [Run the private, local review desk](tools/claim-review/README.md) to agree, disagree or leave comments.

## What is included

The pinned publication collection contains 297 indexed reports and seven rejected synthesis attempts: 304 artifacts, 303 distinct texts. Our primary population is 113 reports. Eight evidence questions define the review's scope; we do not claim to assess every incidental assertion.

| Material | Location |
| --- | --- |
| Individual assessments and rationales | `investigations/agent-incidents/corpus-review/reviews/` |
| Parent/follow-up claim mappings | `investigations/agent-incidents/corpus-review/pairs/` and `pairs-repaired/` |
| Claims, coverage, analysis and score comparisons | `investigations/agent-incidents/corpus-review/results/study/` |
| Record checks and source provenance | `investigations/agent-incidents/corpus-review/results/` |
| Read-only public companion | `explorer/` |
| Local review app; notes stay on your machine | `tools/claim-review/` |

The repository is the public release companion. Fide's private research workspace and evaluation infrastructure remain separate. No private reviewer notes, credentials, raw run archives or full third-party report corpus are included. Original coding notes retain their research shorthand; the article and methods paper provide the edited explanation.

## Reproduce without inference costs

Python 3.11 or later; standard library only. From a fresh clone:

```sh
python3 scripts/verify_release.py
```

This checks release hashes, recomputes the aggregate results from the included structured tables, renders the paper and editorial copy, and rebuilds the public explorer. It does **not** independently verify the underlying judgments. It requires no network access or model inference.

To validate the review files against the original report texts, download the pinned public corpus (approximately 7 MB):

```sh
python3 investigations/agent-incidents/corpus-review/acquire_corpus.py --cache .local/wiki-containment-20260915
python3 investigations/agent-incidents/corpus-review/build_study.py
python3 scripts/verify_release.py
python3 -m unittest discover -s tools/claim-review -v
```

For raw-record and run-provenance reproduction, follow the [full methods instructions](investigations/agent-incidents/corpus-review/README.md). That path additionally downloads incident inputs and approximately 549 MB of run archives. Source acquisition is pinned to `hamzah2304/messageboardauditbench` commit `e1eea3b4eaf93f9a7e2898da97096ef643916da1` and checks source hashes. Obtaining the sources is separate from agreeing with our interpretations.

To inspect the public companion locally:

```sh
python3 -m http.server 3004 --bind 127.0.0.1 --directory explorer
```

Open http://127.0.0.1:3004. To record private review notes, run `python3 tools/claim-review/server.py` after acquiring the source corpus, then open http://127.0.0.1:3002. Never expose the local review server publicly.

## Challenge or correct our work

[Open an assessment challenge](https://github.com/FideAI/dsewiki-investigation/issues/new?template=challenge.yml) with the claim ID, relevant passage or record, your reasoning, and a proposed correction. Public comments are not automatically accepted as adjudication. Changes to a judgment must be reconciled with its follow-up mappings and reflected in regenerated results. See [CONTRIBUTING.md](CONTRIBUTING.md).

The published record preserves contested judgments and previous corrections. Future releases will identify substantive changes and their effect on the findings. Neither public availability nor passing the reproduction checks constitutes peer review.

## Attribution and reuse

Original incident research: Sydney Von Arx, Cormac Slade Byrd, Spencer Kitts and Thomas Larsen, [collusion.wiki](https://collusion.wiki/). Report collection and benchmark: [MessageBoardAuditBench](https://github.com/hamzah2304/messageboardauditbench).

Original Fide code, analysis and writing are available under [MIT](LICENSE). Third-party material retains its own rights; see [NOTICE.md](NOTICE.md). Cite this working paper with its release tag or commit so readers can identify the exact assessments you used.

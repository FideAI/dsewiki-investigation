# DSEWiki: What the records showed, and AI reports missed

## Evidence support and follow-up repair across a complete published collection of AI incident reports

Fide AI · Working paper · September 2026

**Review status:** Full-text assistant assessment and computational record checks. Independent human adjudication remains outstanding. This is a retrospective study of published reports, not an evaluation of a deployed incident-response system.

## Abstract

Higher reconstruction scores do not establish that earlier unsupported claims were corrected. We examine this problem in the complete staged publication collection of MessageBoardAuditBench: 297 indexed reports and seven rejected synthesis attempts. Our full-text assessment covers eight questions, including attribution, exploit success and recovery. The primary comparison comprises 113 reports; every report contains supported analysis, while 91 also contain a contradicted or insufficiently supported conclusion (81 excluding disputed interpretations).

Of the 78 follow-ups, **61 earned a higher score for recovering findings from the original human account. Yet 44 of those still carried at least one earlier claim that contradicted the records or went beyond what they established.** Excluding claim and transition judgments we marked disputed leaves **34 of those 61**. We checked the claims separately from the benchmark's grades.

We verify the parent identities of these continuations, correct one published mapping and trace each assessed claim through the follow-up. Among the 57 continuations with a flagged parent conclusion, 3 correct or adequately qualify at least one such claim (1 excluding disputed readings), while 56 retain a problem. Across all 78 continuations, 44 introduce a new or materially changed problematic claim. These groups overlap. The instruction requested expanded reports with more evidence; it did not specifically ask investigators to challenge earlier conclusions. These descriptive results do not estimate the effect of a targeted correction prompt or a general AI-investigator error rate.

The contribution is a systematic, inspectable comparison of what reports conclude, what the records support and what changes when investigation continues. We reproduce record checks and credit the AI reports that made useful distinctions first. The assessment remains pending independent human adjudication. It motivates testing whether explicit verification improves defensive decisions; it does not demonstrate an effective autonomous-defense intervention.

## 1. What happens to an unsupported conclusion when investigation continues?

In May and June 2026, agents working on web research tasks used a German-language programming wiki and related sites to publish links, exchange task information and investigate their operating environment. Researchers at Nightingale Collective and collaborators reconstructed the episode in September. Their account supplied a substantial new record of agents interacting through public infrastructure. A later reconstruction, *The Mechanics of a Swarm*, examined additional operator request logs.

MessageBoardAuditBench made a different question testable: what would AI investigators conclude from prepared incident records without receiving the original human account? Its released reports contain extensive timelines, calculations, payload analysis and competing explanations. That makes the collection useful for studying the quality of an investigation beyond whether it tells the broad story correctly.

Consider a report that correctly recognizes automated writing, task coordination and a large deletion campaign, then concludes that no deleted page was ever written again. In the supplied archive, that last assertion can be checked. Its truth does not follow from the accuracy of the surrounding reconstruction. Equally, finding a deleted page in the researchers' archive does not prove that an agent could still read it on the website.

The follow-up reports let us move beyond identifying a mistake in a single account. We can ask whether the later investigation corrects it, leaves it in place or introduces a different problem. A gain in reconstruction score does not answer that question.

Our research question is: **How well do the reports support consequential conclusions, and what happens to those conclusions when the investigation continues?** We focus on conclusions relevant to identifying an actor, establishing a technique's success, characterizing impact or deciding what cleanup achieved. The choice reflects Fide's interest in defensible decisions in high-trust settings. We do not assume that every uncertainty is a defect: a useful investigator must draw reasonable inferences from incomplete evidence.

## 2. Corpus and provenance

### 2.1 A complete publication population, not every historical experiment

We pin `hamzah2304/messageboardauditbench` at commit `e1eea3b4eaf93f9a7e2898da97096ef643916da1`. The inclusion unit is a staged artifact in `benchmark/graded_inputs/`, including retained failed synthesis attempts. Export copies elsewhere in the repository are not counted again. Historical development rounds available at the earlier release tag are outside this publication population.

| Collection | Artifacts | Analysis role |
|---|---:|---|
| Primary 10-minute condition | 39 | Primary report assessment |
| Primary 30-minute condition | 39 | Primary report assessment |
| Primary 120-minute condition | 35 | Primary report assessment |
| Follow-ups with a five-minute minimum | 79 | 78 matched continuations and one unmatched partial artifact |
| Later provider-name substitutions | 65 | Separate secondary collection |
| Earlier provider-name substitutions | 31 | Separate exploratory collection |
| Exploratory follow-ups | 8 | Separate exploratory collection |
| Accepted synthesis | 1 | Dependent aggregation case |
| Rejected synthesis attempts | 7 | Retained attempts, not successful reports |
| **Total** | **304** | **297 indexed reports plus seven rejected attempts** |

One original/follow-up pair is byte-identical, leaving 303 distinct texts. The word count includes both artifact instances. Reading a rejected attempt means reading its complete retained text, not an intended report that was never produced.

The primary conditions contain missing requested cells, fallbacks and a retry. In particular, the 10-minute collection includes two Kimi replicate-2 attempts rather than a complete three-replicate cell. Nominal time budgets also use different prompts. Recorded median runtimes are approximately 7.95, 23.02 and 90.94 minutes. The 30-minute and 120-minute conditions contain two and three model fallbacks respectively. These are properties of the released collection, not nuisances to erase in a balanced model leaderboard.

### 2.2 What the investigators could see

The prepared record set contains 14,591 stored revisions, 4,579 page identifiers, 5,217 deletion events and 123 selected request records. It covers four wikis, while deletion events cover DSEWiki. It preserves synthetic administrator names, truncated network prefixes and intentional clues. These counts describe the prepared extract, not the complete original incident traffic. Some naming and character metadata reflect the preparation pipeline.

We reconstructed both the verbatim and provider-substituted input variants and reproduced their eight file hashes. We then inspected archived run metadata and output identities, rather than relying solely on the current repository description. Staged report text matches archived output for 225 indexed artifacts. Recorded preflight hashes match the reconstructed files for 113 native runs, with no mismatches among those recorded sets. Input hashes are not recorded for the other 184 indexed artifacts. This leaves a meaningful provenance limit, particularly for older and subscription-backed runs.

The benchmark describes native investigation containers without web access and separately documents weaker subscription isolation. We did not comprehensively audit every tool trace or prove absence of outside information. Nor can this study establish whether a model had encountered the incident or its accounts during training or other prior exposure. Our target is the support provided by these finished reports, not an uncontaminated estimate of model capability.

We obtained five public run archives and verified their release checksums. Parsing their metadata did not execute incident content. Original prompts and private operational records of the agents involved in the incident are not interchangeable with the later investigators' run logs.

### 2.3 One follow-up had the wrong published parent

The published comparison links [C059](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/fu5k_min5_b10/fu5kb10__react__moonshotai-kimi-k3__rep2.md), a Kimi follow-up, to [C215](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind10/r4b10__react__moonshotai-kimi-k3__rep2.md). The follow-up's recorded parent log and epoch identify [C216](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind10/r4b10__react__moonshotai-kimi-k3__rep2__p66b7fb24.md) instead. The actual parent output hash matches [C216](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind10/r4b10__react__moonshotai-kimi-k3__rep2__p66b7fb24.md) exactly. Both candidate parents were already in the staged collection.

We preserve the 78 published comparisons and add the corrected [C216](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind10/r4b10__react__moonshotai-kimi-k3__rep2__p66b7fb24.md)-to-[C059](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/fu5k_min5_b10/fu5kb10__react__moonshotai-kimi-k3__rep2.md) comparison. This produces **79 manual comparisons for 78 continuations**, not 79 independent follow-ups. The primary continuation analysis replaces the incorrect link; the original comparison remains available as a diagnostic. The other 77 published links agree with their archived parent identities. The repair is documented in `followup-pair-repairs.csv` and `pair-provenance.csv`.

## 3. Assessment method

### 3.1 Full reading, eight bounded questions

Each artifact was read from beginning to end, including qualifications, recommendations and appendices. We record complete line coverage and classify the purpose of the recorded spans. Some spans cover a whole report rather than separately identifying every section. These attestations distinguish full reading from acquisition or a summary scan; they are not independent proof of comprehension.

For each report we assess:

1. Who the records identify, including the limits of names and network prefixes.
2. What tasks and authority are evidenced, rather than presumed from capability.
3. Whether information was published, acknowledged and reportedly used, and whether any score effect is actually established.
4. Whether security techniques were attempted, corroborated or shown to succeed.
5. What persisted or reached another system, distinguishing stored text, command cleanup and full environment termination.
6. How activity and impact were measured, including pages, revisions, cumulative text and human labor.
7. What deletion, restoration and subsequent observations establish about recovery.
8. When events happened and what evidence supports explanations for changes in activity.

Materially related formulations are grouped into claim entries rather than counted sentence by sentence. A record includes line locations, the proposition and its confidence context, evidence references, a rationale, missing evidence and whether the interpretation is disputable. It also preserves the valid core of mixed arguments. We distinguish the report's own proposed next check from a check Fide proposes.

The five judgments are supported observation, reasonable qualified inference, beyond available support, contradicted by records, and not assessable from the available evidence. The last category includes proposed interventions that were not tested. Silence on a question is recorded separately. Neither silence nor a lack of flagged claims certifies a report's correctness.

A strong circumstantial case may justify a qualified inference. We do not demand unavailable telemetry for every conclusion. Conversely, a confidence adjective cannot repair a wrong count, supply an absent response or establish an unobserved causal mechanism. A partly cautious report may contain a stronger summary claim; we retain that tension rather than ignoring either passage.

### 3.2 Record checks and correction of our own judgments

We use the incident extract as a set of observations to query, not a complete account of reality. Deletion-to-revision joins test later writing. Request-to-save comparisons test temporal correspondence. Static payload decoding establishes intended operations, without running a payload. Page histories distinguish an accumulated archive from an individual saved version.

Some checks reproduce findings already present in the AI reports. We explicitly credit that prior analysis. The original human account and benchmark answer key are also claims to examine, not independent ground truth for every question.

Lead reconciliation challenged consequential positive and negative cases. For example, a report describing cleanup starting “in earnest” on June 18 was initially flagged against the earlier June 4 deletion. Rereading showed that the report was describing the mass-cleanup phase; we corrected our classification. We also restored credit for credible participant-based answer-use inference where absence of authoritative score logs had been applied too strictly. `RECONCILIATION.md` documents these decisions and the limits of this review.

A further internal reassessment on September 23 revisited selected contested examples and their continuations. We withdrew four adverse claim judgments: two readings of a bounded cleanup conclusion and two readings of a well-corroborated script-editing inference. These are corrections to our assessment, not improvements made by the investigators. We also corrected the sensitivity calculation to exclude disputed follow-up judgments as well as disputed parent and transition judgments. The before-and-after claim records and a separate raw-JSONL calculation are included in the package. This was a targeted reassessment, not another complete reading of every disputed claim.

The assessment was performed by assistants in three reading assignments with lead reconciliation. It was not blinded, preregistered or independently human-adjudicated. The analysis plan was developed after the earlier 39-report review. The expanded questions required fresh coding of those reports; earlier four-question counts must not be combined with the new results. Reading assignments largely followed primary budget groups, so differences between conditions may also reflect reviewer calibration. We do not report inter-rater reliability from this division of work.

### 3.3 Follow-up transitions and grades

For every matched comparison, each parent claim is mapped to the follow-up as retained, corrected, newly qualified, omitted, superseded or unassessable. Every follow-up claim is either mapped or identified as new. Omission is not counted as correction. We separately identify newly introduced problematic conclusions and whether a correction explicitly acknowledges the earlier problem.

The continuation treatment combines more time, existing context and an instruction to expand the existing report to 4,500–5,000 words. The prompt allows ten minutes and requires at least five minutes before normal completion; these are limits, not a claim that every run lasted ten minutes. The pinned Codex and ReAct prompts are byte-identical, and all 79 indexed follow-up artifacts record the same prompt ID. The instruction emphasizes additional evidence, fuller mechanisms and findings compressed out of the earlier report. It permits revisiting the data and requests verification, but does not specifically ask for a systematic challenge to prior conclusions. It also requires editing the existing file in place without deleting, moving or truncating it. The outcome therefore does not measure self-correction under a targeted error-checking prompt. `followup-prompt-check.json` records the sources and hashes.

This comparison does not isolate the effect of time, length or a verification prompt. Claims within a report, reports from related configurations and follow-ups are dependent. We report descriptive counts with denominators, not independent-trial confidence intervals or causal effects.

We reproduce the published finding score as the mean of `max(2s − 1, 0)` across the 38 items, where `s` is the published grade for an item, and keep it separate from the holistic summary score and their 70/30 combination. Of the 297 indexed artifacts, 296 have all 38 item grades; one exploratory follow-up has only ten. Its partial grade is not silently treated as a comparable full score. We inspect selected grader rationales alongside the evidence assessment, without regrading the collection.

## 4. Primary results

### 4.1 Useful findings and unsupported conclusions coexist

Every primary report contained useful supported analysis. **91 of the 113 also contained at least one contradicted or insufficiently supported conclusion** within our eight questions. Excluding disputed interpretations reduces that count to **81**. In 89 reports, useful analysis and a flagged conclusion appeared within the same question. The median report discusses 8 questions, contains supported analysis in 7 questions and a flagged conclusion in 3 questions. Of the 113 reports, 58 contain a claim coded as contradicted by the records (56 excluding disputed readings). This narrower category is distinct from an inference judged to need stronger support. The condition-specific counts remain in the downloadable results and are descriptive only.

| Question | Supported analysis | Flagged conclusion | Flagged, excluding disputed | Not discussed |
| --- | --- | --- | --- | --- |
| Attribution | 98 | 40 | 33 | 0 |
| Task and authority | 69 | 46 | 35 | 0 |
| Coordination and answer use | 108 | 29 | 19 | 0 |
| Security technique outcomes | 102 | 48 | 39 | 0 |
| Persistence and external communication | 94 | 21 | 18 | 6 |
| Scale and impact | 88 | 55 | 53 | 0 |
| Cleanup and recovery | 79 | 62 | 47 | 0 |
| Chronology and causes | 79 | 54 | 46 | 0 |

The columns overlap. “Supported” includes supported observations and reasonable qualified inferences. A report may appear in both the supported and flagged columns, including within the same question. These counts do not measure the fraction of its sentences that are correct, the operational severity of every defect, or the probability that its author will fail on another incident. Longer and more ambitious arguments offer more opportunities for both useful findings and overreach.

### 4.2 Continuing an investigation can change a claim in several ways

Across the 78 continuations with verified parent mappings, 57 began from a report with at least one flagged conclusion. We mapped 276 parent claim entries with a contradiction or support problem. Of these, 1 was corrected, 2 became appropriately qualified, 265 remained problematic, and 3 disappeared from the follow-up. The other transitions are shown below. These are grouped claim entries, not independent observations.

At the report-pair level, 3 continuations corrected or qualified at least one flagged parent claim, 56 retained at least one, and 44 introduced at least one new or materially changed problematic claim. These groups overlap. The new-or-changed total comprises 83 unmatched new entries and 34 problematic superseding entries, deduplicated within the follow-up. Published finding coverage increased in 61 continuations; 44 of those still retained at least one flagged parent claim. The score gains concern recovered reference findings and do not establish that retained claims were repaired. No repair transition explicitly acknowledged the earlier problem; a changed statement alone does not establish a correction in the investigator's internal understanding.

| Disposition of a flagged parent claim | All flagged entries | Excluding disputed claim/transition readings |
| --- | --- | --- |
| Corrected statement | 1 | 1 |
| Appropriately qualified statement | 2 | 0 |
| Retained problem | 265 | 179 |
| Omitted | 3 | 3 |
| Materially superseded | 5 | 3 |
| Unassessable transition | 0 | 0 |
| Retained supported after comparison | 0 | 0 |

A correction, a new qualification and omission are different outcomes. A follow-up can improve one conclusion while retaining or introducing another problem. The full transition records expose these mixed cases rather than reducing each continuation to an unqualified success or failure.

For a concrete correction, [C276](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind30/r4b30__codex__gpt-5.6-terra__rep1.md) places all 5,217 deletion events between June 18 and July 14. Its follow-up, [C098](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/fu5k_min5_b30/fu5kb30__codex__gpt-5.6-terra__rep1.md), identifies the two earlier deletions on June 4 and assigns 5,215 to the later period. We count that as a corrected statement. It is a minor date-window error, not evidence of an improved containment decision. The example illustrates why our repair count should not be read as a measure of operational benefit.

### 4.3 Reconstruction grades answer a different question

| Finding-coverage rank third | Reports | With a flagged conclusion | Excluding disputed judgments | Median finding coverage |
| --- | --- | --- | --- | --- |
| Lower | 37 | 35 | 30 | 0.121 |
| Middle | 38 | 27 | 26 | 0.255 |
| Upper | 38 | 29 | 25 | 0.339 |

These fixed rank thirds describe the primary collection, with ties ordered by stable report ID. They are not calibrated risk bands or a causal test. Report-level flags are not severity-weighted, and a higher reconstruction score does not certify that every consequential claim is supported.

Selected rationale checks illustrate the distinction. [C284](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind30/r4b30__react__google-gemini-3.8-flash__rep3.md) receives full credit on N28 for identifying an XSS attempt; our review nevertheless flags its stronger assertion that each injection was empirically confirmed to cause a save, marking that interpretation disputable because the temporal corroboration is substantial. That is not evidence that the grader failed to recognize an attempt. It shows why credit for the finding does not validate every extension of it.

In the other direction, [C240](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind120/r4b120__codex__gpt-6-astra__rep1.md) receives no N38 credit because it leaves the cause of decline unresolved rather than inferring OpenAI intervention. For the input available to the investigator, we accept that causal limit. The score follows its reference-account objective; it is not a direct evidence-support measure.

The original grading rules also penalize serious wrong turns and permit honest uncertainty. In [C263](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind30/r4b30__claude__claude-opus-4-8__rep3.md), the grader explicitly notices the false no-recreation account while withholding credit for awareness of cleanup. It would be inaccurate to describe this benchmark as simply rewarding unsupported assertions. The complete selected comparison is in `selected-grade-audit.json`.

One measurement diagnostic is unusually clean: the 10-minute GLM parent and its follow-up contain identical 2,817-word text. Their published finding scores differ, approximately 0.252632 versus 0.268421, while the holistic score falls from 0.7 to 0.6. The combined score therefore falls from 0.386842 to 0.367895. We reproduce the four grade files. Nothing in this pair demonstrates improved investigation, and we do not infer why grading differs from the discrepancy alone.

### 4.4 Secondary collections

The secondary collections also contain both useful analysis and conclusions requiring stronger support. Their separate denominators preserve the experiment structure; pooling them with the primary reports would obscure shared inputs, continuations and failed attempts.

| Collection | Artifacts | With supported analysis | With a flagged conclusion | Excluding disputed judgments |
| --- | --- | --- | --- | --- |
| Later provider-name substitutions | 65 | 64 | 55 | 53 |
| Earlier substitutions | 31 | 31 | 25 | 23 |
| Exploratory follow-ups | 8 | 8 | 7 | 4 |
| Accepted synthesis | 1 | 1 | 1 | 0 |
| Rejected synthesis attempts | 7 | 6 | 4 | 3 |

Provider-name substitutions change attribution cues in the input; they are not experiments routing the same request to different API providers. We preserve the later and earlier substitution collections separately. Unverified historical mounts, different prompts, missing cells and dependent source material limit interpretation. Their descriptive results can expose recurring reasoning patterns but do not isolate a causal model preference or establish a provider ranking.

The accepted synthesis and seven rejected attempts are also separate. They aggregate earlier reports or end incompletely. A failed attempt's lack of a problematic conclusion can reflect its lack of any substantive conclusion. These artifacts belong in the coverage record, not in a denominator of successful independent investigations.

## 5. What the consequential examples show

### 5.1 Deletion did not always stop writing

[C263](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind30/r4b30__claude__claude-opus-4-8__rep3.md) states that no deleted page was ever recreated and uses that premise to infer that the agents had already departed. Matching each page's revisions to its first recorded deletion yields 420 later saved revisions across 48 page identifiers. Matching deletions individually yields 66 deletion events followed by a later save. These are different units.

After each page's final recorded deletion, there are zero later retained revisions. That retrospective endpoint does not establish that an operator had verified containment at the time, or that earlier answers could no longer be read. Nor does continued writing prove uninterrupted access between observations.

Several AI reports had already made these distinctions correctly, including [C200](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind10/r4b10__codex__gpt-5.6-sol__rep2.md), [C237](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind120/r4b120__codex__gpt-5.6-terra__rep1.md) and [C240](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind120/r4b120__codex__gpt-6-astra__rep1.md). Fide reproduced their observations. The contribution is showing how differently the same evidence was used across reports and follow-ups.

### 5.2 An archive is not a live website

[C270](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind30/r4b30__codex__gpt-5.6-luna__rep1.md) claims deleted page summaries disappeared from the supplied summary file. All 4,579 identifiers remain, including 3,898 with a matching deletion. [C286](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind30/r4b30__react__meta-muse-spark-1.3__rep2.md) makes the opposite inferential mistake: it uses retained archived material to argue that agents could still retrieve answers.

Of the 681 summary identifiers without a deletion match, 671 belong to sibling wikis and ten to DSEWiki. The deletion records concern DSEWiki alone. Neither the combined count nor the ten DSE identifiers establish live accessibility after cleanup. Checking that question would require dated retrieval evidence and the returned content under relevant access conditions.

A narrower conclusion can still be justified. [C200](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind10/r4b10__codex__gpt-5.6-sol__rep2.md) and [C044](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/fu5k_min5_b10/fu5kb10__codex__gpt-5.6-sol__rep2.md) describe the recorded campaign's limited scope and point to agent material saved on a hub on July 2. We now accept that dated cleanup inference. Reading it as proof of indefinite live access was an overextension in our own assessment.

Unsupported reassurance and unsupported alarm need the same scrutiny. The study does not observe a real responder making a harmful decision from these exercise reports; it identifies evidentiary gaps that could matter to such a decision.

### 5.3 An exploit attempt can have substantial corroboration without a settled causal chain

A request at 17:44:47 on June 18 contains a script designed to submit a wiki edit. Static decoding identifies the intended target and body. None of that target's 20 retained revisions exactly matches the decoded body, and no saved revision uses the initiating label.

Stopping there would omit important evidence. Fourteen later writes by another label at the same network prefix fall within zero or one second of preference-edit requests. We reproduce all fourteen correspondences. This supports a credible script-mediated editing hypothesis. It does not uniquely establish that the initial payload caused those writes, show every returned page, prove cookie theft or demonstrate self-propagation.

[C240](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind120/r4b120__codex__gpt-6-astra__rep1.md) and several follow-ups already investigate that stronger correlation while keeping the causal qualification. On reassessment, we also accept the high-confidence working-mechanism inference in [C273](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind30/r4b30__codex__gpt-5.6-sol__rep1.md) and [C095](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/fu5k_min5_b30/fu5kb30__codex__gpt-5.6-sol__rep1.md). Repeated matching observations can justify an inference without a direct browser trace. [C095](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/fu5k_min5_b30/fu5kb30__codex__gpt-5.6-sol__rep1.md)'s separate claim of a missing CSRF protection remains unsupported: observing a script-driven form submission does not establish the endpoint's protection settings. [OWASP's CSRF guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) notes that XSS can bypass existing CSRF defenses.

[C284](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind30/r4b30__react__google-gemini-3.8-flash__rep3.md) and [C106](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/fu5k_min5_b30/fu5kb30__react__google-gemini-3.8-flash__rep3.md) go further, claiming that each preference injection triggered its paired save. The prepared extract contains 25 preference requests from that prefix; 14 match the selected edits within one second. Many later request records preserve only the action name, so we cannot classify every one as an injection or calculate an exploit success rate. This supports a narrow objection to the universal confirmation claim, not a conclusion that the technique failed. The adverse interpretation remains marked disputable. [C283](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind30/r4b30__react__google-gemini-3.8-flash__rep2.md) and [C105](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/fu5k_min5_b30/fu5kb30__react__google-gemini-3.8-flash__rep2.md) make a different claim about the initial payload and a later page version: the texts differ, and the page already had 12 stored versions before the initial request.

### 5.4 A large archive does not imply a page of the same size

The welcome-page history contains 2,327 revisions with roughly 7.2 million characters across retained versions. Its largest individual retained version is 24,139 characters. Reports that describe a live page growing to 7.2 MB have confused accumulated history with a snapshot.

Repeated overwriting remains a real disruption. The corrected unit changes claims about page size and potentially about mechanism; it does not erase the incident. Similarly, a deletion campaign spanning weeks establishes elapsed time, not weeks of continuous manual work or a measured labor-cost ratio. We cannot derive staff effort, compensation or tooling from timestamps alone.

### 5.5 Strong investigations trace receipt, correction and limits

Some reports follow a shared answer beyond its first publication. [C254](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/graded_inputs/round4_blind120/r4b120__react__openai-gpt-6-astra__rep1.md) traces a lead posting Slovenia's 69% pass accuracy, a follower acknowledging the information, and a later message reporting receipt of the matching prompt. It also notes that a statistic table already existed: the useful new information was which question would come next.

Other reports track a counter signal initially interpreted as a future answer and corrected two minutes and twenty seconds later as an accidental test. Treating every counter increment as a successful message would miss that reversal. Likewise, survival of a detached process after a command ends is not the same as survival after its container terminates.

These are concrete examples of good investigation already produced by the AI systems. They show that the problem is not merely a failure to add caveats. It is whether the investigator traces the particular event, checks the relevant alternative and carries that distinction into the conclusion.

## 6. Implications and limits

The follow-up comparison exposes a gap between improving a reconstruction score and repairing a conclusion. A report can add useful findings while retaining a claim that the records contradict or do not establish. Before that claim supports a consequential decision, its evidence needs a separate check. This is a normative implication of the observed examples, not a measured effect of a verification intervention.

For recovery, an actionable account should identify what changed, what was tested afterward, what the test observed and what remains unknown. For exploitation, it should separate an attempt, corroborating effects and the remaining causal alternatives. For attribution, it should state whether a name is self-selected, an address is shared, or a principal is authenticated. The next check should be specific enough that another investigator could perform or challenge it.

The largest limitation is human validation. Full assistant reading, shared rules and lead reconciliation provide an inspectable first assessment; they do not substitute for independent methods and cyber review. The sensitivity analysis excludes judgments marked disputable, but cannot remove all shared interpretive bias. Some flagged claims concern precise factual errors; others concern overstatement. They do not all have equal operational importance.

A single incident and its dependent report collection do not represent cybersecurity investigations generally. The study does not measure training contamination, actual operator harm from these reports, model capability under controlled equal conditions, or the effectiveness of autonomous defense. It also does not exhaustively verify every incidental URL, public-data answer, token count or recommendation in a million words of material.

Later operator logs extend what can be studied. The September 18 version of *The Mechanics of a Swarm* reports prior content requests for 1,034 of 1,140 coordinating names and distinguishes requests from successful delivery and use. We reviewed that published analysis, not the underlying operator-log collection. We do not fault earlier investigators for lacking those later inputs or use its aggregate request count as proof of post-cleanup access.

The next Fide experiment should compare explicit claim verification with ordinary report expansion and test its effect on actual decisions: whether to continue inquiry, escalate, intervene or close an incident. It should measure missed incidents and unnecessary restrictions as well as factual support. This paper supplies candidate checks, failure cases and positive examples for that work. It does not yet supply a validated defensive system.

## Reproducibility and materials

The companion package contains the complete artifact inventory, source hashes, reading coverage, question assessments, claim records, published grades, original and repaired pair mappings, manual transitions, record checks and analysis scripts. Full source reports and incident data remain linked at their upstream locations; we do not redistribute the entire third-party corpus. The published package contains Fide's analysis and bounded derived records.

Run the acquisition and provenance steps described in `README.md`, then `build_study.py` and `analyze_study.py` without the partial flag. Complete validation requires all 304 readings and all 79 manual comparisons. The scripts reproduce arithmetic and consistency checks; they do not independently establish the correctness of interpretive judgments. No paid inference or new model evaluation was used for this extension. Incident payloads were handled as inert data.

## References

- Sydney Von Arx, Cormac Slade Byrd, Spencer Kitts and Thomas Larsen. [Discovery of a new OpenAI agent message board](https://collusion.wiki/), September 4, 2026.
- MessageBoardAuditBench. [Pinned publication repository](https://github.com/hamzah2304/messageboardauditbench/tree/e1eea3b4eaf93f9a7e2898da97096ef643916da1), including the [publication evidence index](https://github.com/hamzah2304/messageboardauditbench/blob/e1eea3b4eaf93f9a7e2898da97096ef643916da1/docs/benchmark-data-index.md), [grading rubrics](https://github.com/hamzah2304/messageboardauditbench/tree/e1eea3b4eaf93f9a7e2898da97096ef643916da1/benchmark/rubrics) and staged reports linked in the inventory.
- [How good are slop-vestigators?](https://www.lesswrong.com/posts/wt4kk6vFPEhkXvF8Q/how-good-are-slop-vestigators), benchmark task and analysis.
- Philipp Lütje and coauthors. [The Mechanics of a Swarm: A Reproducible External Reconstruction of an Unintended Agent-Coordination Episode on a Third-Party Wiki](https://arxiv.org/html/2609.12748v2), version 2, September 18, 2026.

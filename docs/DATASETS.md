# Datasets

How ClauseGuard uses the three reference datasets from the PS2 guide, and the rules we follow. This file is the source for the README "Datasets and evaluation" section.

## Summary

| Dataset | Used for | Used for training? | Included in repo? | In first release? |
|---|---|---|---|---|
| Team-written fictional leases | Main test set (rental) | No | Yes, fictional samples only (`sample_documents/`) | Yes |
| CUAD (commercial contracts) | Clause-finding evaluation only | No | No. Downloaded by the user. | Optional |
| India Code (legislation) | Statutory context reference only | No | No | No |
| Open India Law (judgments, legislation) | Not used | No | No | No |

**No model in ClauseGuard is trained or fine-tuned on any dataset.** Gemma is used as released. The embedding model (`all-MiniLM-L6-v2`) is also used as released.

## 1. CUAD (contracts)

- **Source:** https://github.com/The-Atticus-Project/cuad (project page: https://www.atticusprojectai.org/cuad)
- **Licence:** CC BY 4.0. Cite the NeurIPS 2021 paper on the CUAD project page.
- **Use:** Test whether the system finds clauses of types that also appear in rental leases (for example termination, notice, governing law). Compare the system's findings with the expert labels.
- **Limit:** These are commercial agreements. Results measure general clause finding, not performance on consumer rental leases. Never present CUAD results as proof for rental documents.
- **Handling:** Download to a folder outside the repo (for example `data/external/cuad/`, which is git-ignored). Do not commit it.

## 2. India Code (legislation)

- **Source:** https://indiacode.gov.in (the old indiacode.nic.in address redirects here)
- **Licence:** Not verified. The site blocks automated access. Read the terms before any bulk use or redistribution.
- **Use:** Not used in the first release. If a later release needs statutory context, limit it to one or two named Acts, cached locally by hand, and show them only as "for reference; check the current text."
- **Limit:** Statutes are amended and are not contracts. Never derive legality conclusions from them.

## 3. Open India Law (judgments, tribunals, legislation)

- **Source:** https://huggingface.co/datasets/vaquill/open-india-law (login and accepting conditions required; about 54 GB)
- **Licence:** Data CC BY 4.0 (attribute). Scripts Apache-2.0. Some sources have unknown terms status.
- **Use:** Not used in the first release. Its contents are judgments and statutes, not the contracts ClauseGuard reads.
- **Limit:** Point-in-time snapshot (v2026.08). Not current law and not legal advice.

## 4. Rules for the whole team

1. **Do not commit dataset files.** Keep them in `data/external/`, which is git-ignored.
2. **Do not train or fine-tune** any model on these datasets without a new decision recorded in `PROJECT_MASTER.md`. Fine-tuning would also weaken the grounding design.
3. **Do not put dataset text into prompts** except through the normal retrieval path on a document the user has loaded.
4. **Attribute** each dataset in the README and cite CUAD's paper.
5. **Public availability is not permission to redistribute.** Share instructions for downloading, not the data.
6. **Organisers do not supply datasets, API keys or accounts.** Plan the download step during setup.
7. **Nothing here is legal advice.** Dataset content must not be quoted to users as authority.

## 5. CUAD evaluation procedure (if used)

1. Download CUAD. Pick the clause types that also occur in rental leases (candidates: termination, notice period, governing law).
2. Select a fixed sample of contracts from CUAD and record their IDs in `docs/TEST_RESULTS.md`.
3. Run the system on each contract, one clause type at a time, and record whether it finds the expert-labelled clause.
4. Report precision and recall **for CUAD**, with the caveat that the results do not transfer to consumer documents.
5. Keep the CUAD results in a separate section from the rental results.

## 6. Setup steps (for the README)

```
# Only if using CUAD evaluation. Run once while online; no user documents involved.
mkdir -p data/external/cuad
# Download data.zip from https://github.com/The-Atticus-Project/cuad into data/external/cuad/ and unzip it there.
```

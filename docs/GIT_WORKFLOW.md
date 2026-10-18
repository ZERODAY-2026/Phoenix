# Git and GitHub Workflow for Beginners

Goal: four people work in parallel without overwriting each other, and nothing private or huge reaches GitHub.

**Easiest tools:** GitHub Desktop (graphical) or the commands below. Pick one and stick with it.

## 1. One-time setup (R4, Git master)

1. Create a **public** GitHub repository named `clauseguard` (or your final project name).
   - Tick "Add a README" is optional; our pack already has one.
   - Choose **MIT** licence (or Apache-2.0) when GitHub asks, or add the provided `LICENSE` file.
2. Invite the other three under Settings, Collaborators.
3. Copy the files from this pack into the repo folder. **Create `.gitignore` from the provided file, not with `echo`.**
4. Commit and push to `main`:

```
git add .
git commit -m "Initial skeleton: docs, licence, gitignore"
git push origin main
```

5. In GitHub, Settings, Branches: add a rule for `main` that requires a Pull Request before merging (if the option is available on your account). This stops accidental overwrites.

## 2. Everyone else: get the code

```
git clone <repo_url>
cd clauseguard
git checkout -b r2-retrieval      # use your own branch name, see section 3
```

## 3. Branch names (fixed)

| Role | Branch |
|---|---|
| R1 | `r1-model` |
| R2 | `r2-retrieval` |
| R3 | `r3-answer` |
| R4 | `r4-ui` |

## 4. Daily loop

```
git pull origin main              # get others' merged work
# ... edit only YOUR files, run them, test them ...
git status                        # check what changed; stop if you see models/, .pdf or secrets
git add src/ingest.py             # add specific files, not everything
git commit -m "Add clause splitter for numbered clauses"
git push origin r2-retrieval
```

Then on GitHub: **Open a Pull Request** from your branch into `main`. Another teammate reads it and clicks Merge. R4 resolves any problems.

## 5. Rules that prevent disasters

1. **Never commit** `models/`, `.venv/`, `.env`, `*.faiss`, `*.pkl`, `*.npy`, or any real or private document.
2. **Sample documents** in `sample_documents/` must be **fictional** and written by the team. Say so in `sample_documents/README.md`.
3. **One file, one owner.** If two people edit the same file, merge conflicts follow.
4. **Commit small and often.** A working commit is a save point you can return to.
5. **Never use `git push --force`** on `main`.
6. **Before every push:** `git status`, then read the list.
7. **If something breaks:** do not panic-delete. Ask in the team chat; `git log` and `git checkout <old-commit>` let you look at older versions.
8. **No secrets.** The project needs no API keys. If you ever see a key or token in code, stop and remove it before committing. Committed secrets fail gate G5.

## 6. If you get a merge conflict

1. Do not close the editor in a hurry. Run `git status` to see the conflicted files.
2. Open the file; look for `<<<<<<<`, `=======`, `>>>>>>>` markers.
3. Keep the correct lines, delete the markers, save.
4. `git add <file>` then `git commit`.
5. Ask your AI assistant: "Explain this merge conflict and show me what the merged file should look like", and paste the conflicted section.

## 7. Final-day tasks (R4)

- Tag the release: `git tag v1.0 && git push origin v1.0`
- Make sure the repo is **public** and the licence file is visible on the front page
- Open the repo in a private browser window to confirm judges can see it
- Run `docs/SUBMISSION_CHECKLIST.md` top to bottom

# ClauseGuard Privacy Design, Threat Model and Evidence Guide

Privacy is worth 15 points on its own, and a Poor rating caps the whole PS2 score at 40. Judges will run an offline test, monitor connections, review code and dependencies, check temporary files, and confirm that weights and inference are local. **We must be able to prove it, not just claim it.**

## 1. What counts as private (from the guide)

The file, extracted text, chunks, embeddings, summaries, answers, names, metadata, and **the user's questions**. All of it stays on the device.

## 2. Rules we follow

| Allowed | Not allowed |
|---|---|
| Local Gemma inference through Ollama on `127.0.0.1` | Any remote LLM API |
| Local parsing, local embeddings, in-memory index | Cloud OCR, cloud embeddings, cloud storage, translation APIs |
| Downloading model weights and packages **during setup only**, with no user document involved | Telemetry, analytics or crash reports containing document content |
| Content-free logs (timings, counts, status codes) | Logs containing document text, questions or answers |

Any other network access (for example an update check) must be **documented, content-free, and optional or off**.

## 3. Development versus final demo

| Stage | Rule |
|---|---|
| Development | Fictional sample documents only. A LAN model server is tolerated **only** if documented and never used with real documents. Prefer the stub backend. |
| Final demo, recording and evidence | **One laptop. Ollama bound to `127.0.0.1`. Wi-Fi off. No LAN model server.** |

Reason: a second laptop receiving prompts is a content-carrying connection. Ollama also has no built-in authentication, so `OLLAMA_HOST=0.0.0.0` exposes it to everyone on the network.

## 4. Threat model

**Assets:** the uploaded document and everything derived from it, plus questions and answers.

**In scope (we defend against these):**

| Threat | Defence |
|---|---|
| Our app or a dependency sending content to the internet | No remote-call code; offline test; connection monitoring; code and dependency audit |
| Telemetry from Streamlit or libraries | `gatherUsageStats = false`; offline env vars; audit; offline test |
| Embedding model or tokenizer downloading at runtime | Local model folder; `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` |
| Other devices reaching our model server or UI | Ollama and Streamlit bound to `127.0.0.1`; no port forwarding |
| Leftover files (uploads, indexes, caches) | In-memory processing; Delete session; temp-file check |
| Logs leaking content | Content-free logging policy; log review |
| Malicious instructions inside the document | Untrusted-data prompt framing; injection scan; output verification |

**Out of scope (state honestly in the README):**

- Malware or a compromised operating system on the laptop
- Someone with physical access to the unlocked laptop
- Operating-system swap or hibernation files that may contain memory pages
- Browser history or screenshots made by the user
- Encrypted network traffic is invisible to simple inspection, which is why judges look for the **absence of connections** rather than reading payloads

## 5. Known network touchpoints (fill in after testing)

| Touchpoint | When | Carries document content? | Status |
|---|---|---|---|
| Download of Ollama and models (`ollama pull`) | Setup only | No | Allowed, separate from operation |
| Download of the embedding model and `pip install` | Setup only | No | Allowed |
| App to Ollama at `127.0.0.1:11434` | Normal operation | Yes, but stays on the same machine | Allowed (loopback) |
| Browser to Streamlit at `127.0.0.1:8501` | Normal operation | Yes, same machine | Allowed (loopback) |
| Ollama desktop app update check (if the tray app runs) | Possibly at startup | No | **Verify during the offline test; document or avoid by running `ollama serve` from a terminal** |
| Anything else seen in monitoring | | | Must be empty |

## 6. Setup versus operation (keep them separate in the README)

**Setup (internet allowed, no user documents):**

1. Install Python, Git, Ollama
2. `ollama pull <chosen model>`
3. Create a virtual environment and `pip install -r requirements.txt`
4. Download the embedding model once and save it into `models/all-MiniLM-L6-v2/`
5. Turn the internet **off**

**Operation (internet off):**

```
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

(On macOS/Linux use `export` instead of `set`.)

## 7. The offline test (reproducible procedure)

Run on the **final demo laptop**, with a lease nobody on the team wrote.

1. Complete setup. Close all other apps.
2. Turn **Wi-Fi off** and unplug Ethernet (or enable airplane mode). Confirm with `ping 8.8.8.8` that it fails.
3. Start the connection monitor (section 8).
4. Start Ollama bound to loopback: confirm with `netstat -ano | findstr 11434` (Windows) or `ss -tlnp | grep 11434` (Linux). The address must be `127.0.0.1`, not `0.0.0.0`.
5. Start the app and run the full demo script from `docs/PROJECT_MASTER.md` section 14.
6. Stop the monitor and save its output.
7. Run the temp-file check (section 9).
8. Record the screen, including the monitor and the network-off indicator.

**Pass criteria:** the whole flow works; the monitor shows no connections to non-loopback addresses made by Python, Streamlit, Ollama or the browser tab during processing.

## 8. Connection monitoring options

Pick **at least two** and save the output as evidence.

**Windows**
- PowerShell, repeated every few seconds: `Get-NetTCPConnection | Where-Object { $_.RemoteAddress -notin '127.0.0.1','::1','0.0.0.0','::' } | Select-Object State,LocalPort,RemoteAddress,RemotePort,OwningProcess`
- `netstat -ano` and compare process IDs against Task Manager
- TCPView or Resource Monitor (Network tab)
- Wireshark capture with filter `not (ip.addr == 127.0.0.1 or ipv6.addr == ::1)`

**Linux / macOS**
- `sudo ss -tpn` or `lsof -i -nP` while the app runs
- `sudo tcpdump -i any not host 127.0.0.1 and not host ::1`

**Stronger isolation (optional)**
- Run the app in a container with networking off (`--network none`), with the model files mounted. Ollama inside the same container or via a socket.
- A local firewall rule blocking outbound traffic for `python`, `streamlit` and `ollama`.

## 9. Temp-file and leftover-data check

Before and after a session, search for traces of the sample document:

- Pick a distinctive sentence from the test lease (for example a made-up landlord name).
- Search the app folder, the user temp folder (`%TEMP%` on Windows, `/tmp` on Linux/macOS), and the Streamlit cache folders for that string.
- After pressing **Delete session**, repeat the search. Expected result: **no hits**.
- Also confirm that no `.faiss`, `.pkl`, `.npy` or `.json` index files were created in the project folder.

## 10. Code and dependency audit

Run from the repo root and explain every hit in `docs/privacy_audit.md`:

```
grep -rnE "requests\.|urllib|httpx|aiohttp|socket|http://|https://|openai|anthropic|google|telemetry|analytics|sentry|posthog|mixpanel" app.py src/
```

Expected hits: `requests` in `src/llm.py` pointing only to `config.OLLAMA_URL` (loopback). Anything else needs an explanation or removal.

Also list direct dependencies from `requirements.txt` with one line each on what they do and whether they can make network calls. Pay special attention to `sentence-transformers` / `transformers` / `huggingface_hub` (download on first use) and `streamlit` (usage stats).

## 11. Evidence pack to keep in the repo (`docs/evidence/`)

| Item | Format |
|---|---|
| Screen recording of the full offline run (3-5 min) | MP4 link or file under size limits |
| Connection-monitor output during the run | text or screenshot |
| `netstat`/`ss` output showing Ollama on loopback | text |
| Temp-file search results before and after Delete | text |
| Code audit with explanations | `docs/privacy_audit.md` |
| Benchmarks (model, quantisation, runtime, RAM, speed) | `docs/benchmarks.md` |
| Statement of known network touchpoints | section 5 above, filled in |

## 12. Honest wording for the README

Use language like: "ClauseGuard processes documents locally. We tested with networking disabled and monitored connections during processing; see `docs/evidence/`. We cannot protect against a compromised device, and operating-system swap files are outside our control."

Do **not** write "100% secure" or "fully private" without the evidence next to it.

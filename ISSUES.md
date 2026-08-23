# Epic: Fine-Tuning Dataset Expansion & Multi-Component Synthesis (`spm-veneer-coder`)

This master issue defines the dataset expansion roadmap, component-wise coverage goals, and fine-tuning guidelines for `spm-veneer-coder`.

> [!IMPORTANT]
> **Multi-Component Page Synthesis Rule:** Real-world web pages are rarely single-component snippets. Scraped and synthetic training examples **can and SHOULD combine multiple React components** within the same `.vnr` manifest (e.g. `UiNavHeader` + `UiSearchBar` + `UiTableListPage` or `UiSplitLayout` + `UiTagBadge` + `UiToast`) to train the model on full-page modernizations.

---

## 🎯 Master Target Metrics

- **Target Example Count:** **255 to 340+ complex, real-world HTML → VNR examples** (15 to 20 complex examples per component target across all 17 components in `spm-components`).
- **Dataset Composition:** Rebalance from current ~7.3% to **70%+ direct HTML → VNR page transformation tasks**.
- **Model Preset:** Train via `presets/qwen2.5-coder-1.5b.yaml` and `presets/qwen2.5-coder-0.5b.yaml` with LoRA rank `r: 32` (`lora_alpha: 32`) and `num_train_epochs: 3`.

---

## 📋 Sub-Issues Breakdown

### 🔹 Sub-Issue #1: Multi-Component Real-World HTML Page Reconstruction

- [ ] **Task 1.1 — Navigation & Search Header Pages (15-20 Examples)**
  - *Components Combined:* `UiNavHeader` + `UiSearchBar` + `UiHeroLanding`
  - *Scenarios:* Wiki header navigation, documentation search bars, brand logos, primary/secondary link rows, mobile breakpoints.

- [ ] **Task 1.2 — Data Table & Portal Lists (15-20 Examples)**
  - *Components Combined:* `UiNavHeader` + `UiTableListPage` + `UiTagBadge` + `UiPaginationBar`
  - *Scenarios:* GitHub issues, StackOverflow feeds, admin panels, multi-value array tag columns (`| split: ','`), date/currency column formatting.

- [ ] **Task 1.3 — Media Gallery & Split Viewer Portals (15-20 Examples)**
  - *Components Combined:* `UiSplitLayout` + `UiImageViewer` + `UiScrollPanel` + `UiTagBadge`
  - *Scenarios:* Image boards (Safebooru/Craigslist), panoramic photo viewers using `imageUrl`/`title` aliases, tag sidebars.

- [ ] **Task 1.4 — Discussion & Article Thread Pages (15-20 Examples)**
  - *Components Combined:* `UiCommentListPage` + `UiPostDetails` + `UiTagBadge`
  - *Scenarios:* Hacker News threads, Reddit posts, article layouts with optional thumbnails, author metadata fallbacks.

- [ ] **Task 1.5 — Metrics & Dashboard Analytics (15-20 Examples)**
  - *Components Combined:* `UiDashboardPage` + `UiStatsDashboard` + `UiTable` + `UiToast`
  - *Scenarios:* Algolia search metrics, server performance counters, status indicators, toast alert notifications.

---

### 🔹 Sub-Issue #2: Component-Specific Feature Extensions & Syntax Aliases

- [ ] **Task 2.1 — `UiSplitLayout` Image Alias Mappings (15-20 Examples)**
  - *Details:* Mapping `imageSlot` children bindings using `imageUrl` (fallback to `src`) and `title` (fallback to `alt`).

- [ ] **Task 2.2 — `UiTableListPage` Array & Tag Badge Rendering (20-30 Examples)**
  - *Details:* Mapping multi-value array tag columns (`["bug", "p0", "ui"]`) rendered automatically as `<UiTagBadge>` elements.

- [ ] **Task 2.3 — Child Item Binding Diagnostic Recovery (10-15 Examples)**
  - *Details:* Diagnostic Q&A examples training the LLM to recover when `spm validate` reports `FAIL` on missing child item bindings.

---

### 🔹 Sub-Issue #3: Dataset Compilation & Fine-Tuning Execution

- [ ] **Task 3.1 — Compile JSONL Dataset Bundle**
  - Run `python -m spm_finetune.cli.main compile-dataset --config presets/qwen2.5-coder-1.5b.yaml` and verify dataset output.
- [ ] **Task 3.2 — Execute Unsloth SFT Training Run**
  - Run `python train.py --preset presets/qwen2.5-coder-1.5b.yaml` and verify loss convergence.
- [ ] **Task 3.3 — Evaluate Model via Golden Eval Suite**
  - Run `./venv/bin/pytest tests/test_evals.py` and verify multi-component generation pass rate.

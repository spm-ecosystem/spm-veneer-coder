# Dataset Expansion & Fine-Tuning Backlog (`spm-veneer-coder`)

This document catalogs dataset expansion tasks, required example additions, and fine-tuning improvements to be incorporated into `in/dataset/` for future model retraining runs.

---

## Issue #1: Add Dataset Examples for `UiSplitLayout` `imageUrl` / `title` Aliases

- **Context:** `UiSplitLayout` was updated to support `imageUrl` (fallback to `src`) and `title` (fallback to `alt`) inside `imageSlot` children bindings.
- **Task:** Create 15-20 HTML → VNR mapping examples in `in/dataset/` demonstrating gallery image items where image URLs are mapped to `imageUrl` or `src` and captions are mapped to `title` or `alt`.
- **Target Component:** `UiSplitLayout`
- **Expected VNR Syntax:**
  ```vnr
  reconstruct ".gallery-detail" -> UiSplitLayout {
      child imageSlot extends GalleryItem {
          selector: ".main-image-container";
      }
  }
  class GalleryItem {
      bind imageUrl: "img.hero | attr:src";
      bind title: "figcaption | text";
  }
  ```

---

## Issue #2: Add Dataset Examples for Array-Based Tag/Badge Columns in `UiTableListPage`

- **Context:** `UiTableListPage` now natively renders cell values containing arrays of strings/tags (e.g. `["bug", "p0", "ui"]`) as `<UiTagBadge>` component rows.
- **Task:** Create 20-30 HTML → VNR mapping examples where table rows contain multi-value tag columns (e.g. issue labels, category chips, status tags).
- **Target Component:** `UiTableListPage`
- **Expected VNR Syntax:**
  ```vnr
  reconstruct "#issue-list" -> UiTableListPage {
      child tableRows extends IssueRow {
          selector: "tr.issue";
      }
  }
  class IssueRow {
      bind title: "a.issue-title | text";
      bind labels: ".labels-container .label-tag | text | split: ','";
  }
  ```

---

## Issue #3: Add Dataset Examples for Child Item Binding Validation Diagnostics

- **Context:** `spm validate` now validates child item bindings and reports failure if a child selector returns `null` for mandatory bindings.
- **Task:** Add 10-15 compiler feedback diagnostic Q&A examples training the model to recover when `spm validate` reports `FAIL` on missing child item bindings.
- **Expected Diagnostic Pattern:**
  ```text
  Child "tableRows": "tr.item" -> FAIL (0 matches or missing bind "title")
  ```

---

## Issue #4: Dataset Rebalancing & Fine-Tuning Preset Optimization

- **Context:** Current dataset composition contains 450 examples, but only ~33 are direct HTML → VNR transformation tasks.
- **Task:**
  1. Synthesize 250+ new HTML → VNR transformation examples across all 17 components in `spm-components`.
  2. Maintain LoRA rank `r: 32` (`lora_alpha: 32`) and `num_train_epochs: 3` in `presets/qwen2.5-coder-0.5b.yaml` and `presets/qwen2.5-coder-1.5b.yaml`.

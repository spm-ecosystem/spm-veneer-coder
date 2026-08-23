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

## Issue #4: Component-Wise Dataset Expansion (15-20 Complex HTML Examples per Component)

- **Context:** Current dataset composition contains 450 examples, but only ~33 are direct HTML → VNR transformation tasks.
- **Requirement:** Create **15 to 20 complex, real-world HTML → VNR transformation examples for EACH of the 17 React components** in `spm-components` (totaling **255–340 complex HTML examples**).
- **Target Component Catalog (17 Components):**
  1. `UiNavHeader` (15-20 examples: brand logos, responsive link bars, utility sub-navs)
  2. `UiHeroLanding` (15-20 examples: tagline headers, CTA buttons, embedded search)
  3. `UiTableListPage` (15-20 examples: multi-column tables, tag arrays, date/currency values)
  4. `UiModernGridPage` (15-20 examples: image card grids, sidebar tag groups, pagination)
  5. `UiCommentListPage` (15-20 examples: nested comment threads, author meta, timestamps)
  6. `UiDashboardPage` (15-20 examples: metric cards, summary charts, widget panels)
  7. `UiImageCard` (15-20 examples: gallery cards, hover overlays, tag badges)
  8. `UiImageViewer` (15-20 examples: panoramic fit modes, zoom containers, captions)
  9. `UiPaginationBar` (15-20 examples: page link lists, prev/next controls, PID parameters)
  10. `UiPostDetails` (15-20 examples: article layouts, action buttons, metadata bars)
  11. `UiScrollPanel` (15-20 examples: tag sidebars, statistics HTML, quick action buttons)
  12. `UiSearchBar` (15-20 examples: form input wrappers, hidden fields, auto-submit URLs)
  13. `UiSplitLayout` (15-20 examples: image viewer + scroll panel split layouts, imageUrl/title aliases)
  14. `UiStatsDashboard` (15-20 examples: analytics counters, trend indicators, metric grids)
  15. `UiTable` (15-20 examples: primitive data tables, custom render columns)
  16. `UiTagBadge` (15-20 examples: status badges, tag chips, add/remove action controls)
  17. `UiToast` (15-20 examples: alert notifications, top window postMessage toasts)

- **Training Preset Config:** Maintain LoRA rank `r: 32` (`lora_alpha: 32`) and `num_train_epochs: 3` in `presets/qwen2.5-coder-0.5b.yaml` and `presets/qwen2.5-coder-1.5b.yaml`.

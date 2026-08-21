# Media query gated mobile reconstruction
## User
Write a Veneer Spec (.vnr) that reconstructs a mobile-only category drawer, but only mounts it on narrow viewports:

```html
<nav id="mobile-category-drawer" class="mobile-only">
  <a class="drawer-link" href="/category/electronics">Electronics</a>
  <a class="drawer-link" href="/category/home-garden">Home &amp; Garden</a>
  <a class="drawer-link" href="/category/toys">Toys</a>
</nav>
```
## Assistant
You can gate a `reconstruct` block so it only mounts under a specific viewport size using the `mediaQuery` property, set to a standard CSS media query string:

```vnr
reconstruct "#mobile-category-drawer" -> UiGridPage {
    mediaQuery: "(max-width: 768px)";
    pageTitle: "Categories";
    
    child categoryLinks {
        selector: "a.drawer-link";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

# Nested child mapping for threaded discussion replies
## User
Based on this two-level comment thread HTML, write a `.vnr` reconstruct targeting `UiPostDetails` that maps top-level comments and their nested replies:

```html
<div id="post-thread">
  <div class="comment depth-0" data-comment-id="501">
    <p class="comment-text">Great write-up, thanks for sharing!</p>
    <div class="comment depth-1" data-comment-id="502">
      <p class="comment-text">Agreed, very clear explanation.</p>
    </div>
  </div>
</div>
```
## Assistant
You can nest `child` blocks inside one another to map recursive structures like threaded replies — each level of nesting produces its own array-valued prop scoped to its parent:

```vnr
reconstruct "#post-thread" -> UiPostDetails {
    pageTitle: "Post Thread";
    
    child topLevelComments {
        selector: ".comment.depth-0";
        bind body: "p.comment-text | text";
        bind commentId: "self | attr:data-comment-id";
        
        child replies {
            selector: ".comment.depth-1";
            bind body: "p.comment-text | text";
            bind commentId: "self | attr:data-comment-id";
        }
    }
}
```

# Capturing hidden CSRF fields while replacing a search form
## User
I'm replacing this legacy search form with a modern component, but it has hidden fields I need to keep submitting correctly:

```html
<form id="legacy-quick-search" action="/search" method="get">
  <input type="hidden" name="csrf_token" value="a91f..." />
  <input type="hidden" name="site_id" value="42" />
  <input type="text" name="q" placeholder="Search products" />
  <button type="submit">Go</button>
</form>
```
## Assistant
Use the `hiddenInputs` extractor to collect every `<input type="hidden">` descendant as a JSON array, so the new component can still submit compatible hidden values:

```vnr
selector "#legacy-quick-search" -> UiSearchBar {
    action: replace;
    placeholder: "Search products";
    submitUrl: "https://example.com/search";
    queryParamName: "q";
    bind hiddenFields: "self | hiddenInputs";
}
```

# Resolving onclick-based navigation with hrefOrOnclick
## User
This product tile navigates through an inline `onclick` handler instead of a real link — how do I bind its destination URL?

```html
<div class="product-tile" data-sku="SKU-3391">
  <img src="/img/sku-3391.jpg" alt="Wireless Charger" />
  <div class="tile-caption" onclick="window.location='/product/wireless-charger'">
    Wireless Charger
  </div>
</div>
```
## Assistant
The `hrefOrOnclick` extractor normalizes both a real `href` attribute and an inline `onclick` navigation handler into a single destination string, so you don't need separate logic for each case:

```vnr
selector ".product-tile" -> UiImageCard {
    action: replace;
    bind imageUrl: "img | attr:src";
    bind caption: ".tile-caption | text";
    bind linkUrl: ".tile-caption | hrefOrOnclick";
    bind sku: "self | attr:data-sku";
}
```

# Reading adjacent sibling values with nextSiblingText
## User
Write a Veneer Spec reconstruct for a status panel where each metric's value sits in a plain `<span>` right after its label, rather than nested inside it:

```html
<div id="status-panel">
  <div class="stat-row">
    <span class="stat-label">Uptime</span>
    <span>99.98%</span>
  </div>
  <div class="stat-row">
    <span class="stat-label">Active Users</span>
    <span>18,204</span>
  </div>
</div>
```
## Assistant
When a label and its value are adjacent siblings instead of being nested together, match the label element and pipe through `nextSiblingText` to grab the following element's text content:

```vnr
reconstruct "#status-panel" -> UiStatsDashboard {
    pageTitle: "System Status";
    
    child metrics {
        selector: ".stat-row";
        bind label: ".stat-label | text";
        bind value: ".stat-label | nextSiblingText";
    }
}
```

# Self-referential selector for anchor tracking in pagination links
## User
I want each pagination link to also expose its own unique selector string, for a scroll-restore feature. Here's the markup:

```html
<nav id="results-pager">
  <a class="page-link" href="/search?page=1">1</a>
  <a class="page-link" href="/search?page=2">2</a>
  <a class="page-link" href="/search?page=3">3</a>
</nav>
```
## Assistant
The `selector` base extractor, applied to `self`, generates a unique CSS selector string for the matched element itself — useful for features like scroll-position restoration that need to re-locate the original node later:

```vnr
reconstruct "#results-pager" -> UiPaginationBar {
    pageTitle: "Search Results";
    
    child pages {
        selector: "a.page-link";
        bind label: "self | text";
        bind url: "self | attr:href";
        bind anchorSelector: "self | selector";
    }
}
```

# Preserving multiple legacy widgets in a single reconstruct
## User
Map this item page into `UiItemDetailsPage`, but keep both the legacy Q&A widget and the legacy shipping calculator alive and interactive:

```html
<div id="item-page">
  <h1 class="item-name">Trail Running Shoes</h1>
  <div class="item-desc">Lightweight shoes built for rough terrain.</div>
  <div id="legacy-qna-widget">...</div>
  <div id="legacy-shipping-calc">...</div>
</div>
```
## Assistant
You can preserve as many legacy widgets as needed in one `preserve` block — just add one named slot per widget:

```vnr
reconstruct "#item-page" -> UiItemDetailsPage {
    pageTitle: "Item Details";
    
    bind title: "h1.item-name | text";
    bind description: ".item-desc | text";
    
    preserve {
        qnaSlot: "#legacy-qna-widget";
        shippingCalculatorSlot: "#legacy-shipping-calc";
    }
}
```

# Fixing a missing semicolon compile error
## User
Why does this fail to compile?

```vnr
selector "#footer-links" -> UiNavHeader {
    action: replace
    logoHref: "https://example.com/";
}
```
## Assistant
Every property assignment in Veneer Spec must terminate with a semicolon — the `action: replace` line is missing its trailing `;`, which the compiler needs to know the statement has ended:

```vnr
selector "#footer-links" -> UiNavHeader {
    action: replace;
    logoHref: "https://example.com/";
}
```

# Duplicate theme block compile error across files
## User
I have `theme "First" { variables {} }` in one `.vnr` file and `theme "Second" { variables {} }` in another file in the same project. The compile fails — why, and how do I fix it?
## Assistant
A Veneer Spec project may only declare a single `theme` block across the entire compiled workspace, even if the two declarations live in different files — the compiler treats it as one global project-wide theme, not a per-file setting. Consolidate both into one declaration:

```vnr
// theme.vnr — single, consolidated theme declaration for the whole workspace
theme "StorefrontDefault" {
    variables {
        --spm-accent: "#e11d48";
    }
    customStyles {
        "#legacy-popup-ad { display: none !important; }"
    }
}
```

# Static JSON array prop via raw string for grid tag groups
## User
How do I pass a static list of filter tag groups (Category, Brand, Price) as a prop on a grid reconstruct?
## Assistant
Wrap the JSON array in a raw string literal so it doesn't need any backslash or quote escaping, then assign it directly to the static prop:

```vnr
reconstruct "#catalog-grid" -> UiGridPage {
    pageTitle: "Catalog";
    tagGroups: R"([
      { "title": "Category", "typeKey": "category" },
      { "title": "Brand", "typeKey": "brand" },
      { "title": "Price", "typeKey": "price" }
    ])";
}
```

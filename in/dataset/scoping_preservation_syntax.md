# Media query gated mobile reconstruction
## User
Write a Veneer Spec (.vnr) that reconstructs a mobile-only category drawer, but only mounts it on narrow viewports:

```html
<nav id="mobile-category-drawer" class="mobile-only">
  <a class="drawer-link" id="cat-1" data-img="/thumbs/cat1.jpg" href="/category/electronics">Electronics</a>
  <a class="drawer-link" id="cat-2" data-img="/thumbs/cat2.jpg" href="/category/home-garden">Home &amp; Garden</a>
</nav>
```
## Assistant
You can gate a `reconstruct` block so it only mounts under a specific viewport size using the `mediaQuery` property, and map the drawer links directly to `UiImageCard` components using the inline component child syntax:

```vnr
reconstruct "#mobile-category-drawer" -> UiModernGridPage {
    mediaQuery: "(max-width: 768px)";
    pageTitle: "Categories";
    
    child items -> UiImageCard {
        selector: "a.drawer-link";
        width: "140px";
        aspectRatio: "square";
        
        bind imageUrl: "self | attr:data-img";
        bind linkUrl: "self | attr:href";
        bind title: "self | text";
        bind id: "self | attr:id";
    }
}
```

---

# Nested child mapping for threaded discussion replies
## User
Based on this two-level comment thread HTML, write a `.vnr` reconstruct targeting `UiCommentListPage` that maps top-level comments and their nested replies:

```html
<div id="post-thread">
  <div class="comment depth-0" data-comment-id="501">
    <span class="user">Alice</span>
    <span class="date">2026-08-21</span>
    <a class="permalink" href="/comments/501">Link</a>
    <div class="comment depth-1" data-comment-id="502">
      <span class="user">Bob</span>
      <span class="date">2026-08-21</span>
      <p class="comment-text">Agreed, very clear explanation.</p>
    </div>
  </div>
</div>
```
## Assistant
You can nest `child` blocks inside one another to map recursive structures like threaded replies in `UiCommentListPage`:

```vnr
reconstruct "#post-thread" -> UiCommentListPage {
    pageTitle: "Post Thread";
    
    child threads {
        selector: ".comment.depth-0";
        bind id: "self | attr:data-comment-id";
        bind postUser: "span.user | text";
        bind postDate: "span.date | text";
        bind postUrl: "a.permalink | attr:href";
        
        child comments {
            selector: ".comment.depth-1";
            bind author: "span.user | text";
            bind date: "span.date | text";
            bind body: "p.comment-text | text";
        }
    }
}
```

---

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

---

# Resolving onclick-based navigation with hrefOrOnclick
## User
This product tile navigates through an inline `onclick` handler instead of a real link — how do I bind its destination URL?

```html
<div class="product-tile" id="tile-3391">
  <img src="/img/sku-3391.jpg" alt="Wireless Charger" />
  <div class="tile-caption" onclick="window.location='/product/wireless-charger'">
    Wireless Charger
  </div>
</div>
```
## Assistant
The `hrefOrOnclick` extractor normalizes both a real `href` attribute and an inline `onclick` navigation handler into a single destination string, so you don't need separate logic for each case:

```vnr
child items -> UiImageCard {
    selector: ".product-tile";
    width: "160px";
    aspectRatio: "square";
    
    bind imageUrl: "img | attr:src";
    bind title: ".tile-caption | text";
    bind linkUrl: ".tile-caption | hrefOrOnclick";
    bind id: "self | attr:id";
}
```

---

# Reading adjacent sibling values with nextSiblingText
## User
Write a Veneer Spec reconstruct for a dashboard card list where each card's description sits in a plain element right after its title link:

```html
<div id="settings-menu">
  <div class="menu-item">
    <a class="item-link" href="/settings/profile">Profile Info</a>
    <p>Manage username, emails, and phone numbers...</p>
  </div>
</div>
```
## Assistant
When a title and its description are adjacent siblings instead of being nested together, match the title link and pipe through `nextSiblingText` to grab the following element's text content:

```vnr
reconstruct "#settings-menu" -> UiDashboardPage {
    pageTitle: "Settings";
    
    child cards {
        selector: ".menu-item";
        bind title: "a.item-link | text";
        bind url: "a.item-link | attr:href";
        bind description: "a.item-link | nextSiblingText";
    }
}
```

---

# Self-referential selector for anchor tracking in pagination links
## User
I want each pagination link to also expose its own unique selector string. Here's the markup:

```html
<nav id="results-pager">
  <a class="page-link" href="/search?page=1">1</a>
  <a class="page-link" href="/search?page=2">2</a>
</nav>
```
## Assistant
The `selector` base extractor, applied to `self`, generates a unique CSS selector string for the matched element itself:

```vnr
reconstruct "#results-pager" -> UiPaginationBar {
    paramName: "page";
    
    child pageLinks {
        selector: "a.page-link";
        bind label: "self | text";
        bind url: "self | attr:href";
        bind anchorSelector: "self | selector";
    }
}
```

---

# Preserving multiple legacy widgets in a single reconstruct
## User
Map this item page into `UiSplitLayout`, but keep both the legacy Q&A widget and the legacy shipping calculator alive:

```html
<div id="item-page">
  <div class="item-desc">Lightweight shoes built for rough terrain.</div>
  <div id="legacy-qna-widget">...</div>
  <div id="legacy-shipping-calc">...</div>
</div>
```
## Assistant
You can preserve as many legacy widgets as needed in one `preserve` block under `UiSplitLayout`:

```vnr
reconstruct "#item-page" -> UiSplitLayout {
    sidebarWidth: "280px";
    sidebarSide: "right";
    
    bind mainHtml: ".item-desc | html";
    
    preserve {
        qnaSlot: "#legacy-qna-widget";
        shippingCalculatorSlot: "#legacy-shipping-calc";
    }
}
```

---

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

---

# Duplicate theme block compile error across files
## User
I have `theme "First" { variables {} }` in one `.vnr` file and `theme "Second" { variables {} }` in another file in the same project. The compile fails — why, and how do I fix it?
## Assistant
A Veneer Spec project may only declare a single `theme` block across the entire compiled workspace. Consolidate both into one declaration:

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

---

# Static configuration option for grid layouts
## User
How do I pass a static configuration to a reconstructed modern grid page?
## Assistant
You can set options like `mobileColumns` directly in the reconstruct block:

```vnr
reconstruct "#catalog-grid" -> UiModernGridPage {
    pageTitle: "Catalog";
    showSearch: true;
    searchPlaceholder: "Search catalog...";
    mobileColumns: 3;
}
```

# Invalid Component Name
## User
I tried `reconstruct ".header" -> UiNavbar {}` but spm-cli gives an error. What's wrong?
## Assistant
`UiNavbar` is not a registered component in the SPM ecosystem. The correct component for a navigation header is `UiNavHeader`.

```vnr
// ❌ UiNavbar does not exist — compile error: unknown component "UiNavbar"
reconstruct ".header" -> UiNavbar {
    action: replace;
}
```

```vnr
// ✅ Use the correct component name
reconstruct ".header" -> UiNavHeader {
    action: replace;
    logoUrl: ".logo img | attr:src";
}
```

Valid navigation-related components are: `UiNavHeader` (full header with logo and links) and `UiHeroLanding` (landing page hero section with nav).

# Wrong Extractor Name
## User
I'm using `bind title: ".card h2 | txt";` and the binding returns nothing at runtime. Why?
## Assistant
`txt` is not a valid extractor — the runtime `engine.ts` will hit the `else { return null }` branch and silently discard the value. The correct extractor is `text`.

```vnr
// ❌ "txt" is not a valid extractor — binding silently returns null at runtime
bind title: ".card h2 | txt";
```

```vnr
// ✅ Use "text" to extract textContent
bind title: ".card h2 | text";
```

The full list of valid base extractors is: `text`, `html`, `attr:<name>`, `hrefOrOnclick`, `selector`, `nextSiblingText`, `hiddenInputs`.

# Missing Pipe Between Selector and Extractor
## User
What's wrong with `bind price: "span.price"` — the value is always null.
## Assistant
Every `bind` expression must have exactly one base extractor after a `|` pipe. Without the pipe and extractor, the runtime receives a rule string it cannot parse and returns `null` for that field.

```vnr
// ❌ missing pipe and extractor — the engine splits on "|" and finds no extractor
bind price: "span.price";
```

```vnr
// ✅ add a pipe and a base extractor
bind price: "span.price | text";
```

```vnr
// ✅ or apply a pipe transform after the base extractor
bind price: "span.price | text | cleanNumber";
```

# Using UiToastContainer instead of UiToast
## User
I want to show notifications. I tried `reconstruct "#notifications" -> UiToastContainer {}` but the compiler says unknown component.
## Assistant
The registered component is `UiToast`, not `UiToastContainer`. `UiToastContainer` does not exist in the component registry.

```vnr
// ❌ "UiToastContainer" is not in COMPONENT_REGISTRY
reconstruct "#notifications" -> UiToastContainer {
    action: replace;
}
```

```vnr
// ✅ The correct component name is UiToast
reconstruct "#notifications" -> UiToast {
    action: replace;
}
```

# UiModernGridPage — items is Required
## User
I reconstruct a grid page but the component renders blank. My code is:
```vnr
reconstruct ".catalog" -> UiModernGridPage {
    pageTitle: "Products";
}
```
## Assistant
`UiModernGridPage` requires an `items` prop (typed as `GridItem[]` in the component interface). Without a `child items` block providing the array, the component receives `undefined` for `items` and renders nothing.

```vnr
// ❌ "items" is a required prop — UiModernGridPage renders blank without it
reconstruct ".catalog" -> UiModernGridPage {
    pageTitle: "Products";
}
```

```vnr
// ✅ add a child block to populate items
reconstruct ".catalog" -> UiModernGridPage {
    pageTitle: "Products";
    child items {
        selector: ".product-card";
        bind title: ".card-title | text";
        bind imageUrl: "img | attr:src";
        bind linkUrl: "a | attr:href";
        bind id: "self | attr:data-id";
    }
}
```

`GridItem` requires at minimum `title`, `imageUrl`, `linkUrl`, and `id`.

# UiImageCard — Required Props Missing
## User
My `UiImageCard` reconstruct compiles fine but renders nothing. What required props am I missing?
## Assistant
`UiImageCard` has four required props in its TypeScript interface: `imageUrl`, `linkUrl`, `title`, and `id`. If any of these bindings extract `null` at runtime (because the selector didn't match), the card will silently render nothing.

```vnr
// ❌ missing required props — imageUrl, linkUrl, title, id are all required
reconstruct ".promo-banner" -> UiImageCard {
    action: replace;
    bind imageUrl: "img | attr:data-src";
}
```

```vnr
// ✅ supply all four required props
reconstruct ".promo-banner" -> UiImageCard {
    action: replace;
    bind imageUrl: "img | attr:data-src";
    bind linkUrl: "a | attr:href";
    bind title: ".banner-title | text";
    bind id: "self | attr:data-id";
}
```

# Wrong Scope for child Selector
## User
I have a `child items` that uses `.product-card` as selector, but it picks up cards from outside my container too. Why?
## Assistant
By default, `child` selectors are scoped to the enclosing `reconstruct` or `selector` container (equivalent to `scope: "container"`). If you're seeing elements from outside, you may have accidentally written `scope: "document"`, which queries the entire page.

```vnr
// ❌ scope: "document" scans the full DOM — picks up .product-card from everywhere
reconstruct ".featured-section" -> UiModernGridPage {
    pageTitle: "Featured";
    child items {
        selector: ".product-card";
        scope: "document";
        bind title: ".card-title | text";
    }
}
```

```vnr
// ✅ omit scope (defaults to "container") or set it explicitly
reconstruct ".featured-section" -> UiModernGridPage {
    pageTitle: "Featured";
    child items {
        selector: ".product-card";
        bind title: ".card-title | text";
    }
}
```

# hrefOrOnclick — When to Use It
## User
Some links on the site use `onclick="document.location='/path'"` instead of a real `href`. My `bind linkUrl: "a | attr:href"` returns `#` or null. How do I handle this?
## Assistant
Use the `hrefOrOnclick` extractor. It first checks the `href` attribute — if it's a real URL (not `#` or `javascript:...`), it returns it. Otherwise it parses the `onclick` handler looking for `document.location` or `window.location` assignments and returns the extracted path.

```vnr
// ❌ attr:href returns "#" for JS-driven links
bind linkUrl: "a.product-link | attr:href";
```

```vnr
// ✅ hrefOrOnclick handles both href and onclick patterns
bind linkUrl: "a.product-link | hrefOrOnclick";
```

This extractor is implemented in `engine.ts` and handles patterns like `document.location = '/path'`, `window.location.href = '/path'`, and standard `href` attributes in priority order.

# Pipe Transform Without Base Extractor
## User
I tried `bind price: "span.price | cleanNumber"` but the value is null.
## Assistant
`cleanNumber` is a **pipe transform**, not a base extractor. It must come *after* a base extractor. Without a base extractor first, the engine fails to extract a value before the transform stage.

```vnr
// ❌ cleanNumber is a pipe transform — it cannot be the first pipe segment
bind price: "span.price | cleanNumber";
```

```vnr
// ✅ extract text first, then apply the transform
bind price: "span.price | text | cleanNumber";
```

`cleanNumber` strips commas, spaces and non-numeric characters (except `.` and `-`), then parses a float. Useful for price strings like `"$1,299.00"` → `"1299"`.

# UiSplitLayout — Using imageSlot vs Child
## User
I want to show images in a `UiSplitLayout`. I tried using a `bind imageUrl` directly on the reconstruct but nothing appears.
## Assistant
`UiSplitLayout` expects images through the `imageSlot` child array (typed as `ImageSlotItem[]`), not a top-level `bind`. A top-level `bind imageUrl` is not a prop that `UiSplitLayout` accepts — the prop interface has no `imageUrl` at the reconstruct level.

```vnr
// ❌ UiSplitLayout has no top-level imageUrl prop
reconstruct ".product-detail" -> UiSplitLayout {
    action: replace;
    bind imageUrl: ".product-img | attr:src";
}
```

```vnr
// ✅ use a child block named "imageSlot"
reconstruct ".product-detail" -> UiSplitLayout {
    action: replace;
    child imageSlot {
        selector: ".product-img";
        bind url: "self | attr:src";
        bind alt: "self | attr:alt";
    }
}
```

# Using nextSiblingText
## User
A price label and the price value are siblings in the DOM: `<span class="label">Price</span><span>$29.99</span>`. How do I extract the price?
## Assistant
Use `nextSiblingText`. It matches the element your selector targets, then reads the `textContent` of the immediately following sibling element — useful when a label and its value are adjacent siblings rather than parent/child.

```vnr
// ❌ this would select the label text "Price", not the value
bind price: "span.label | text";
```

```vnr
// ✅ nextSiblingText reads the text of the element AFTER the matched selector
bind price: "span.label | nextSiblingText";
```

Note: `nextSiblingText` uses `nextElementSibling`, so it skips text nodes and finds the next actual element. If the sibling doesn't exist, it returns `null` silently.

# UiSearchBar — queryParamName vs searchParamName
## User
I'm setting up a search bar. The spec example uses `searchParamName` but it doesn't seem to match the component prop.
## Assistant
`UiSearchBar` uses `queryParamName` (not `searchParamName`) for the query string parameter name. In VNR, you bind it as a static prop. `searchParamName` is used by layout components that *contain* a search bar (like `UiModernGridPage`, `UiScrollPanel`, `UiHeroLanding`, `UiSplitLayout`), which forward it to their internal `UiSearchBar`.

```vnr
// ❌ searchParamName is not a prop on UiSearchBar directly
selector ".site-search" -> UiSearchBar {
    action: replace;
    searchParamName: "q";
}
```

```vnr
// ✅ use queryParamName for UiSearchBar
selector ".site-search" -> UiSearchBar {
    action: replace;
    queryParamName: "q";
    placeholder: "Search...";
    submitUrl: "/search";
}
```

```vnr
// ✅ use searchParamName when configuring a layout component that embeds a search bar
reconstruct ".catalog" -> UiModernGridPage {
    pageTitle: "Browse";
    showSearch: "true";
    searchParamName: "q";
    searchSubmitUrl: "/search";
    child items { selector: ".card"; bind title: ".title | text"; }
}
```

# hiddenInputs Extractor
## User
A form has hidden inputs that I need to pass to the search component. How do I extract them all at once?
## Assistant
Use the `hiddenInputs` extractor. It queries all `input[type="hidden"]` inside the matched element, collects their `name`/`value` pairs, and returns the result as a JSON array string — which maps directly to `UiSearchBar`'s `hiddenFields` prop (typed as `{ name: string; value: string }[] | string`).

```vnr
// ❌ attr:value only gets a single input's value
bind hiddenFields: "form.search | attr:value";
```

```vnr
// ✅ hiddenInputs collects ALL hidden inputs under the matched element
selector ".search-form" -> UiSearchBar {
    action: replace;
    queryParamName: "q";
    submitUrl: "/search";
    bind hiddenFields: "form | hiddenInputs";
}
```

# UiNavbar, UiHeader, UiNavigation — All Invalid
## User
I keep getting compiler errors with my header component. I've tried `UiNavbar`, `UiHeader`, and `UiNavigation` — none work. What's the correct name?
## Assistant
None of those are registered components. The valid component for a site header with logo and navigation links is `UiNavHeader`.

```vnr
// ❌ UiNavbar — does not exist
reconstruct ".nav" -> UiNavbar {}

// ❌ UiHeader — does not exist
reconstruct ".nav" -> UiHeader {}

// ❌ UiNavigation — does not exist
reconstruct ".nav" -> UiNavigation {}
```

```vnr
// ✅ The correct component name is UiNavHeader
reconstruct ".nav" -> UiNavHeader {
    action: replace;
    bind logoUrl: ".logo img | attr:src";
    bind logoHref: ".logo | attr:href";
    child primaryLinks {
        selector: "nav a.primary";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

The full list of registered components: `UiNavHeader`, `UiHeroLanding`, `UiSearchBar`, `UiImageCard`, `UiTagBadge`, `UiPaginationBar`, `UiModernGridPage`, `UiImageViewer`, `UiScrollPanel`, `UiSplitLayout`, `UiCommentListPage`, `UiDashboardPage`, `UiStatsDashboard`, `UiTable`, `UiTableListPage`, `UiToastContainer`, `UiBox`, `UiFlexRow`, `UiFlexColumn`, `UiGrid`, `UiText`, `UiImage`, `UiLink`, `UiScrollBox`.

# UiCard, UiProductCard — Invalid Component Names
## User
I want to display product cards in a grid. I tried `UiCard` and `UiProductCard` but the compiler rejects them.
## Assistant
`UiCard` and `UiProductCard` are not registered components. For individual cards, use `UiImageCard`. For a full grid of cards, use `UiModernGridPage` with a `child items` block.

```vnr
// ❌ UiCard and UiProductCard do not exist
reconstruct ".product-grid" -> UiCard {}
reconstruct ".product-grid" -> UiProductCard {}
```

```vnr
// ✅ For a single card replace:
selector ".promo-card" -> UiImageCard {
    action: replace;
    bind imageUrl: "img | attr:src";
    bind linkUrl: "a | attr:href";
    bind title: ".card-title | text";
    bind id: "self | attr:data-id";
}

// ✅ For a full grid:
reconstruct ".product-grid" -> UiModernGridPage {
    pageTitle: "Products";
    child items {
        selector: ".product-card";
        bind imageUrl: "img | attr:src";
        bind linkUrl: "a | attr:href";
        bind title: ".title | text";
        bind id: "self | attr:data-id";
    }
}
```

# UiTableListPage — columns Prop Structure
## User
My `UiTableListPage` shows rows but the columns are wrong. I tried `bind columns: ".col-header | text"` but it doesn't work.
## Assistant
`columns` in `UiTableListPage` is a static configuration array (`TableColumnConfig[]`), not a scraped value — it defines how to render columns, not what data to extract. You set it as a static JSON value using a raw string, not a `bind`.

```vnr
// ❌ columns is a static layout config, not a scraped field
reconstruct ".data-table" -> UiTableListPage {
    bind columns: ".col-header | text";
    child tableRows { selector: "tr"; bind name: "td:first-child | text"; }
}
```

```vnr
// ✅ columns is declared as a static raw-string JSON array
reconstruct ".data-table" -> UiTableListPage {
    pageTitle: "Data";
    columns: R"([
      { "key": "name", "header": "Name", "type": "text" },
      { "key": "url", "header": "Link", "type": "link", "urlKey": "url" }
    ])";
    child tableRows {
        selector: "tr.data-row";
        bind name: "td:first-child | text";
        bind url: "td a | attr:href";
    }
}
```

# UiPaginationBar — paramName vs pageParamName
## User
I set up `UiPaginationBar` but clicking page links doesn't update the URL query param. I tried `pageParamName` but nothing happens.
## Assistant
The correct prop is `paramName`, not `pageParamName`. `UiPaginationBar` uses `paramName` (typed as `string?` in its TypeScript interface) alongside a `child pageLinks` block that provides the scraped page links.

```vnr
// ❌ pageParamName is not a valid prop on UiPaginationBar
selector ".pagination" -> UiPaginationBar {
    action: replace;
    pageParamName: "page";
}
```

```vnr
// ✅ use paramName and provide pageLinks via child
selector ".pagination" -> UiPaginationBar {
    action: replace;
    paramName: "page";
    child pageLinks {
        selector: "a.page-link";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

# UiTagBadge — Required label Prop
## User
My `UiTagBadge` renders nothing. I only have the `href` bound.
## Assistant
`UiTagBadge` has one required prop: `label` (typed as `string` — not optional). Without `label` the badge renders nothing.

```vnr
// ❌ label is required — UiTagBadge renders nothing without it
selector ".tag" -> UiTagBadge {
    action: replace;
    bind href: "self | attr:href";
}
```

```vnr
// ✅ bind label (required) and optionally href, count, addUrl, removeUrl
selector ".tag" -> UiTagBadge {
    action: replace;
    bind label: "self | text";
    bind href: "self | attr:href";
    bind count: ".tag-count | text | number";
}
```

# number vs cleanNumber Pipe Transform
## User
My price shows as `null` when I use `| number`. The raw text is `"$1,299.00"`. What's wrong?
## Assistant
`number` strips nothing — it calls `Number(val.trim())` which returns `NaN` for `"$1,299.00"` because of the dollar sign and comma. Use `cleanNumber` instead: it strips commas, spaces and non-numeric characters (except `.` and `-`) before parsing.

```vnr
// ❌ Number("$1,299.00") → NaN → null
bind price: "span.price | text | number";
```

```vnr
// ✅ cleanNumber strips "$" and "," before parsing → "1299"
bind price: "span.price | text | cleanNumber";
```

`number` is suitable only for text that is already a plain numeric string (e.g. `"42"`, `"3.14"`). For any formatted currency, use `cleanNumber`.

# preserve — Slot Name Must Match Component id
## User
I used `preserve` to keep a comment form but it disappears at runtime. My code compiles fine.
## Assistant
`preserve` reparents a legacy DOM node into a named slot **inside** the new Shadow DOM layout, but the target layout component must have an element with `id="{slotName}-container"` in its rendered output. If the slot name doesn't match, the legacy node is removed from the original page but never reappears — it fails silently at runtime, not at compile time.

```vnr
// ❌ compiles fine but fails silently if UiSplitLayout has no id="commentForm-container"
reconstruct ".post-page" -> UiSplitLayout {
    action: replace;
    preserve commentForm: "form.comment-form";
}
```

To fix: check the target component's actual rendered HTML to find its valid slot container IDs before using `preserve`. If no matching container ID exists, the slot name is invalid at runtime.

# split Pipe — Returns JSON Array String
## User
I bound a comma-separated tag string with `| split` expecting an array. The component shows the raw JSON string instead.
## Assistant
The `split` pipe returns a **JSON-encoded array string** (e.g. `'["tag1","tag2"]'`), not a JavaScript array. The Veneer Spec runtime passes this JSON string to the React component prop, which must accept `string` or parse it internally. If the component expects `string[]`, the JSON string is passed as-is and the component is responsible for parsing.

```vnr
// ✅ split whitespace-delimited tokens into a JSON array string
bind tags: ".tags | text | split";
// Result prop value: '["cooking","travel","tech"]'

// ✅ split on a custom delimiter (e.g. comma)
bind tags: ".tags | text | split:,";
// Result prop value: '["cooking"," travel"," tech"]'
// Note: values are NOT trimmed with split:<delim>
```

For components that accept a `TagItem[]` prop (like `UiModernGridPage`), use a `child tags` block instead of a top-level `bind tags`:

```vnr
child tags {
    selector: "a.tag";
    bind label: "self | text";
    bind href: "self | attr:href";
}
```

# selector vs reconstruct — When to Use Each
## User
When should I use `selector` vs `reconstruct`? I always use `reconstruct` for everything.
## Assistant
They serve different scopes:

- **`selector`** targets a **single element** (a nav bar, a button, a search box) to either hide it or replace it with a React component in-place, without affecting the rest of the page.
- **`reconstruct`** targets a **large container** (a full catalog section, comment board, or whole page viewport), hides all legacy children inside it, and mounts a React layout component inside an isolated Shadow DOM host.

```vnr
// ✅ selector: replace a single nav element in-place
selector "#top-nav" -> UiNavHeader {
    action: replace;
    bind logoUrl: ".logo img | attr:src";
}

// ✅ reconstruct: replace an entire page section with a modern layout
reconstruct "#main-catalog" -> UiModernGridPage {
    pageTitle: "Browse";
    child items {
        selector: ".product-card";
        bind title: ".title | text";
        bind imageUrl: "img | attr:src";
        bind linkUrl: "a | attr:href";
        bind id: "self | attr:data-id";
    }
}
```

Using `reconstruct` on a small element like a nav bar is technically valid but wasteful — it spins up a Shadow DOM host unnecessarily. Prefer `selector` for contained single-element replacements.

# urlPattern — Only Inside reconstruct or selector Blocks
## User
I declared `urlPattern` at the top level of my `.vnr` file but it has no effect.
## Assistant
`urlPattern` is a block-level constraint, not a file-level directive. It must be declared **inside** a `reconstruct` or `selector` block, where it gates whether that specific block activates on the current page URL.

```vnr
// ❌ urlPattern at file/theme level has no effect
urlPattern: R"(/products/*)";

reconstruct ".catalog" -> UiModernGridPage {
    pageTitle: "Products";
}
```

```vnr
// ✅ urlPattern inside the block that it should gate
reconstruct ".catalog" -> UiModernGridPage {
    urlPattern: R"(/products/*)";
    pageTitle: "Products";
    child items {
        selector: ".product-card";
        bind title: ".title | text";
        bind imageUrl: "img | attr:src";
        bind linkUrl: "a | attr:href";
        bind id: "self | attr:data-id";
    }
}
```

Multiple blocks can have different `urlPattern` values in the same file, enabling a single `.vnr` file to handle multiple page types.

# UiPostDetails — imageUrl is Required
## User
My `UiPostDetails` reconstruct compiles but renders nothing on the image side. I only have `tags` and `buttons` children.
## Assistant
`UiPostDetails` has one required prop: `imageUrl` (typed as `string` — not optional). Without it the component cannot render its image slot and falls back to an empty layout.

```vnr
// ❌ imageUrl is required — component renders broken without it
reconstruct ".post-detail" -> UiPostDetails {
    child tags {
        selector: "a.tag";
        bind label: "self | text";
        bind href: "self | attr:href";
    }
}
```

```vnr
// ✅ bind imageUrl (required) before adding optional children
reconstruct ".post-detail" -> UiPostDetails {
    bind imageUrl: ".post-hero img | attr:src";
    child tags {
        selector: "a.tag";
        bind label: "self | text";
        bind href: "self | attr:href";
    }
    child buttons {
        selector: "a.action-btn";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

# Using bind keyword inside reconstruct block
## User
Why does `reconstruct "#search" -> UiSearchBar { bind hiddenFields: "form | hiddenInputs"; }` fail to compile?
## Assistant
The `bind` keyword is ONLY used inside `class` definitions. Inside `reconstruct` blocks, direct property assignments do not use the `bind` keyword.

```vnr
// ❌ Do NOT use "bind" inside reconstruct blocks — compiler error: Expected ':' after property key
reconstruct "#search" -> UiSearchBar {
    bind hiddenFields: "form | hiddenInputs";
}
```

```vnr
// ✅ Assign properties directly without the "bind" keyword
reconstruct "#search" -> UiSearchBar {
    hiddenFields: "form | hiddenInputs";
}
```

# Using attr: prefix with standalone extractors
## User
Why does `bind url: "a | attr:hrefOrOnclick";` fail to compile?
## Assistant
`hrefOrOnclick`, `nextSiblingText`, `hiddenInputs`, and `selector` are standalone base extractors. Do NOT prefix them with `attr:`. The `attr:` prefix is ONLY for HTML attribute names like `attr:src` or `attr:href`.

```vnr
// ❌ Do NOT use "attr:" prefix with standalone extractors
bind url: "a | attr:hrefOrOnclick";
bind text: "span | attr:nextSiblingText";
bind fields: "form | attr:hiddenInputs";
bind sel: "self | attr:selector";
```

```vnr
// ✅ Use standalone base extractors directly after the pipe
bind url: "a | hrefOrOnclick";
bind text: "span | nextSiblingText";
bind fields: "form | hiddenInputs";
bind sel: "self | selector";
```

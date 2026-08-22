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

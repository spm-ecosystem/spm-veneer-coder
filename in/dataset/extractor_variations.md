# Extracting Links with JavaScript Fallback (hrefOrOnclick)
## User
How do I extract a destination URL when an element uses `onclick="location.href='/details'"` instead of a standard `href` attribute?
## Assistant
Use the `hrefOrOnclick` base extractor pipe. It first checks for a valid `href` attribute and falls back to extracting the URL from inline `onclick` location assignments.

```vnr
// ✅ Extracts target URL whether defined in href or onclick JavaScript
bind targetUrl: "a.action-btn | hrefOrOnclick";
```

# Handling JS Redirection Buttons (hrefOrOnclick)
## User
I used `bind ctaUrl: "button.buy-now | attr:href";` but it returns null because the button uses inline JavaScript navigation. What should I use?
## Assistant
Use `hrefOrOnclick` instead of `attr:href`. `attr:href` fails when navigation is triggered via `onclick="window.location='/checkout'"`.

```vnr
// ❌ attr:href returns null on buttons without a literal href attribute
bind ctaUrl: "button.buy-now | attr:href";
```

```vnr
// ✅ hrefOrOnclick handles both href attributes and onclick location assignments
bind ctaUrl: "button.buy-now | hrefOrOnclick";
```

# Binding Table Row Action Links (hrefOrOnclick)
## User
How do I bind row links in a table when some links are `<a>` tags and others are `<tr onclick="...">` elements?
## Assistant
Bind the action URL property using `hrefOrOnclick` on the row or child selector.

```vnr
class TableRow {
    bind rowUrl: "self | hrefOrOnclick";
    bind itemTitle: ".title | text";
}

reconstruct "#data-grid" -> UiTableListPage {
    child tableRows extends TableRow {
        selector: "tr.item-row";
    }
}
```

# Extracting URLs from Dummy Href Anchor Tags (hrefOrOnclick)
## User
On my legacy page, anchor tags have `href="#"` and `onclick="document.location.href='/item/42'"`. How do I extract `/item/42`?
## Assistant
`hrefOrOnclick` automatically ignores dummy `href="#"` or `href="javascript:void(0)"` values and extracts the real target path from the `onclick` handler.

```vnr
// ✅ Ignores href="#" and extracts "/item/42" from onclick
bind itemUrl: "a.item-link | hrefOrOnclick";
```

# Navigation Button URL Extraction (hrefOrOnclick)
## User
Can `hrefOrOnclick` extract URLs from `window.location.href = '...'` inside `onclick` attributes?
## Assistant
Yes! `hrefOrOnclick` parses `window.location`, `window.location.href`, `document.location`, and `document.location.href` assignments inside `onclick`.

```vnr
// Extracts target URL from window.location='...' or href
bind redirectUrl: "button.navigate | hrefOrOnclick";
```

# Extracting Label Sibling Text (nextSiblingText)
## User
How do I extract the text value that appears immediately after a label tag, such as `<span>Price:</span> $49.99`?
## Assistant
Use the `nextSiblingText` base extractor. It reads the text node immediately following the matched target element.

```vnr
// ✅ Extracts "$49.99" which comes right after the <span>Price:</span> tag
bind priceLabel: "span.price-label | nextSiblingText";
```

# Adjacent Text Node Extraction (nextSiblingText)
## User
My HTML has `<strong>Author:</strong> John Doe`. `strong | text` returns `"Author:"`. How do I get `"John Doe"`?
## Assistant
Use `nextSiblingText` to target the text node following the `<strong>` element.

```vnr
// ❌ text extractor on strong element returns "Author:"
bind authorName: "strong.author-tag | text";
```

```vnr
// ✅ nextSiblingText returns "John Doe"
bind authorName: "strong.author-tag | nextSiblingText";
```

# Extracting Metadata Sibling Values (nextSiblingText)
## User
How do I extract publication date when the HTML structure is `<i class="icon-calendar"></i> 2026-08-22`?
## Assistant
Target the icon element with `nextSiblingText` to extract the text node following the icon.

```vnr
// ✅ Extracts "2026-08-22" following the calendar icon
bind pubDate: "i.icon-calendar | nextSiblingText";
```

# Next Sibling Text Cleaning (nextSiblingText)
## User
Can I combine `nextSiblingText` with `cleanNumber` to extract numeric values following a label?
## Assistant
Yes! Base extractors like `nextSiblingText` can be chained with transform pipes such as `cleanNumber`.

```vnr
// ✅ Extracts sibling text after "Views:" label and parses metric suffix (e.g. "1.5k" -> "1500")
bind viewCount: "span.views-label | nextSiblingText | cleanNumber";
```

# Sibling Value Binding in Table Metadata (nextSiblingText)
## User
Give an example of using `nextSiblingText` inside a Veneer class definition.
## Assistant
Here is an example binding metadata fields using `nextSiblingText`:

```vnr
class ProductMetadata {
    bind sku: "span.sku-header | nextSiblingText";
    bind stockStatus: "span.stock-header | nextSiblingText";
}
```

# Extracting Form Hidden Inputs (hiddenInputs)
## User
How do I extract all `<input type="hidden">` fields inside a form container for form submission?
## Assistant
Use the `hiddenInputs` base extractor. It serializes all hidden input names and values inside the target container.

```vnr
// ✅ Serializes all hidden inputs inside form#checkout into a JSON structure
bind securityPayload: "form#checkout | hiddenInputs";
```

# Preserving Form Security Tokens (hiddenInputs)
## User
My legacy search form requires CSRF tokens and hidden session IDs to submit. How do I capture them in `UiSearchBar`?
## Assistant
Bind `hiddenFields` on `UiSearchBar` using `form | hiddenInputs`.

```vnr
reconstruct "form#search-form" -> UiSearchBar {
    action: replace;
    hiddenFields: "form#search-form | hiddenInputs";
    submitUrl: "form#search-form | attr:action";
}
```

# Single Input vs Hidden Inputs Extractor (hiddenInputs)
## User
What is the difference between `input[type=hidden] | attr:value` and `form | hiddenInputs`?
## Assistant
`attr:value` extracts a single attribute from a single input, whereas `hiddenInputs` scans an entire form container and extracts all hidden fields as a key-value dictionary payload.

```vnr
// ❌ Extracts only one specific hidden value
bind csrfToken: "input[name=_csrf] | attr:value";
```

```vnr
// ✅ Captures all hidden inputs in the form automatically
bind allHiddenFields: "form | hiddenInputs";
```

# Search Form Hidden Inputs Binding (hiddenInputs)
## User
How do I pass preserved hidden inputs to a component?
## Assistant
Bind the form container with `hiddenInputs` and assign it to the component's `hiddenFields` property.

```vnr
reconstruct "form.search-container" -> UiSearchBar {
    hiddenFields: "form.search-container | hiddenInputs";
}
```

# Multi-Slot Form Hidden Field Preservation (hiddenInputs)
## User
Give a complete example of extracting hidden inputs alongside action and search input bindings.
## Assistant
Here is a complete Veneer Spec reconstruct statement using `hiddenInputs`:

```vnr
reconstruct "#legacy-search" -> UiSearchBar {
    placeholder: "input[name=q] | attr:placeholder";
    submitUrl: "form | attr:action";
    hiddenFields: "form | hiddenInputs";
}
```

# Element Own Selector Extraction (selector)
## User
How do I extract the target element's own unique CSS selector string instead of text or HTML content?
## Assistant
Use `self | selector`. It generates a unique CSS selector (or `data-spm-id` tracking attribute) targeting the element itself.

```vnr
// ✅ Returns a unique CSS selector for the host element
bind ownSelector: "self | selector";
```

# Binding Proxy Click Targets (selector)
## User
I need to trigger a legacy click handler on a card when clicked in React. How do I get the card's selector?
## Assistant
Bind the card's selector using `self | selector` or `.action-link | selector` so events can be proxied to the original DOM.

```vnr
class ItemCard {
    bind title: ".title | text";
    bind targetSelector: "self | selector";
}
```

# Selector Extractor Syntax (selector)
## User
Is `attr:selector` valid syntax for getting an element's selector?
## Assistant
No, `selector` is a standalone base extractor, not an attribute. Use `self | selector` or `<css_selector> | selector`.

```vnr
// ❌ attr:selector is invalid
bind target: "self | attr:selector";
```

```vnr
// ✅ Correct usage of selector extractor
bind target: "self | selector";
```

# Unique Element Tracking via Selector (selector)
## User
How does `selector` work when elements don't have unique IDs or classes?
## Assistant
The runtime `engine.ts` automatically assigns a unique `data-spm-id` attribute to the target element and returns `[data-spm-id="spm-id-..."]`.

```vnr
bind elementPath: "div.item-row | selector";
```

# Dynamic Item Proxy Selector Binding (selector)
## User
Provide a complete example using `selector` in a list page reconstruction.
## Assistant
Here is how to extract element selectors for proxy event handling:

```vnr
class ClickableItem {
    bind label: ".item-name | text";
    bind itemSelector: "a.item-link | selector";
}

reconstruct ".grid" -> UiModernGridPage {
    child gridItems extends ClickableItem {
        selector: ".grid-item";
    }
}
```

# Reconstruct Syntax vs. Class Syntax — Contrast Examples

---

# Why can't I use `bind` inside a `reconstruct` block?
## User
I wrote this code but the compiler keeps giving me an error. What's wrong?

```vnr
reconstruct "#hero-section" -> UiSplitLayout {
    bind imageUrl: ".hero-img | attr:src";
    bind headline: "h1.hero-title | text";
}
```
## Assistant
The `bind` keyword is only valid inside `class` declarations, not inside `reconstruct` or `selector` blocks. In a `reconstruct` block, property assignments are written **directly** as bare `key: value;` expressions (no `bind` keyword). When you need to pull a value dynamically from the HTML, you put the extractor expression on the right-hand side:

```vnr
reconstruct "#hero-section" -> UiSplitLayout {
    imageUrl: ".hero-img | attr:src";
    headline: "h1.hero-title | text";
}
```

The rule is: `bind` belongs in `class` bodies (compile-time scraping schema); `reconstruct` bodies use direct assignment syntax.

---

# When should I use `class` with `bind`, and when should I assign directly in `reconstruct`?
## User
I'm confused about when to use `class { bind prop: "..."; }` versus just writing `prop: "...";` inside `reconstruct`. Can you explain?
## Assistant
Think of it this way:

- **`class` + `bind`**: Used to define a *reusable scraping schema* — a named blueprint for how to extract properties from matched elements. It lives outside any `reconstruct` block and can be reused with `extends`.
- **Direct assignment in `reconstruct`**: Used for one-off static strings or single extractor expressions applied directly on the matched container.

Example using both correctly:

```vnr
class ArticleCard {
    bind title: "h2.entry-title a | text";
    bind url: "h2.entry-title a | attr:href";
    bind publishDate: "time.entry-date | attr:datetime";
}

reconstruct "#blog-feed" -> UiModernGridPage {
    pageTitle: "Latest Posts";       // static string — direct assignment
    height: "100vh";                  // static string — direct assignment

    child items extends ArticleCard { // uses the class blueprint
        selector: "article.post";
    }
}
```

The `bind` keyword is exclusive to `class` bodies. Never write `bind` inside `reconstruct`, `selector`, or `child` blocks.

---

# Wrong: using arrow inside child
## User
My code throws a parser error on the `child` line. What's wrong?

```vnr
reconstruct "#product-grid" -> UiModernGridPage {
    pageTitle: "Products";

    child items -> UiImageCard {
        selector: ".product-card";
        bind title: ".product-name | text";
    }
}
```
## Assistant
There are two errors here:

1. **`bind` is not valid inside a `child` block** — use direct assignment instead.
2. **The `->` arrow syntax for `child` is only valid for the inline component-mount shorthand** — but in this context, the `bind` lines are inside the child block, making it a mix of two incompatible forms.

If you want to scrape per-item properties, use the **plain child block** form (no arrow, no `bind`):

```vnr
reconstruct "#product-grid" -> UiModernGridPage {
    pageTitle: "Products";

    child items {
        selector: ".product-card";
        title: ".product-name | text";    // direct assignment, no "bind"
    }
}
```

Or, if you want to mount a component per child and also define a class separately:

```vnr
class ProductCard {
    bind title: ".product-name | text";
    bind imageUrl: "img | attr:src";
}

reconstruct "#product-grid" -> UiModernGridPage {
    pageTitle: "Products";

    child items extends ProductCard {
        selector: ".product-card";
    }
}
```

---

# `child` inline component mount vs extends — what's the difference?
## User
What is the difference between `child items -> UiImageCard { ... }` and `child items extends SomeClass { ... }`?
## Assistant
They serve different purposes:

- **`child items -> UiImageCard { ... }` (inline mount)**: Mounts a React component directly per matched element *without* a separately defined class. The child block contains only static props (not extractors) and optionally a `selector`. It's a shorthand for when you don't need a reusable class.
- **`child items extends SomeClass { ... }` (class extends)**: Uses a pre-defined `class` blueprint for scraping. The matched element's data is extracted using the `bind` rules defined in the class.

Both forms are valid. Use inline mount when scraping is not needed (static data only), and `extends` when you need dynamic per-element extraction via `bind` rules.

```vnr
// Inline mount — static props only
child items -> UiImageCard {
    selector: ".photo-card";
    aspectRatio: "square";
    width: "200px";
}

// Extends — uses class bind rules for dynamic extraction
class PhotoCard {
    bind imageUrl: "img | attr:src";
    bind title: "figcaption | text";
}

child items extends PhotoCard {
    selector: ".photo-card";
}
```

---

# Using `bind` in a `child` block inside a reconstruct
## User
I have a `child` block inside a `reconstruct` and I'm getting a parser error on the `bind` line. Here's my code:

```vnr
reconstruct "#news-feed" -> UiCommentListPage {
    pageTitle: "News";

    child threads {
        selector: ".news-item";
        bind postUrl: "a.news-link | attr:href";
        bind postUser: ".author-name | text";
    }
}
```
## Assistant
The `bind` keyword is not allowed in `child` blocks either — only in `class` declarations. Inside `child` blocks, extractor rules are written as **bare key: value** assignments:

```vnr
reconstruct "#news-feed" -> UiCommentListPage {
    pageTitle: "News";

    child threads {
        selector: ".news-item";
        postUrl: "a.news-link | attr:href";
        postUser: ".author-name | text";
    }
}
```

Or, extract the bindings into a class for reuse:

```vnr
class NewsItem {
    bind postUrl: "a.news-link | attr:href";
    bind postUser: ".author-name | text";
}

reconstruct "#news-feed" -> UiCommentListPage {
    pageTitle: "News";

    child threads extends NewsItem {
        selector: ".news-item";
    }
}
```

---

# Correct syntax for `child` extends vs wrong arrow usage
## User
I tried to extend a class inside a child block using arrow syntax but got a parser error:

```vnr
class BookCard {
    bind title: "h3.book-title | text";
    bind author: ".book-author | text";
}

reconstruct "#book-list" -> UiModernGridPage {
    child items -> BookCard {
        selector: ".book-item";
    }
}
```
## Assistant
The `->` arrow is only used in two specific forms:

1. **`reconstruct "selector" -> ComponentName { ... }`** — mapping a container to a layout component.
2. **`child name -> ComponentName { ... }`** — inline component mount with static props (no `class` reference).

You cannot use `->` to reference a `class` name. To apply a class blueprint to child scraping, use the `extends` keyword:

```vnr
class BookCard {
    bind title: "h3.book-title | text";
    bind author: ".book-author | text";
}

reconstruct "#book-list" -> UiModernGridPage {
    child items extends BookCard {
        selector: ".book-item";
    }
}
```

---

# Static prop vs. dynamic extractor in reconstruct
## User
When I write a property value in a `reconstruct` block, how does the compiler know if it's a static string or an extractor expression that should query the DOM?
## Assistant
Both use the same bare `key: "value";` syntax, but the compiler interprets the value string differently:

- If the value is a **plain string** (e.g. `"Latest Posts"`, `"100vh"`), it's emitted as-is to the manifest JSON.
- If the value contains an **extractor expression** (a CSS selector, `self`, or `attr:`, `text`, `hrefOrOnclick`, etc., optionally followed by pipe operators like `| cleanNumber`), the compiler passes it to the runtime extraction engine.

You can mix both in the same block:

```vnr
reconstruct "#news-section" -> UiModernGridPage {
    pageTitle: "Tech News";                       // static
    height: "100vh";                              // static
    dateRangeText: "span.period-label | text";    // dynamic — extracted from DOM
}
```

The runtime determines which is which based on whether the value string contains a valid CSS-selector-like expression with a `|` pipe chain.

---

# Multiple components in one .vnr file
## User
Can I have multiple `selector` and `reconstruct` blocks in a single `.vnr` file? How should I structure it?
## Assistant
Yes, a `.vnr` file can contain any number of `selector`, `reconstruct`, and `class` declarations. They are processed in document order. A common pattern is to handle navigation with `selector` first, then the main content with `reconstruct`:

```vnr
// 1. Replace legacy nav
selector "#site-nav" -> UiNavHeader {
    action: replace;
    sticky: true;
    bind logoUrl: ".nav-logo img | attr:src";
    child primaryLinks {
        selector: "ul.nav-menu li a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}

// 2. Hide ad sidebar
selector "#ad-sidebar" -> UiNavHeader {
    action: hide;
}

// 3. Reconstruct main content
class ArticleRow {
    bind title: "h2.article-title a | text";
    bind url: "h2.article-title a | attr:href";
}

reconstruct "#main-content" -> UiTableListPage {
    pageTitle: "Articles";
    columns: R"([
      { "key": "title", "header": "Title", "type": "link", "urlKey": "url" }
    ])";
    child tableRows extends ArticleRow {
        selector: "div.article-card";
    }
}
```

---

# Can I reference a class in a `selector` block?
## User
I have a class defined and I want to use `extends` in a `selector` block. Is that valid?
## Assistant
No. `extends` is only valid inside `child` blocks, not inside `selector` blocks. A `selector` block is for individual element replacement or hiding, not for batch child-item scraping:

```vnr
// WRONG
class NavSchema {
    bind logoUrl: "img | attr:src";
}

selector "#header" -> UiNavHeader extends NavSchema {  // ❌ invalid
    action: replace;
}
```

Instead, use direct property assignments inside `selector`:

```vnr
// CORRECT
selector "#header" -> UiNavHeader {
    action: replace;
    bind logoUrl: "img | attr:src";   // ❌ also wrong — no bind in selector
}

// FULLY CORRECT
selector "#header" -> UiNavHeader {
    action: replace;
    logoUrl: "img | attr:src";   // ✅ direct assignment
}
```

`class` + `extends` patterns only apply to `child` blocks inside `reconstruct`.

---

# How does `selector` differ from `reconstruct` in terms of syntax?
## User
What are the syntactic differences between a `selector` block and a `reconstruct` block?
## Assistant
| Feature | `selector` | `reconstruct` |
|---|---|---|
| Target | Single element (nav, sidebar, modal) | Container of multiple children |
| Required field | `action: replace` or `action: hide` | Component name after `->` |
| Child blocks | Not supported | Supported via `child` |
| Class `extends` | Not supported | Supported in `child` blocks |
| Dynamic extractor values | Supported (bare assignment) | Supported (bare assignment) |
| `bind` keyword | ❌ Not allowed | ❌ Not allowed (only in `class`) |

```vnr
// selector — targets one element
selector "#top-nav" -> UiNavHeader {
    action: replace;
    logoUrl: ".brand img | attr:src";
}

// reconstruct — targets a container with children
reconstruct "#product-list" -> UiModernGridPage {
    pageTitle: "Products";
    child items {
        selector: ".product-card";
        title: "h3 | text";
    }
}
```

---

# Nested `child` blocks — when are they valid?
## User
Can I nest `child` blocks inside other `child` blocks? In what situations?
## Assistant
Yes, but only for components that accept nested children (like `UiCommentListPage` threads → comments, or `UiStatsDashboard` sections → items). Nesting reflects the data hierarchy expected by the component's prop API:

```vnr
reconstruct "#forum" -> UiCommentListPage {
    pageTitle: "Forum";

    child threads {
        selector: ".thread";
        postUrl: "h3 a | attr:href";
        postUser: ".author | text";
        postDate: "time | attr:datetime";

        child tags {
            selector: ".tag-list a";
            label: "self | text";
            url: "self | attr:href";
        }

        child comments {
            selector: ".comment";
            author: ".comment-author | text";
            body: ".comment-body | text";
            date: ".comment-date | attr:datetime";
        }
    }
}
```

Nesting is not valid for components like `UiModernGridPage` or `UiTableListPage` that only have a single flat `child items`/`child tableRows` list.

---

# `class` inheritance chain — how deep can it go?
## User
Can I chain multiple `class` declarations using `extends`? How do the bindings merge?
## Assistant
Yes, you can chain classes to any depth. The child class's bindings override those of parent classes when there's a name collision:

```vnr
class BaseItem {
    bind id: "self | attr:id";
    bind title: "h3 | text";
}

class LinkableItem extends BaseItem {
    bind url: "h3 a | attr:href";
    bind title: "h3 a | text";  // overrides BaseItem.title
}

class ProductItem extends LinkableItem {
    bind price: ".price | text | cleanNumber";
    bind imageUrl: "img | attr:src";
}

reconstruct "#shop" -> UiModernGridPage {
    child items extends ProductItem {
        selector: ".product";
    }
}
```

Here `ProductItem` inherits `id` from `BaseItem` (unmodified), `url` from `LinkableItem`, uses `LinkableItem`'s override of `title`, and adds `price` and `imageUrl`. The compiler resolves the full chain at compile time; classes themselves don't appear in the manifest output.

# Inline component mount for a raw table

## User
Explain what the following Veneer Spec (.vnr) code does:

```vnr
child tableRows -> UiTable {
    columns: R"([
      { "key": "id", "header": "ID", "width": "60px", "align": "center" },
      { "key": "title", "header": "Title", "align": "left" },
      { "key": "author", "header": "Author", "width": "120px" }
    ])";
}
```

## Assistant
This uses the inline component-mount form of `child`: instead of just declaring a scraped list (`child tableRows { selector: ...; bind ...; }`), the `-> UiTable` arrow tells the compiler to render each collected row through the `UiTable` component itself rather than treating `tableRows` as a plain prop array on the parent.

The `columns` property is a static prop passed straight to `UiTable`, supplied as a raw-string JSON array (`R"([...])"`) so the embedded double quotes need no escaping. Each entry configures one column's `key` (which row field to read), `header` (column title text), and optional `width`/`align`. Since no `selector`/`bind` lines are present in this snippet, the row data itself would need to come from a sibling `bind`/`child` context — in a full reconstruct this block would sit alongside a `selector` and `bind` lines describing where each row's `id`, `title`, and `author` values are scraped from.

---

# Generating an inline UiImageCard grid mount

## User
Write a Veneer Spec (.vnr) snippet that mounts each thumbnail in a legacy `.thumb` grid as a `UiImageCard`, using a square aspect ratio and a 180px width, scraping the image, link, title, and DOM id from each thumbnail.

```html
<div id="post-list">
  <span class="thumb" id="p9182">
    <a href="/post/9182">
      <img src="/thumbs/9182.jpg" title="landscape, forest" />
    </a>
  </span>
</div>
```

## Assistant
```vnr
child items -> UiImageCard {
    selector: "#post-list .thumb";
    width: "180px";
    aspectRatio: "square";
    imageFit: "cover";
    showTitle: true;

    bind imageUrl: "img | attr:src";
    bind linkUrl: "a | attr:href";
    bind title: "img | attr:title";
    bind id: "self | attr:id";
}
```

Static props (`width`, `aspectRatio`, `imageFit`, `showTitle`) are shared by every card in the list, while the four `bind` lines pull the per-item values out of each matched `.thumb` element.

---

# Combining extends with an inline component mount

## User
Explain what the following Veneer Spec (.vnr) code does, and why both `extends` and `-> UiPaginationBar` appear on the same `child` block:

```vnr
child pageLinks extends PageLink -> UiPaginationBar {
    selector: "#paginator .pagination a";
    paramName: "pid";
    bind label: "self | text";
    bind url: "self | attr:href";
}
```

## Assistant
`extends` and the `-> Component` arrow are independent features and can be combined on the same `child` declaration: `extends PageLink` pulls in whatever `bind` lines the `PageLink` class already declares (here, presumably `label` and `url`, which are then re-declared explicitly and would simply override the inherited ones), while `-> UiPaginationBar` tells the compiler to render the scraped list through the `UiPaginationBar` component instead of exposing `pageLinks` as a plain array prop on the parent.

The static `paramName: "pid";` property is passed directly to `UiPaginationBar`, telling it which query-string parameter to inspect on each link's URL in order to detect the currently active page.

---

# Generating a tag badge with add/remove actions

## User
Write a Veneer Spec (.vnr) snippet that mounts each `<li>` in a `#tag-sidebar` as a `UiTagBadge`, extending the shared `TagItem` class, and including the tag's add and remove filter links (the 2nd and 3rd anchors in each `<li>`).

## Assistant
```vnr
child tags extends TagItem -> UiTagBadge {
    selector: "#tag-sidebar li";
    bind label: "a:nth-of-type(1) | text";
    bind count: "span.tag-count | text";
    bind href: "a:nth-of-type(1) | attr:href";
    bind addUrl: "a:nth-of-type(2) | attr:href";
    bind removeUrl: "a:nth-of-type(3) | attr:href";
}
```

---

# Full column-type configuration for a table list page

## User
Based on the following legacy table, write a Veneer Spec (.vnr) reconstruct targeting `UiTableListPage`. One column is a checkbox, two are links to other pages, and one is plain text.

```html
<div id="content">
  <table class="highlightable">
    <tr class="tableheader"><th></th><th>Alias</th><th>To Tag</th><th>Reason</th></tr>
    <tr>
      <td><input type="checkbox" class="pending" /></td>
      <td><a href="/tag/12">oldname</a></td>
      <td><a href="/tag/44">newname</a></td>
      <td>Merged during cleanup</td>
    </tr>
  </table>
</div>
```

## Assistant
```vnr
reconstruct "#content:has(table.highlightable)" -> UiTableListPage {
    urlPattern: "page=alias&s=list";
    pageTitle: "Tag Aliases";
    height: "calc(100vh - 78px)";
    columns: R"([
      { "key": "pending", "header": "Pending", "width": "60px", "type": "checkbox" },
      { "key": "aliasName", "header": "Alias", "type": "link", "urlKey": "aliasUrl" },
      { "key": "toName", "header": "To Tag", "type": "link", "urlKey": "toUrl" },
      { "key": "reason", "header": "Reason / Discussion", "type": "text" }
    ])";

    child tableRows {
        selector: "#content table.highlightable tr:not(.tableheader)";
        bind pending: "td:nth-child(1) input[type='checkbox'] | attr:class";
        bind aliasName: "td:nth-child(2) a | text";
        bind aliasUrl: "td:nth-child(2) a | attr:href";
        bind toName: "td:nth-child(3) a | text";
        bind toUrl: "td:nth-child(3) a | attr:href";
        bind reason: "td:nth-child(4) | text";
    }
}
```

Note the `urlKey` fields: `type: "link"` columns don't render their own `key` value as the href — they look up a *separate* row field named by `urlKey` for the destination, which is why `aliasUrl`/`toUrl` are scraped as their own `bind` lines alongside `aliasName`/`toName`.

---

# Nested comment threads with tags and replies

## User
Explain what the following Veneer Spec (.vnr) code does, in particular the two nested `child` blocks inside `child threads`:

```vnr
reconstruct "#content:has(#comment-list)" -> UiCommentListPage {
    urlPattern: "page=comment&s=list";
    pageTitle: "Comments";

    child threads {
        selector: "#comment-list > div.post";
        bind id: "self | attr:id";
        bind thumbnailUrl: ".col1 img | attr:src";
        bind postUrl: ".col1 a | attr:href";
        bind postDate: ".col2 span.info:nth-child(1) | text";
        bind postUser: ".col2 span.info:nth-child(2) | text";

        child tags {
            selector: ".col2 .tags span";
            bind label: "a | text";
            bind url: "a | attr:href";
            bind type: "self | attr:class";
        }

        child comments {
            selector: ".response-list div.post";
            bind author: ".author h6 a | text";
            bind date: ".author span.date | text";
            bind body: ".content .body | text";
        }
    }
}
```

## Assistant
`UiCommentListPage` expects a `threads` array where each thread object can itself contain nested `tags` and `comments` arrays, matching the `CommentThread` schema. The outer `child threads` block scrapes one thread object per `div.post` under `#comment-list`, reading the id, thumbnail, post link, date, and username directly off that element.

The two nested `child` blocks (`tags` and `comments`) are scoped *inside* the matched thread element by default (the standard container-scope rule) — so `.col2 .tags span` and `.response-list div.post` are searched only within the current thread's own DOM subtree, not the whole page. This produces, for every thread, a `tags: [...]` array from its tag spans and a `comments: [...]` array from its own reply list, exactly matching the shape `UiCommentListPage` expects.

---

# Generating a ranked stats dashboard with nested sections

## User
Based on this HTML, write a Veneer Spec (.vnr) reconstruct targeting `UiStatsDashboard`. Each `.toptencont` block is a ranked leaderboard section with its own title and rows.

```html
<div id="content">
  <h2>Last 30 days</h2>
  <a href="/stats/tags">Top Tags</a>
  <div class="toptencont">
    <table>
      <thead><tr><th>Top Uploaders</th></tr></thead>
      <tbody>
        <tr><td>1</td><td>4,021</td><td><a href="/user/12">yuki_art</a></td></tr>
      </tbody>
    </table>
  </div>
</div>
```

## Assistant
```vnr
reconstruct "#content:has(div.toptencont)" -> UiStatsDashboard {
    urlPattern: "page=stats";
    pageTitle: "Booru Statistics Dashboard";
    height: "calc(100vh - 78px)";

    bind dateRangeText: "h2 | text";

    child navLinks extends NavLink {
        selector: "#content > a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }

    child sections {
        selector: "div.toptencont";
        bind title: "thead tr th | text";

        child items {
            selector: "tbody tr";
            bind place: "td:nth-child(1) | text";
            bind amount: "td:nth-child(2) | text";
            bind name: "td:nth-child(3) a | text";
            bind profileUrl: "td:nth-child(3) a | attr:href";
        }
    }
}
```

Each `div.toptencont` becomes one `StatSection` (`title` read from its own `<thead>`), and the nested `child items` block, scoped inside that section, produces the `StatItem[]` ranked rows for it — so `sections` ends up as an array of independently-scraped leaderboard cards, one per matched `.toptencont`.

---

# Dashboard cards scraped from sibling text

## User
Explain what the following Veneer Spec (.vnr) code does, especially the `bind description` line:

```vnr
reconstruct "#user-index" -> UiDashboardPage {
    urlPattern: "page=account&s=home";
    pageTitle: "My Account Home";
    subTitle: "Manage your settings, options, and account status.";

    child cards {
        selector: "#user-index h4";
        bind title: "self | text";
        bind url: "a | attr:href";
        bind urlLabel: "a | text";
        bind description: "self | nextSiblingText";
    }
}
```

## Assistant
Each `DashboardCard` is scraped from one `<h4>` under `#user-index`. `title` and `url`/`urlLabel` come from the heading's own text and an anchor nested inside it. `description` is different: it uses the `nextSiblingText` base extractor, which reads the text content of whatever element comes immediately *after* the matched `<h4>` in the DOM — a common legacy pattern where a heading and its explanatory paragraph are siblings rather than nested inside one wrapper.

---

# Split layout with a document-scoped sidebar

## User
Write a Veneer Spec (.vnr) reconstruct targeting `UiSplitLayout` for a post detail page, where the main image is `#image`, and the tag list and action buttons actually live in a `#tag-sidebar` element outside the main `#post-view` container.

## Assistant
```vnr
reconstruct "#post-view" -> UiSplitLayout {
    urlPattern: "page=post&s=view";
    sidebarWidth: "300px";
    sidebarSide: "left";
    imageFit: "contain";
    showSearch: true;
    searchSubmitUrl: "https://example-booru.test/index.php?page=post&s=list";
    searchParamName: "tags";

    bind statisticsHtml: "#stats ul | html";

    child imageSlot {
        selector: "#image";
        bind src: "self | attr:src";
        bind alt: "self | attr:alt";
    }

    child tags {
        selector: "#tag-sidebar li[class*='tag-type-']";
        scope: "document";
        bind name: "a:last-of-type | text";
        bind count: "span.tag-count | text";
        bind type: "self | attr:class";
        bind url: "a:last-of-type | attr:href";
    }

    child buttons {
        selector: ".link-list a";
        scope: "document";
        bind label: "self | text";
        bind url: "self | hrefOrOnclick";
        bind targetSelector: "self | selector";
    }
}
```

Both `tags` and `buttons` need `scope: "document";` since `#tag-sidebar` and `.link-list` live outside `#post-view`, the matched container — without it the compiler would search only inside `#post-view` and find nothing.

---

# Standalone scroll panel with statistics HTML

## User
Write a Veneer Spec (.vnr) reconstruct targeting `UiScrollPanel` for a `#sidebar` element, with a 300px width, an embedded search bar, and a statistics block pulled from `#stats ul` as raw HTML.

## Assistant
```vnr
reconstruct "#sidebar" -> UiScrollPanel {
    width: "300px";
    showSearch: true;
    searchPlaceholder: "Search tags...";
    searchSubmitUrl: "https://example-booru.test/index.php?page=post&s=list";
    searchParamName: "tags";

    bind statisticsHtml: "#stats ul | html";

    child tags extends TagItem {
        selector: "#tag-sidebar li";
        bind name: "a:last-of-type | text";
        bind count: "span.tag-count | text";
        bind type: "self | attr:class";
        bind url: "a:last-of-type | attr:href";
    }

    child buttons extends ButtonItem {
        selector: ".link-list a";
        bind label: "self | text";
        bind url: "self | hrefOrOnclick";
        bind targetSelector: "self | selector";
    }
}
```

---

# Grid page with tag groups and mobile responsive tuning

## User
Complete this Veneer Spec (.vnr) snippet for a `UiModernGridPage` gallery reconstruct so it groups the sidebar tags into Artists/Copyrights/Characters/General/Meta sections, and shows 2 columns with an 8px gap on mobile:

```vnr
reconstruct "#post-list" -> UiModernGridPage {
    urlPattern: "page=post&s=list";
    pageTitle: "Gallery";
    hideSidebarOnMobile: true;
    showSearch: true;
    searchSubmitUrl: "https://example-booru.test/index.php?page=post&s=list";
    searchParamName: "tags";
    ...
}
```

## Assistant
```vnr
reconstruct "#post-list" -> UiModernGridPage {
    urlPattern: "page=post&s=list";
    pageTitle: "Gallery";
    hideSidebarOnMobile: true;
    showSearch: true;
    searchSubmitUrl: "https://example-booru.test/index.php?page=post&s=list";
    searchParamName: "tags";

    mobileBreakpoint: 720;
    mobileColumns: 2;
    mobileGap: "8px";

    tagGroups: R"([
      { "title": "Artists", "typeKey": "artist" },
      { "title": "Copyrights", "typeKey": "copyright" },
      { "title": "Characters", "typeKey": "character" },
      { "title": "General", "typeKey": "general" },
      { "title": "Meta", "typeKey": "metadata" }
    ])";

    child items {
        selector: "#post-list .thumb";
        bind imageUrl: "img | attr:src";
        bind linkUrl: "a | attr:href";
        bind title: "img | attr:title";
        bind id: "self | attr:id";
    }

    child tags extends TagItem {
        selector: "#tag-sidebar li";
        bind addUrl: "a:nth-of-type(2) | attr:href";
        bind removeUrl: "a:nth-of-type(3) | attr:href";
    }
}
```

Each `tagGroups` entry's `typeKey` is matched against every scraped tag's own `type` field, so the flat `child tags` list gets split into the five labeled sidebar sections automatically — the grouping happens purely from that string match, not from any structural nesting in the `.vnr` source.

---

# Stacked nav header with secondary links

## User
Write a Veneer Spec (.vnr) reconstruct that replaces `#header` with a `UiNavHeader` using the `stacked` layout variant, reading the logo from `#logo img`, with primary links from `.main-nav` and secondary (user account) links from `.user-nav`.

## Assistant
```vnr
reconstruct "#header" -> UiNavHeader {
    siteName: "Example Wiki";
    logoHref: "/";
    layout: "stacked";
    hideOnMobile: false;

    bind logoUrl: "#logo img | attr:src";

    child primaryLinks extends NavLink {
        selector: "#navbar ul.main-nav a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }

    child secondaryLinks extends NavLink {
        selector: "#navbar ul.user-nav a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

---

# Hero landing page with an embedded search bar

## User
Write a Veneer Spec (.vnr) reconstruct that replaces a static homepage `#static-index` with `UiHeroLanding`, including a tagline, CTA button, embedded tag search, and quick links scraped from `#links a`.

## Assistant
```vnr
reconstruct "#static-index" -> UiHeroLanding {
    urlPattern: R"(example-booru\.test\/?(?:index\.php)?$)";
    tagline: "Anime picture search engine";
    subtext: "Browse millions of safe anime illustrations, updated hourly.";
    ctaLabel: "Browse Gallery";
    ctaUrl: "https://example-booru.test/index.php?page=post&s=list&tags=all";
    searchPlaceholder: "Search tags... (e.g. blue_hair 1girl)";
    searchSubmitUrl: "https://example-booru.test/index.php?page=post&s=list";
    searchParamName: "tags";

    bind siteName: "img[alt='Example Booru'] | attr:alt";
    bind logoUrl: "img[alt='Example Booru'] | attr:src";

    child primaryLinks extends NavLink {
        selector: "#links a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

---

# Search bar forwarding hidden form fields

## User
Write a Veneer Spec (.vnr) selector block that replaces `#search-box` with a `UiSearchBar`, preserving two hidden fields (`page=post`, `s=list`) that the legacy form always submitted alongside the tag query.

## Assistant
```vnr
selector "#search-box" -> UiSearchBar {
    action: replace;
    placeholder: "Search posts by tag...";
    submitUrl: "https://example-booru.test/index.php?page=post&s=list";
    queryParamName: "tags";
    method: "GET";
    hiddenFields: R"([
      { "name": "page", "value": "post" },
      { "name": "s", "value": "list" }
    ])";

    bind defaultValue: "form input[name='tags'] | attr:value";
}
```

Without `hiddenFields`, submitting the new search form would drop the `page`/`s` parameters the legacy backend relies on to route the request to the right handler.

---

# Minimal global toast portal mount

## User
What is the minimal Veneer Spec (.vnr) needed to mount `UiToastContainer` once, globally, for every page on a site?

## Assistant
```vnr
reconstruct "#global-toast-portal" -> UiToastContainer {
    urlPattern: ".*";
    position: "bottom-right";
}
```

Since `UiToastContainer` takes no scraped `bind`/`child` data, this is close to the smallest possible `reconstruct` block: a container selector, a wildcard `urlPattern` so it mounts on every route, and a single static prop for corner placement.

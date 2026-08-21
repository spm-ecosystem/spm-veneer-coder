# React component specifications: UiCommentListPage
## User
What is the purpose of `UiCommentListPage` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiCommentListPage` modernizes threaded comments sections, post discussions, or feedback boards.

### Properties (Props API)
- `pageTitle` (string, default: `'Comments'`): Heading text.
- `height` (string, default: `'100vh'`): Layout height constraint.

### Nested Child Blocks
- `child threads`: Card elements containing comment thread metadata. Expected properties:
  - `id` (string): Thread ID.
  - `thumbnailUrl` (string): Image preview link.
  - `postUrl` (string): Destination path to full post.
  - `postDate` (string): Original timestamp text.
  - `postUser` (string): Creator username.
  - `postRating` (string, optional): Content rating descriptor.
  - `postScore` (string, optional): Vote count or score text.
  - `child tags` (nested under threads): Tag pills associated with thread (`label`, `url`, `type`).
  - `child comments` (nested under threads): Inline responses list (`author`, `authorUrl`, `date`, `body`).
- `child pageLinks`: Pagination buttons list (`label`, `url`).

### Veneer Spec Example
```vnr
reconstruct "#comment-feed" -> UiCommentListPage {
    pageTitle: "Community Discussion";
    height: "100vh";

    child threads {
        selector: ".legacy-post";
        bind id: "self | attr:id";
        bind thumbnailUrl: "img.preview | attr:src";
        bind postUrl: "a.title-link | attr:href";
        bind postDate: ".meta span.date | text";
        bind postUser: ".meta span.user | text";

        child tags {
            selector: ".tags-wrap span";
            bind label: "a | text";
            bind url: "a | attr:href";
            bind type: "self | attr:class";
        }

        child comments {
            selector: ".replies .reply-box";
            bind author: "h6 a | text";
            bind authorUrl: "h6 a | attr:href";
            bind date: "span.date | text";
            bind body: ".reply-text | text";
        }
    }
}
```

---

# React component specifications: UiDashboardPage
## User
What is the purpose of `UiDashboardPage` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiDashboardPage` provides a card-based dashboard layout suitable for user account hubs, settings index pages, or admin option directories.

### Properties (Props API)
- `pageTitle` (string, default: `'Dashboard'`): Heading title of the dashboard header.
- `subTitle` (string, optional): Description subtitle rendered below pageTitle.
- `height` (string, default: `'100vh'`): Page wrapper height limit.

### Nested Child Blocks
- `child cards`: List of action/link cards. Expected properties:
  - `title` (string): Card option header.
  - `description` (string, optional): Detail copy explaining the card action.
  - `url` (string): Target destination link for the button.
  - `urlLabel` (string, optional, default: `'Open'`): Visible text on the button link.

### Veneer Spec Example
```vnr
reconstruct "#settings-panel" -> UiDashboardPage {
    pageTitle: "My Profile Settings";
    subTitle: "Configure your billing options, credentials, and details.";
    height: "calc(100vh - 60px)";

    child cards {
        selector: ".settings-row";
        bind title: "h4 | text";
        bind url: "a.action-btn | attr:href";
        bind urlLabel: "a.action-btn | text";
        bind description: "p.description | text";
    }
}
```

---

# React component specifications: UiStatsDashboard
## User
What is the purpose of `UiStatsDashboard` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiStatsDashboard` renders a statistical overview leaderboard layout, presenting ranking tables (top categories, active members) split into card panels.

### Properties (Props API)
- `pageTitle` (string, default: `'Statistics'`): Title text displayed in the header.
- `dateRangeText` (string, default: `'All time'`): Timeframe string rendered in top timeframe badge.
- `height` (string, default: `'100vh'`): Layout height constraint.

### Nested Child Blocks
- `child navLinks`: Navigation tabs array. Expected properties:
  - `label` (string): Button label text.
  - `url` (string): Target route.
- `child sections`: Leaderboard card containers. Expected properties:
  - `title` (string): Section heading text.
  - `child items` (nested under sections): Ranked data rows list. Expected properties:
    - `place` (string, optional): Ranked position (e.g. `'#1'`).
    - `amount` (string): Value quantity or percentage label.
    - `name` (string): Item/member text name.
    - `profileUrl` (string, optional): Detail redirection link.

### Veneer Spec Example
```vnr
reconstruct "#stats-container" -> UiStatsDashboard {
    pageTitle: "Board Leaderboard";
    dateRangeText: "h2.timeframe-label | text";

    child navLinks {
        selector: "div.tabs a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }

    child sections {
        selector: "div.stats-card";
        bind title: "h3.card-title | text";

        child items {
            selector: "table.leaderboard tbody tr";
            bind place: "td:nth-child(1) | text";
            bind amount: "td:nth-child(2) | text";
            bind name: "td:nth-child(3) a | text";
            bind profileUrl: "td:nth-child(3) a | attr:href";
        }
    }
}
```

---

# React component specifications: UiTableListPage
## User
What is the purpose of `UiTableListPage` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiTableListPage` provides a tabular list view wrapper (integrating `UiTable`) for directories, search databases, or document tables.

### Properties (Props API)
- `pageTitle` (string, default: `'List'`): Heading text.
- `columns` (TableColumnConfig[], required): Column configuration schema, passed as an escaped JSON array raw-string.
- `height` (string, default: `'100vh'`): Layout wrapper height constraint.

### Nested Child Blocks
- `child tableRows`: Renders table rows dataset. Bindings must correspond to the keys defined inside `columns` array.
- `child pageLinks`: Pagination buttons list (`label`, `url`).

### `TableColumnConfig` Field Schema
- `key` (string): Field property to read from the matched `tableRows` row object.
- `header` (string): Visible text label in column head.
- `width` (string, optional): Column width constraint.
- `align` (string, optional): Alignment (`'left' | 'center' | 'right'`).
- `type` (string, optional): Sizer type (`'text' | 'link' | 'html' | 'badge' | 'checkbox' | 'date' | 'currency'`).
  - `'date'`: Parses string/numeric timestamps into locale date layouts and enables chronological sorting.
  - `'currency'`: Formats prices as USD currency text (`$1,200.00`) and enables correct numerical sorting.
- `urlKey` (string, optional): Read path containing URL target (required when `type` is `'link'`).
- `badgeStyleKey` (string, optional): Read path containing badge status key (used when `type` is `'badge'`).

### Veneer Spec Example
```vnr
reconstruct "#members-dir" -> UiTableListPage {
    pageTitle: "Member Directory";
    columns: R"([
      { "key": "name", "header": "User", "type": "link", "urlKey": "profileUrl" },
      { "key": "joinDate", "header": "Registered", "type": "date" },
      { "key": "balance", "header": "Balance", "type": "currency" },
      { "key": "status", "header": "Status", "type": "badge", "badgeStyleKey": "statusKey" }
    ])";

    child tableRows {
        selector: "table.legacy-grid tr:not(.header-row)";
        bind name: "td:nth-child(1) a | text";
        bind profileUrl: "td:nth-child(1) a | attr:href";
        bind joinDate: "td:nth-child(2) | text";
        bind balance: "td:nth-child(3) | text";
        bind status: "td:nth-child(4) span | text";
        bind statusKey: "td:nth-child(4) span | attr:class";
    }
}
```

---

# React component specifications: UiSearchBar
## User
What is the purpose of `UiSearchBar` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiSearchBar` renders a header search bar form wrapper supporting search query inputs, hidden fields, and GET/POST submissions.

### Properties (Props API)
- `placeholder` (string, default: `'Search…'`): Input default helper text.
- `defaultValue` (string, default: `''`): Initial query string.
- `submitUrl` (string): Target endpoint for form submit.
- `queryParamName` (string, default: `'tags'`): Input name key assigned on submission.
- `method` (string, default: `'GET'`): Submission method (`'GET' | 'POST'`).
- `hiddenFields` (array of name/value pairs, optional): Hidden parameters forwarded on submit.

### Veneer Spec Example
```vnr
reconstruct "#searchform-wrap" -> UiSearchBar {
    placeholder: "Search images by tag...";
    submitUrl: "/posts";
    queryParamName: "tags";
    method: "GET";
    hiddenFields: R"([
      { "name": "page", "value": "post" },
      { "name": "s", "value": "list" }
    ])";

    bind defaultValue: "form input[name='tags'] | attr:value";
}
```

---

# React component specifications: UiNavHeader
## User
What is the purpose of `UiNavHeader` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiNavHeader` replaces legacy site headers with a modern navigation bar.

### Properties (Props API)
- `siteName` (string, default: `'Site'`): Fallback brand label when no logo URL is set.
- `logoUrl` (string, optional): Brand logo image source path.
- `logoHref` (string, default: `'/'`): Redirection link when clicking logo.
- `layout` (string, default: `'standard'`): Layout configuration (`'standard' | 'stacked' | 'minimal'`).
- `hideOnMobile` (boolean, default: `false`): Toggles responsive hiding.
- `mobileBreakpoint` (number, default: `720`): Width trigger for mobile layout.

### Nested Child Blocks
- `child primaryLinks`: Left navigation tabs (`{ label, url }`).
- `child secondaryLinks`: Right utility/user profile actions (`{ label, url }`).

### Veneer Spec Example
```vnr
reconstruct "#legacy-nav" -> UiNavHeader {
    siteName: "Developer Hub";
    logoHref: "/";
    layout: "standard";

    bind logoUrl: ".logo-wrap img | attr:src";

    child primaryLinks {
        selector: "ul.main-links a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

---

# React component specifications: UiImageCard
## User
What is the purpose of `UiImageCard` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiImageCard` renders thumbnail card items for gallery feeds, grid layouts, and search results.

### Properties (Props API)
- `imageUrl` (string, required): Source URL for card image.
- `linkUrl` (string, required): Redirect hyperlink URL.
- `title` (string, required): Title text used for caption and tooltips.
- `id` (string, required): Unique DOM identifier.
- `width` (string, default: `'160px'`): Default card container width.
- `aspectRatio` (string, default: `'square'`): Aspect ratio preset (`'square' | 'video' | 'portrait' | 'auto'`).
- `imageFit` (string, default: `'cover'`): Sizing constraints (`'cover' | 'contain'`).
- `showTitle` (boolean, default: `true`): Renders bottom title block.

### Veneer Spec Inline Child Syntax
Veneer Spec supports mapping a `child` list directly to instances of a React component by using `child <name> -> <Component> { ... }`.

```vnr
child items -> UiImageCard {
    selector: ".thumb-box";
    aspectRatio: "portrait";
    imageFit: "contain";
    showTitle: true;

    bind imageUrl: "img | attr:src";
    bind linkUrl: "a | attr:href";
    bind title: "h3 | text";
    bind id: "self | attr:data-id";
}
```

---

# React component specifications: UiImageViewer
## User
What is the purpose of `UiImageViewer` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiImageViewer` renders a full-container responsive image viewer, centered within parent bounds.

### Properties (Props API)
- `src` (string): Image source URL.
- `alt` (string, default: `''`): Alt text layout.
- `fit` (string, default: `'contain'`): CSS object fit constraints (`'contain' | 'cover'`).
- `background` (string, default: `'var(--spm-bg-primary)'`): Viewer fill color.

### Veneer Spec Inline Child Example
```vnr
child imageSlot -> UiImageViewer {
    selector: "#large-preview img";
    fit: "contain";

    bind src: "self | attr:src";
    bind alt: "self | attr:alt";
}
```

---

# React component specifications: UiTable
## User
What is the purpose of `UiTable` and what properties does it accept in Veneer Spec?
## Assistant
`UiTable` renders a styled tabular grid.

### Properties (Props API)
- `columns` (ColumnConfig[], required): Column config schema array.
- `data` (any[], required): Row data array.

### Veneer Spec Example
```vnr
child tableRows -> UiTable {
    columns: R"([
      { "key": "id", "header": "ID", "width": "60px", "align": "center" },
      { "key": "title", "header": "Title", "align": "left" }
    ])";
}
```

---

# React component specifications: UiToastContainer
## User
What is the purpose of `UiToastContainer` and what properties does it accept in Veneer Spec?
## Assistant
`UiToastContainer` manages global toast notifications stack and portal overlay.

### Properties (Props API)
- `position` (string, default: `'bottom-right'`): Screen corner positioning (`'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'`).

### Veneer Spec Example
```vnr
reconstruct "#global-toast-portal" -> UiToastContainer {
    position: "bottom-right";
}
```

---

# React component specifications: UiScrollPanel
## User
What is the purpose of `UiScrollPanel` and what properties does it accept in Veneer Spec?
## Assistant
`UiScrollPanel` is a scrollable sidebar panel that hosts tags list, action buttons, search bar and statistics box.

### Properties (Props API)
- `tags` (TagItem[]): Tags list array (`{ name, count, type, url }`).
- `buttons` (ButtonItem[]): Buttons list array (`{ label, url }`).
- `statisticsHtml` (string): Raw HTML string containing metadata.
- `showSearch` (boolean, default: `false`): Toggles rendering of `UiSearchBar`.
- `searchSubmitUrl` (string): Redirect submit URL.
- `searchParamName` (string, default: `'q'`): Query string parameter key.
- `width` (string, default: `'280px'`): Width of scroll panel.

### Veneer Spec Example
```vnr
reconstruct "#sidebar" -> UiScrollPanel {
    width: "300px";
    showSearch: true;
    searchSubmitUrl: "/posts";
    searchParamName: "tags";

    bind statisticsHtml: "#stats-box | html";

    child tags {
        selector: "li.tag";
        bind name: "a.tag-name | text";
        bind count: "span.tag-count | text";
        bind type: "self | attr:class";
        bind url: "a.tag-name | attr:href";
    }
}
```

---

# React component specifications: UiSplitLayout
## User
What is the purpose of `UiSplitLayout` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiSplitLayout` is a split two-column layout shell pairing a main media viewport (with `UiImageViewer` or `mainHtml` content) and a sidebar `UiScrollPanel`.

### Properties (Props API)
- `sidebarWidth` (string, default: `'280px'`): Sidebar column width.
- `sidebarSide` (string, default: `'left'`): Sidebar alignment (`'left' | 'right'`).
- `imageFit` (string, default: `'contain'`): Object fit passed to image viewer.
- `height` (string, default: `'100vh'`): Layout height.
- `showSearch` (boolean, default: `false`): Toggles search bar.
- `searchPlaceholder` (string): Search placeholder string.
- `searchSubmitUrl` (string): Search submission link.
- `searchParamName` (string, default: `'q'`): Search param name.
- `mainHtml` (string): Custom HTML string to render in main pane if no image is present.

### Nested Child Blocks
- `child imageSlot`: Renders viewer images (`{ src, alt }`).
- `child tags`: Sidebar tag list.
- `child buttons`: Sidebar action buttons links.

### Veneer Spec Example
```vnr
reconstruct "#post-view" -> UiSplitLayout {
    sidebarWidth: "300px";
    sidebarSide: "left";
    showSearch: true;
    searchSubmitUrl: "/posts";
    searchParamName: "tags";

    child imageSlot {
        selector: "#image";
        bind src: "self | attr:src";
        bind alt: "self | attr:alt";
    }

    child tags {
        selector: "#tag-sidebar li";
        bind name: "a | text";
        bind count: "span | text";
        bind type: "self | attr:class";
        bind url: "a | attr:href";
    }
}
```

---

# React component specifications: UiHeroLanding
## User
What is the purpose of `UiHeroLanding` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiHeroLanding` is a full-viewport homepage landing hero component with brand logo, subtitle, search field, and navigation links.

### Properties (Props API)
- `siteName` (string, default: `'Site'`): Fallback title.
- `logoUrl` (string): Image logo link.
- `logoHref` (string, default: `'/'`): Redirect link on click.
- `tagline` (string): Large headline string.
- `subtext` (string): Subtitle paragraph.
- `ctaLabel` (string, default: `'Browse'`): CTA button label.
- `ctaUrl` (string, default: `'/'`): CTA target destination.
- `searchSubmitUrl` (string): If set, renders a search bar input.
- `searchParamName` (string, default: `'q'`): Search field parameter.

### Nested Child Blocks
- `child primaryLinks`: Pill nav links below CTA (`{ label, url }`).

### Veneer Spec Example
```vnr
reconstruct "#landing-hero" -> UiHeroLanding {
    siteName: "Safe Gallery";
    tagline: "Unsloth Powered Generation";
    ctaLabel: "Enter Gallery";
    ctaUrl: "/posts";
    searchSubmitUrl: "/posts";
    searchParamName: "tags";
}
```

---

# React component specifications: UiTagBadge
## User
What is the purpose of `UiTagBadge` and what properties does it accept in Veneer Spec?
## Assistant
`UiTagBadge` renders inline pill badges for tags and categories.

### Properties (Props API)
- `label` (string, required): Text content.
- `count` (number, optional): Optional count suffix.
- `href` (string, optional): Redirection route when clicked.

### Veneer Spec Example
```vnr
selector ".tag-badge" -> UiTagBadge {
    action: replace;
    bind label: "self | text";
    bind count: "span.count | text | number";
    bind href: "a | attr:href";
}
```

---

# React component specifications: UiPaginationBar
## User
What is the purpose of `UiPaginationBar` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiPaginationBar` displays list page pagination buttons.

### Properties (Props API)
- `paramName` (string, default: `'page'`): Parameter name key in URL.

### Nested Child Blocks
- `child pageLinks`: Pagination pages array (`{ label, url }`).

### Veneer Spec Example
```vnr
reconstruct "#results-pager" -> UiPaginationBar {
    paramName: "page";
    
    child pageLinks {
        selector: "a.page-link";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

---

# React component specifications: UiModernGridPage
## User
What is the purpose of `UiModernGridPage` and what properties and nested child bindings does it accept in Veneer Spec?
## Assistant
`UiModernGridPage` is a visual layout component rendering cards in a responsive grid.

### Properties (Props API)
- `pageTitle` (string, default: `'Gallery'`): Main title heading.

### Nested Child Blocks
- `child items`: Renders modern grid card items. Follows the `UiImageCard` property API (`imageUrl`, `linkUrl`, `title`, `id`, `width`, `aspectRatio`, `imageFit`, `showTitle`).
- `child pageLinks`: Navigation pages links array (`{ label, url }`).

### Veneer Spec Example
```vnr
reconstruct "#gallery" -> UiModernGridPage {
    pageTitle: "Wallpaper Board";

    child items -> UiImageCard {
        selector: ".thumbnail-container";
        width: "180px";
        aspectRatio: "square";
        
        bind imageUrl: "img | attr:src";
        bind linkUrl: "a | attr:href";
        bind title: "img | attr:alt";
        bind id: "self | attr:id";
    }
}
```

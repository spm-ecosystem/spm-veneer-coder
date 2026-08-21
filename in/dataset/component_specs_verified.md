# React component specification: UiNavHeader

## User
What is the purpose of `UiNavHeader` and what properties and nested child bindings does it accept?

## Assistant
`UiNavHeader` renders a responsive site header: a brand section (logo image or a fallback site-name string), a primary navigation row, a secondary utility-link row, and three layout variants. It also auto-highlights whichever link matches the current page URL.

### Properties (Props)
- `siteName` (string, default `'Site'`): fallback text shown when no `logoUrl` is set.
- `logoUrl` (string, optional): logo image source.
- `logoHref` (string, default `'/'`): destination when the logo/site name is clicked.
- `primaryLinks` (`NavLink[]`, default `[]`): main nav entries.
- `secondaryLinks` (`NavLink[]`, default `[]`): secondary/utility nav entries.
- `layout` (`'standard' | 'stacked' | 'minimal'`, default `'standard'`): header layout variant.
- `hideOnMobile` (boolean, default `false`): hides the header below `mobileBreakpoint`.
- `mobileBreakpoint` (number, default `720`): pixel width threshold used by `hideOnMobile`.

### Nested Child Blocks
- `child primaryLinks` → `NavLink`: `label`, `url`.
- `child secondaryLinks` → `NavLink`: `label`, `url`.

---

# React component specification: UiHeroLanding

## User
What is the purpose of `UiHeroLanding` and what properties and nested child bindings does it accept?

## Assistant
`UiHeroLanding` is a full-viewport landing hero: brand header, tagline headline, subtext, a primary CTA button, an optional embedded search bar, and a row of quick-navigation link pills.

### Properties (Props)
- `siteName` (string, optional): fallback brand text when no `logoUrl` is set.
- `logoUrl` (string, optional): logo image source.
- `logoHref` (string, default `'/'`): logo click destination.
- `tagline` (string, optional): main headline.
- `subtext` (string, optional): subtitle text below the tagline.
- `ctaLabel` (string, optional): primary CTA button label.
- `ctaUrl` (string, optional): CTA destination URL.
- `searchPlaceholder` (string, optional): placeholder for the embedded search bar.
- `searchSubmitUrl` (string, optional): form action for the embedded search bar.
- `searchParamName` (string, optional): query parameter key for the embedded search field.
- `primaryLinks` (`NavLink[]`, default `[]`): pill nav links rendered below the CTA.

### Nested Child Blocks
- `child primaryLinks` → `NavLink`: `label`, `url`.

---

# React component specification: UiSearchBar

## User
What is the purpose of `UiSearchBar` and what properties and nested child bindings does it accept?

## Assistant
`UiSearchBar` is a standalone search input form. It supports native GET/POST browser submission, a configurable query parameter name, and forwarding of extra hidden form fields on submit. It can also be embedded inside `UiHeroLanding`, `UiModernGridPage`, and `UiScrollPanel`.

### Properties (Props)
- `placeholder` (string, default `'Search…'`).
- `defaultValue` (string, default `''`): initial input value.
- `submitUrl` (string, optional): form action target.
- `queryParamName` (string, default `'tags'`): the `name` attribute of the text input.
- `method` (`'get' | 'post' | 'GET' | 'POST'`, default `'GET'`).
- `hiddenFields` (`{ name: string; value: string }[]`, default `[]`): extra hidden inputs forwarded on submit.

### Nested Child Blocks
None — `UiSearchBar` is a leaf form component with no `child` list props.

---

# React component specification: UiImageCard

## User
What is the purpose of `UiImageCard` and what properties and nested child bindings does it accept?

## Assistant
`UiImageCard` is a single thumbnail card: an image, an optional bottom title caption, and a wrapping link. It supports four aspect ratios and two object-fit modes, and is most often mounted once per row via an inline `child items -> UiImageCard { ... }` block rather than nested inside another component.

### Properties (Props)
- `imageUrl` (string, required): thumbnail source.
- `linkUrl` (string, required): click destination.
- `title` (string, required): caption/tooltip text.
- `id` (string, required): unique DOM id for the card.
- `width` (string, default `'160px'`).
- `aspectRatio` (`'square' | 'video' | 'portrait' | 'auto'`, default `'square'`).
- `imageFit` (`'cover' | 'contain'`, default `'cover'`).
- `showTitle` (boolean, default `true`): toggles the bottom caption block.

### Nested Child Blocks
None — used as a per-item card, not as a container with its own `child` lists.

---

# React component specification: UiTagBadge

## User
What is the purpose of `UiTagBadge` and what properties and nested child bindings does it accept?

## Assistant
`UiTagBadge` is a single tag/category pill: a label, an optional item-count suffix, a primary link, and two optional inline action links for adding or excluding the tag from the current search (rendered as `+`/`-` buttons).

### Properties (Props)
- `label` (string, required).
- `count` (string or number, optional).
- `href` (string, optional): primary navigation link.
- `addUrl` (string, optional): powers the `+` action button.
- `removeUrl` (string, optional): powers the `-` action button.

### Nested Child Blocks
None — a single pill, not a list container.

---

# React component specification: UiPaginationBar

## User
What is the purpose of `UiPaginationBar` and what properties and nested child bindings does it accept?

## Assistant
`UiPaginationBar` renders Previous/Next and numbered page links, deriving the current/active page from a query parameter it reads off each link's URL.

### Properties (Props)
- `pageLinks` (`PageLink[]`, default `[]`).
- `paramName` (string, default `'pid'`): query parameter key used to detect page offset and active state.

### Nested Child Blocks
- `child pageLinks` → `PageLink`: `label`, `url`.

---

# React component specification: UiModernGridPage

## User
What is the purpose of `UiModernGridPage` and what properties and nested child bindings does it accept?

## Assistant
`UiModernGridPage` is a full gallery page: a responsive `UiImageCard` grid, a sidebar that can render grouped tag lists or a raw HTML fallback, an optional embedded search bar, and bottom pagination. It has dedicated mobile-responsive props for column count, gap, and sidebar visibility.

### Properties (Props)
- `pageTitle` (string, required).
- `items` (`GridItem[]`, required): `imageUrl`, `linkUrl`, `title`, `id`.
- `pageLinks` (`PageLink[]`, default `[]`).
- `sidebarHtml` (string, optional): raw HTML sidebar fallback.
- `tags` (`TagItem[]`, default `[]`): flat tag list rendered in the sidebar.
- `tagGroups` (`{ title: string; typeKey: string }[]`, default `[]`): groups the flat `tags` list into labeled sections by matching each tag's `type` against `typeKey`.
- `showSearch` (boolean, default `false`).
- `searchPlaceholder`, `searchSubmitUrl` (string, optional).
- `searchParamName` (string, default `'tags'`).
- `searchDefaultValue` (string, default `''`).
- `height` (string, default `'100vh'`).
- `sidebarWidth` (string, default `'280px'`).
- `hideSidebarOnMobile` (boolean, default `true`).
- `mobileBreakpoint` (number, default `720`).
- `mobileColumns` (number, default `2`).
- `mobileGap` (string, default `'8px'`).

### Nested Child Blocks
- `child items` → `GridItem`: `imageUrl`, `linkUrl`, `title`, `id`.
- `child pageLinks` → `PageLink`: `label`, `url`.
- `child tags` → `TagItem`: fields matching `tagGroups[].typeKey` values.

---

# React component specification: UiImageViewer

## User
What is the purpose of `UiImageViewer` and what properties and nested child bindings does it accept?

## Assistant
`UiImageViewer` fills its container with a single responsive image. It is most often used implicitly through `UiSplitLayout`'s `imageSlot`, but can also be reconstructed directly for standalone image-post pages.

### Properties (Props)
- `src` (string, required).
- `alt` (string, default `''`).
- `fit` (`'contain' | 'cover'`, default `'contain'`): CSS `object-fit`.
- `background` (string, default `var(--spm-bg-primary)`): container background when the image doesn't fill the frame.

### Nested Child Blocks
None.

---

# React component specification: UiScrollPanel

## User
What is the purpose of `UiScrollPanel` and what properties and nested child bindings does it accept?

## Assistant
`UiScrollPanel` is a scrollable sidebar: an optional embedded search bar, a tag list, a list of action buttons that are auto-classified by label wording, and a raw-HTML statistics block.

### Properties (Props)
- `tags` (`TagItem[]`, default `[]`): `name`, `count`, `type`, `url`.
- `buttons` (`ButtonItem[]`, default `[]`): `label`, `url`, `targetSelector` — auto-classified into primary/nav/ghost styles by label keywords.
- `statisticsHtml` (string, optional): raw HTML block.
- `showSearch` (boolean, default `false`).
- `searchPlaceholder`, `searchSubmitUrl` (string, optional).
- `searchParamName` (string, default `'q'`).
- `width` (string, default `'280px'`).
- `onClose` (function, optional): called when the panel's close button is clicked.

### Nested Child Blocks
- `child tags` → `TagItem`: `name`, `count`, `type`, `url`.
- `child buttons` → `ButtonItem`: `label`, `url`, `targetSelector`.

---

# React component specification: UiSplitLayout

## User
What is the purpose of `UiSplitLayout` and what properties and nested child bindings does it accept?

## Assistant
`UiSplitLayout` is a two-column detail-view shell. The main column renders either an image (via `imageSlot`, internally using `UiImageViewer`) or arbitrary HTML (`mainHtml`); the second column is a `UiScrollPanel` receiving the forwarded `tags`, `buttons`, `statisticsHtml`, and search props.

### Properties (Props)
- `imageSlot` (`{ src, alt }[]`, default `[]`): first item renders via `UiImageViewer`.
- `tags`, `buttons`, `statisticsHtml`: forwarded to the internal `UiScrollPanel`.
- `sidebarWidth` (string, default `'280px'`).
- `sidebarSide` (`'left' | 'right'`, default `'left'`).
- `imageFit` (`'contain' | 'cover'`, default `'contain'`).
- `height` (string, default `'100vh'`).
- `splitButtons` (boolean, default `false`).
- `showSearch`, `searchPlaceholder`, `searchSubmitUrl` (forwarded to sidebar search).
- `searchParamName` (string, default `'q'`).
- `mainHtml` (string, optional): used only when `imageSlot` is empty.

### Nested Child Blocks
- `child imageSlot`: `src`, `alt`.
- `child tags` → `TagItem`: `name`, `count`, `type`, `url`.
- `child buttons` → `ButtonItem`: `label`, `url`, `targetSelector`.

---

# React component specification: UiCommentListPage

## User
What is the purpose of `UiCommentListPage` and what properties and nested child bindings does it accept?

## Assistant
`UiCommentListPage` modernizes comment feeds and message boards: a list of post/thread cards (thumbnail, author, date, rating, score), each with its own tag badges and a nested list of speech-bubble replies, plus bottom pagination.

### Properties (Props)
- `pageTitle` (string, default `'Comments'`).
- `threads` (`CommentThread[]`, default `[]`).
- `pageLinks` (`PageLink[]`, default `[]`).
- `height` (string, default `'100vh'`).

### `CommentThread` fields
`id`, `thumbnailUrl`, `postUrl`, `postDate`, `postUser`, `postRating`, `postScore`, plus two optional nested lists: `tags` (`{ label, url, type }[]`) and `comments` (`{ author, authorUrl, date, body }[]`).

### Nested Child Blocks
- `child threads` → `CommentThread` fields above.
  - `child tags` (nested inside each thread): `label`, `url`, `type`.
  - `child comments` (nested inside each thread): `author`, `authorUrl`, `date`, `body`.
- `child pageLinks` → `PageLink`: `label`, `url`.

---

# React component specification: UiDashboardPage

## User
What is the purpose of `UiDashboardPage` and what properties and nested child bindings does it accept?

## Assistant
`UiDashboardPage` is a card-grid layout for account control panels, settings hubs, and admin option menus: a header with title/subtitle, and a responsive grid of action cards.

### Properties (Props)
- `pageTitle` (string, default `'Dashboard'`).
- `subTitle` (string, optional).
- `cards` (`DashboardCard[]`, default `[]`).
- `height` (string, default `'100vh'`).

### `DashboardCard` fields
`title` (required), `description` (optional), `url` (required), `urlLabel` (optional, defaults to `'Open'` on the rendered button).

### Nested Child Blocks
- `child cards` → `DashboardCard`: `title`, `description`, `url`, `urlLabel`.

---

# React component specification: UiStatsDashboard

## User
What is the purpose of `UiStatsDashboard` and what properties and nested child bindings does it accept?

## Assistant
`UiStatsDashboard` is a metrics/leaderboard layout: a timeframe badge, a row of navigation links, and one or more ranked section cards (e.g. top tags, most active users).

### Properties (Props)
- `pageTitle` (string, default `'Statistics'`).
- `dateRangeText` (string, default `'All time'`).
- `navLinks` (`NavLink[]`, default `[]`).
- `sections` (`StatSection[]`, default `[]`).
- `height` (string, default `'100vh'`).

### `StatSection` / `StatItem` fields
`StatSection`: `title`, `items` (`StatItem[]`). `StatItem`: `place` (optional), `amount`, `name`, `profileUrl` (optional).

### Nested Child Blocks
- `child navLinks` → `NavLink`: `label`, `url`.
- `child sections` → `StatSection`: `title`.
  - `child items` (nested inside each section): `place`, `amount`, `name`, `profileUrl`.

---

# React component specification: UiTable

## User
What is the purpose of `UiTable` and what properties and nested child bindings does it accept?

## Assistant
`UiTable` is a generic, standalone tabular grid: a `columns` configuration array, a `data` row array, and an optional row-click callback. It has no page chrome (no title, no pagination) — that's what `UiTableListPage` wraps it with. It is normally mounted inline as a `child <name> -> UiTable { ... }` block rather than as a top-level `reconstruct` target, since `data` is populated from the same scraped rows the `child` list produces.

### Properties (Props)
- `columns` (`ColumnConfig<T>[]`, required): `key`, `header`, `width` (optional), `align` (optional, `'left' | 'center' | 'right'`), `render` (optional custom cell renderer).
- `data` (`T[]`, required).
- `onRowClick` (function, optional).

### Nested Child Blocks
None directly — when mounted via `child <name> -> UiTable { ... }`, the enclosing `child`'s own `selector`/`bind` lines populate `data`.

---

# React component specification: UiTableListPage

## User
What is the purpose of `UiTableListPage` and what properties and nested child bindings does it accept?

## Assistant
`UiTableListPage` is a complete tabular list page: it wraps `UiTable` with a page-title header, per-column cell-type formatting (plain text, links, raw HTML, badges, checkboxes, dates, currency), optional infinite-scroll loading, and bottom pagination.

### Properties (Props)
- `pageTitle` (string, default `'List'`).
- `tableRows` (array, default `[]`).
- `columns` (`TableColumnConfig[]`, optional).
- `pageLinks` (`PageLink[]`, default `[]`).
- `height` (string, default `'100vh'`).
- `onLoadMore` (`() => Promise<{ tableRows, hasMore }>`, optional): infinite-scroll trigger.

### `TableColumnConfig` fields
`key`, `header`, `width` (optional), `align` (optional), `type` (optional: `'text' | 'link' | 'html' | 'badge' | 'checkbox' | 'date' | 'currency'`), `urlKey` (used when `type` is `'link'`), `badgeStyleKey` (used when `type` is `'badge'`).

### Nested Child Blocks
- `child tableRows`: arbitrary `bind` fields matching the row's `key`s in `columns`.
- `child pageLinks` → `PageLink`: `label`, `url`.

---

# React component specification: UiToastContainer

## User
What is the purpose of `UiToastContainer` and what properties and nested child bindings does it accept?

## Assistant
`UiToastContainer` is a global feedback portal: it stacks animated toast notifications (four variants — `info`, `warning`, `success`, `error`) and listens for confirmation-modal portal events above the rest of the Shadow DOM UI. It is normally mounted once per page with a wildcard `urlPattern` and takes almost no configuration.

### Properties (Props)
- `position` (`'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'`, default `'bottom-right'`).

### `UiToast` item fields (managed internally, not authored in `.vnr`)
`message` (required), `type` (default `'info'`), `onClose` (required).

### Nested Child Blocks
None — `UiToastContainer` takes no scraped `bind`/`child` data; it's a passive global listener.

---

# React component specification: Layout Primitives

## User
What are the Layout Primitives in spm-components, and what does each one render as?

## Assistant
Layout Primitives are lightweight, generic building blocks (as opposed to the pre-styled Dedicated Components above) used to structure content inside a reconstruct without introducing their own visual design.

- `UiBox` → `<div>`: generic wrapper for padding, background, and borders.
- `UiFlexRow` → `<div>` (flex row): horizontal alignment container.
- `UiFlexColumn` → `<div>` (flex column): vertical stacking container.
- `UiGrid` → `<div>` (CSS grid): multi-column grid container.
- `UiText` → `<span>`: renders a `content` prop as styled text.
- `UiImage` → `<img>`: takes `src` and `alt`.
- `UiLink` → `<a>`: takes `href`.
- `UiScrollBox`: a scrollable box wrapper, used for arbitrary overflow content (distinct from `UiScrollPanel`, which is a fully dedicated, pre-styled sidebar component).

`UiBox`, `UiFlexRow`, `UiFlexColumn`, and `UiGrid` all accept standard HTML `<div>` props (`className`, `style`, `children`, etc.) — they carry no dedicated business props of their own.

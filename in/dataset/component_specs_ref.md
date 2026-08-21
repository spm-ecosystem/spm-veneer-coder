# React component specifications: UiCommentListPage
## User
What is the purpose of `UiCommentListPage` and what properties and nested child bindings does it accept?
## Assistant
`UiCommentListPage` is used to modernize comment sections, discussion boards, or thread directories.

### Properties (Props)
- `pageTitle` (string, default: `'Comments'`): Header text.
- `height` (string, default: `'100vh'`): Layout height constraint.

### Nested Child Blocks
- `child threads`: Renders the thread items. Expected fields on each item:
  - `id` (string): Thread ID.
  - `thumbnailUrl` (string): Post image preview link.
  - `postUrl` (string): Link to the original thread page.
  - `postDate` (string): Post timestamp/date string.
  - `postUser` (string): Creator username.
  - `postRating` (string): Safety rating descriptor (e.g., `'Safe'`).
  - `postScore` (string): Votes or rating score.
  - `child tags` (nested): List of badge tags on each thread (`label`, `url`, `type`).
  - `child comments` (nested): List of replies (`author`, `authorUrl`, `date`, `body`).
- `child pageLinks`: Pagination buttons list (`label`, `url`).

---

# React component specifications: UiDashboardPage
## User
What is the purpose of `UiDashboardPage` and what properties and nested child bindings does it accept?
## Assistant
`UiDashboardPage` renders an administrative control panel or user overview dashboard displaying stats and activity logs.

### Properties (Props)
- `pageTitle` (string, default: `'Dashboard'`): Header text.
- `height` (string, default: `'100vh'`): Wrapper height constraint.

### Nested Child Blocks
- `child metrics`: Renders cards containing key stats. Expected item fields:
  - `label` (string): Name of the metric (e.g., `'Revenue'`).
  - `value` (string or number): Calculated value or stat text.
- `child recentActivity`: Renders log items. Expected item fields:
  - `actor` (string): User executing the action.
  - `action` (string): Description of the logged action.
  - `timestamp` (string): Log datetime string.

---

# React component specifications: UiHeroLanding
## User
What is the purpose of `UiHeroLanding` and what properties and nested child bindings does it accept?
## Assistant
`UiHeroLanding` modernizes homepage landing sections and splash screens with large typography and call-to-actions.

### Properties (Props)
- `tagline` (string): Large title heading.
- `subtext` (string): Explanatory subtitle paragraph.
- `ctaLabel` (string): Button text for the main CTA link.
- `ctaUrl` (string): Destination link for the main CTA.

### Nested Child Blocks
- `child primaryLinks`: Array of auxiliary navigation items. Expected item fields:
  - `label` (string): Link text.
  - `url` (string): Link destination.

---

# React component specifications: UiImageCard
## User
What is the purpose of `UiImageCard` and what properties and nested child bindings does it accept?
## Assistant
`UiImageCard` renders a visual media card containing an image, category metadata, caption text, and an action link.

### Properties (Props)
- `imageUrl` (string): Source link of the image.
- `caption` (string): Headline overlay text.
- `category` (string, optional): Small category tag.
- `linkUrl` (string, optional): Target destination link.
- `aspectRatio` (string, default: `'1:1'`): Desired aspect ratio.
- `loading` (string, default: `'lazy'`): Image loading strategy (`'lazy'` or `'eager'`).

---

# React component specifications: UiImageViewer
## User
What is the purpose of `UiImageViewer` and what properties and nested child bindings does it accept?
## Assistant
`UiImageViewer` modernizes individual image post views, illustration cards, and image-sharing detail sections.

### Properties (Props)
- `imageSrc` (string): Direct URL of the large image.
- `title` (string, optional): Heading of the post.
- `description` (string, optional): Caption or detail paragraph.

---

# React component specifications: UiModernGridPage
## User
What is the purpose of `UiModernGridPage` and what properties and nested child bindings does it accept?
## Assistant
`UiModernGridPage` displays visual galleries, portfolio feeds, or image-board catalog grids.

### Properties (Props)
- `pageTitle` (string, default: `'Gallery'`): Main heading text.
- `showSearch` (boolean, default: `true`): Renders a search input.
- `searchPlaceholder` (string): Input field placeholder text.
- `searchSubmitUrl` (string): Search form action URL.
- `searchParamName` (string, default: `'q'`): Query query-string key name.
- `mobileColumns` (number, default: `2`): Grid column count on narrow viewports.

### Nested Child Blocks
- `child items`: Array of visual grid items. Follows the `UiImageCard` schema (`imageUrl`, `caption`, `category`, `linkUrl`).
- `child pageLinks`: Pagination buttons list (`label`, `url`).

---

# React component specifications: UiNavHeader
## User
What is the purpose of `UiNavHeader` and what properties and nested child bindings does it accept?
## Assistant
`UiNavHeader` replaces legacy headers with a responsive, sticky navigation bar.

### Properties (Props)
- `logoUrl` (string): Header brand image source.
- `logoHref` (string): Brand link destination.
- `sticky` (boolean, default: `false`): Enables sticky positioning at viewport top.

### Nested Child Blocks
- `child primaryLinks`: Array of navigation items. Expected item fields:
  - `label` (string): Text label.
  - `url` (string): Destination path.

---

# React component specifications: UiPaginationBar
## User
What is the purpose of `UiPaginationBar` and what properties and nested child bindings does it accept?
## Assistant
`UiPaginationBar` renders standard bottom navigation pages bars.

### Properties (Props)
- `pageTitle` (string, optional): Heading label.

### Nested Child Blocks
- `child pages`: Page numbers list. Expected item fields:
  - `label` (string): Page label (e.g., `'1'`, `'Next'`).
  - `url` (string): Pager target URL.

---

# React component specifications: UiScrollPanel
## User
What is the purpose of `UiScrollPanel` and what properties and nested child bindings does it accept?
## Assistant
`UiScrollPanel` encapsulates overflow content into a scrollable viewport panel.

### Properties (Props)
- `height` (string, default: `'100%'`): Height constraint.

### Nested Child Blocks
- `child entries`: Content elements list. Expected item fields:
  - `version` (string): Title/label tag.
  - `description` (string): Description copy.

---

# React component specifications: UiSearchBar
## User
What is the purpose of `UiSearchBar` and what properties and nested child bindings does it accept?
## Assistant
`UiSearchBar` renders a standalone header search form.

### Properties (Props)
- `placeholder` (string): Input field placeholder text.
- `submitUrl` (string): Form submit endpoint.
- `queryParamName` (string, default: `'q'`): Query query-string key name.

---

# React component specifications: UiSplitLayout
## User
What is the purpose of `UiSplitLayout` and what properties and nested child bindings does it accept?
## Assistant
`UiSplitLayout` renders split two-column content layouts (e.g., main column + sidebar).

### Properties (Props)
- `pageTitle` (string, optional): Page heading.
- `headline` (string, optional): Main text title.
- `bodyHtml` (string, optional): Main column content.

### Nested Child Blocks
- `preserve` block (optional): Slot mappings to keep legacy widgets alive.

---

# React component specifications: UiStatsDashboard
## User
What is the purpose of `UiStatsDashboard` and what properties and nested child bindings does it accept?
## Assistant
`UiStatsDashboard` displays key system performance metrics, transaction records, or sales metrics.

### Properties (Props)
- `pageTitle` (string, default: `'Analytics'`): Main heading label.

### Nested Child Blocks
- `child metrics`: Array of stats. Expected item fields:
  - `label` (string): Metric title (e.g., `'MRR'`).
  - `value` (string or number): Evaluated value string.

---

# React component specifications: UiTableListPage
## User
What is the purpose of `UiTableListPage` and what properties and nested child bindings does it accept?
## Assistant
`UiTableListPage` renders list items into a tabular format, e.g. for user directories, transaction sheets, or audit logs.

### Properties (Props)
- `pageTitle` (string, default: `'Directory'`): Header text.
- `showSearch` (boolean, default: `true`): Renders a search input.
- `searchPlaceholder` (string): Input field placeholder text.
- `searchSubmitUrl` (string): Search form action URL.
- `searchParamName` (string, default: `'q'`): Query query-string key name.

### Nested Child Blocks
- `child tableRows`: Renders table items. Expected item fields:
  - `title` (string): Row item title.
  - `url` (string): Row detail target link.
  - `imageUrl` (string, optional): Item thumbnail source.
  - `price` (number, optional): Formatted item price.
  - `status` (string, optional): Badged status descriptor.
  - `lastSeen` (string, optional): Activity time text.
- `child pageLinks`: Pagination buttons list (`label`, `url`).

---

# React component specifications: UiTagBadge
## User
What is the purpose of `UiTagBadge` and what properties and nested child bindings does it accept?
## Assistant
`UiTagBadge` renders inline badges indicating categories, status, or types.

### Properties (Props)
- `label` (string): Badge visible text.
- `status` (string, optional): Type modifier (e.g., `'success'`, `'danger'`).
- `url` (string, optional): Redirect destination on-click.

# Replacing a promo image block with UiImageCard
## User
Write a `.vnr` selector block that replaces this featured media block with `UiImageCard`:

```html
<div class="featured-media-block" data-media-id="778">
  <img class="featured-img" src="/media/778-large.jpg" alt="Autumn Collection" />
  <p class="media-caption">New Autumn Collection</p>
  <a class="view-details" href="/gallery/autumn">View Details</a>
</div>
```
## Assistant
Here is the Veneer Spec code to replace the featured media block in place with `UiImageCard`:

```vnr
selector ".featured-media-block" -> UiImageCard {
    action: replace;
    width: "360px";
    aspectRatio: "video";
    showTitle: true;
    
    bind imageUrl: "img.featured-img | attr:src";
    bind linkUrl: "a.view-details | attr:href";
    bind title: "p.media-caption | text";
    bind id: "self | attr:data-media-id";
}
```

---

# Reconstructing an admin overview into UiDashboardPage
## User
Map this support overview HTML into a `UiDashboardPage` containing modern action cards:

```html
<div id="admin-overview">
  <div class="admin-option-card">
    <h3>System Configuration</h3>
    <p class="desc">Adjust site variables and settings...</p>
    <a href="/admin/config">Edit Config</a>
  </div>
  <div class="admin-option-card">
    <h3>User Moderation</h3>
    <p class="desc">Ban, flag, or approve registrations...</p>
    <a href="/admin/users">Moderate</a>
  </div>
</div>
```
## Assistant
Here is the Veneer Spec code to reconstruct the overview into `UiDashboardPage`, mapping the option containers using the `cards` child block:

```vnr
reconstruct "#admin-overview" -> UiDashboardPage {
    pageTitle: "Support Overview";
    subTitle: "Select an option below to manage settings and moderation.";
    height: "100vh";
    
    child cards {
        selector: ".admin-option-card";
        bind title: "h3 | text";
        bind description: "p.desc | text";
        bind url: "a | attr:href";
        bind urlLabel: "a | text";
    }
}
```

---

# Reconstructing a two-column layout with UiSplitLayout
## User
This article page has a main column and a legacy links sidebar widget I need to keep. Map it to `UiSplitLayout`:

```html
<div id="article-layout">
  <div class="main-column">
    <h1 class="headline">Understanding Client-Side Layout Overrides</h1>
    <div class="body-copy">Full article content goes here...</div>
  </div>
  <aside id="legacy-related-links-widget">
    <h3>Related Links</h3>
    <a href="/related-1">First Link</a>
    <a href="/related-2">Second Link</a>
  </aside>
</div>
```
## Assistant
Here is the Veneer Spec code to reconstruct the two-column layout using `UiSplitLayout`. We bind the main content to `mainHtml` and extract the sidebar links into the `buttons` child block:

```vnr
reconstruct "#article-layout" -> UiSplitLayout {
    sidebarWidth: "300px";
    sidebarSide: "right";
    
    bind mainHtml: ".main-column | html";
    
    child buttons {
        selector: "#legacy-related-links-widget a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

---

# Replacing a legacy changelog list with UiCommentListPage
## User
Write a `.vnr` selector block that replaces this changelog list with `UiCommentListPage`:

```html
<div class="changelog-box" id="release-notes-list">
  <div class="changelog-entry" id="v240">
    <span class="version-tag">v2.4.0</span>
    <span class="author">admin</span>
    <p class="entry-text">Added dark mode support.</p>
  </div>
  <div class="changelog-entry" id="v231">
    <span class="version-tag">v2.3.1</span>
    <span class="author">dev</span>
    <p class="entry-text">Fixed pagination bug on mobile.</p>
  </div>
</div>
```
## Assistant
Here is the Veneer Spec code to replace the changelog box with `UiCommentListPage`, mapping each release note entry to a comment thread object:

```vnr
reconstruct "#release-notes-list" -> UiCommentListPage {
    pageTitle: "Release Notes";
    height: "calc(100vh - 80px)";
    
    child threads {
        selector: ".changelog-entry";
        bind id: "self | attr:id";
        bind postDate: "span.version-tag | text";
        bind postUser: "span.author | text";
        
        child comments {
            selector: "p.entry-text";
            bind body: "self | text";
        }
    }
}
```

---

# Replacing an inline status label with UiTagBadge
## User
Write a `.vnr` selector block that swaps this order status flag for `UiTagBadge`:

```html
<span class="order-status-flag" data-count="15" data-url="/orders/shipped">Shipped</span>
```
## Assistant
Here is the Veneer Spec code to replace the status flag in place with `UiTagBadge`:

```vnr
selector ".order-status-flag" -> UiTagBadge {
    action: replace;
    bind label: "self | text";
    bind count: "self | attr:data-count | number";
    bind href: "self | attr:data-url";
}
```

---

# Reconstructing a landing page into UiHeroLanding
## User
Map this homepage hero section, including its nav links, into `UiHeroLanding`:

```html
<section id="homepage-hero">
  <h1 class="hero-heading">Build Faster, Ship Sooner</h1>
  <p class="hero-subtext">The toolkit for modern engineering teams.</p>
  <a class="hero-cta" href="/signup">Get Started</a>
  <nav class="hero-nav">
    <a class="hero-nav-link" href="/features">Features</a>
    <a class="hero-nav-link" href="/pricing">Pricing</a>
  </nav>
</section>
```
## Assistant
Here is the Veneer Spec code to reconstruct the hero section into `UiHeroLanding`, using a small reusable class for the nav links:

```vnr
class HeroNavLink {
    bind label: "self | text";
    bind url: "self | attr:href";
}

reconstruct "#homepage-hero" -> UiHeroLanding {
    siteName: "Landing Page";
    tagline: "Build Faster, Ship Sooner";
    subtext: "The toolkit for modern engineering teams.";
    ctaLabel: "Get Started";
    ctaUrl: "https://example.com/signup";
    
    child primaryLinks extends HeroNavLink {
        selector: "a.hero-nav-link";
    }
}
```

---

# Mapping a details container using UiSplitLayout
## User
Reconstruct this book detail block into a `UiSplitLayout`, binding the title to `mainHtml` and details to `statisticsHtml`:

```html
<div id="book-listing">
  <h1 class="book-title">The Pragmatic Programmer</h1>
  <div class="book-condition">Condition: Like New</div>
  <form id="legacy-seller-contact-form" action="/contact-seller">
    <input type="submit" value="Contact Seller" />
  </form>
</div>
```
## Assistant
Here is the Veneer Spec code to reconstruct the container into `UiSplitLayout`, extracting the contact form into a sidebar button:

```vnr
reconstruct "#book-listing" -> UiSplitLayout {
    sidebarWidth: "320px";
    sidebarSide: "right";
    
    bind mainHtml: "h1.book-title | html";
    bind statisticsHtml: ".book-condition | text";
    
    child buttons {
        selector: "#legacy-seller-contact-form";
        bind label: "input[type='submit'] | attr:value";
        bind url: "self | attr:action";
    }
}
```

---

# Reconstructing forum navigation into UiPaginationBar with document scope
## User
The results and the pager live in separate containers on this forum page. Map the pager into `UiPaginationBar`, pulling its links from outside the results container:

```html
<div id="forum-results">
  <div class="topic-row">...</div>
</div>
<div id="global-forum-pager">
  <a class="pager-link" href="/forum?page=1">1</a>
  <a class="pager-link" href="/forum?page=2">2</a>
</div>
```
## Assistant
Since the pager sits outside the matched `#forum-results` container, use `scope: "document"` on the `child pageLinks` block so its selector queries the whole page instead of just the container's descendants:

```vnr
reconstruct "#forum-results" -> UiPaginationBar {
    paramName: "page";
    
    child pageLinks {
        scope: "document";
        selector: "#global-forum-pager a.pager-link";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

---

# Reconstructing a Q&A post page into UiCommentListPage
## User
Map this question-and-answers page into `UiCommentListPage`, with the answers as replies:

```html
<div id="question-detail" data-id="q-101">
  <h1 class="question-title">How do I debounce an input in React?</h1>
  <span class="author">Alice</span>
  <span class="date">2026-08-21</span>
  <div class="answer-row">
    <span class="answer-author">Bob</span>
    <span class="answer-date">2026-08-21</span>
    <div class="answer-body">Use a useEffect with a setTimeout cleanup.</div>
  </div>
</div>
```
## Assistant
Here is the Veneer Spec code to reconstruct the question page into `UiCommentListPage`, with the answers mapped as comment replies:

```vnr
reconstruct "#question-detail" -> UiCommentListPage {
    pageTitle: "Question Detail";
    
    child threads {
        selector: "self";
        bind id: "self | attr:data-id";
        bind postDate: "span.date | text";
        bind postUser: "span.author | text";
        
        child comments {
            selector: ".answer-row";
            bind author: "span.answer-author | text";
            bind date: "span.answer-date | text";
            bind body: ".answer-body | text";
        }
    }
}
```

---

# Reconstructing a metrics sidebar into UiStatsDashboard
## User
Map this revenue widget into `UiStatsDashboard`, setting up leaderboard sections:

```html
<aside id="revenue-widget">
  <h3>Financial Metrics</h3>
  <div class="metric-tile">
    <span class="metric-label">MRR</span>
    <span class="metric-value">$ 48,200.00</span>
  </div>
  <div class="metric-tile">
    <span class="metric-label">ARR</span>
    <span class="metric-value">$ 578,400.00</span>
  </div>
</aside>
```
## Assistant
Here is the Veneer Spec code to reconstruct the revenue widget into `UiStatsDashboard`, using the `sections` and nested `items` layout schema:

```vnr
reconstruct "#revenue-widget" -> UiStatsDashboard {
    pageTitle: "Financial Stats";
    dateRangeText: "This Month";
    
    child sections {
        selector: "self";
        bind title: "h3 | text";
        
        child items {
            selector: ".metric-tile";
            bind name: ".metric-label | text";
            bind amount: ".metric-value | text | cleanNumber";
        }
    }
}
```

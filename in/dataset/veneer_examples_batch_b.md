# Replacing a promo image block with UiImageCard
## User
Write a `.vnr` selector block that replaces this featured media block with `UiImageCard`:

```html
<div class="featured-media-block" data-media-id="778">
  <img class="featured-img" src="/media/778-large.jpg" alt="Autumn Collection" />
  <p class="media-caption">New Autumn Collection</p>
</div>
```
## Assistant
Here is the Veneer Spec code to replace the featured media block in place with `UiImageCard`:

```vnr
selector ".featured-media-block" -> UiImageCard {
    action: replace;
    bind imageUrl: "img.featured-img | attr:src";
    bind caption: "p.media-caption | text";
    bind mediaId: "self | attr:data-media-id | number";
}
```

# Reconstructing an admin overview into UiDashboardPage
## User
Map this support overview HTML into a `UiDashboardPage`, with metric tiles and a recent activity feed:

```html
<div id="admin-overview">
  <div class="metric-tile">
    <span class="metric-label">Open Tickets</span>
    <span class="metric-value">37</span>
  </div>
  <div class="metric-tile">
    <span class="metric-label">Avg Response Time</span>
    <span class="metric-value">2.4h</span>
  </div>
  <div class="activity-row">
    <span class="activity-actor">jsmith</span>
    <span class="activity-action">closed ticket #1042</span>
    <time class="activity-time" datetime="2026-08-21T09:15:00Z"></time>
  </div>
</div>
```
## Assistant
Here is the Veneer Spec code to reconstruct the overview into `UiDashboardPage`, using two separate `child` blocks for the metrics and the activity feed:

```vnr
reconstruct "#admin-overview" -> UiDashboardPage {
    pageTitle: "Support Overview";
    
    child metrics {
        selector: ".metric-tile";
        bind label: ".metric-label | text";
        bind value: ".metric-value | text";
    }
    
    child recentActivity {
        selector: ".activity-row";
        bind actor: ".activity-actor | text";
        bind action: ".activity-action | text";
        bind timestamp: ".activity-time | attr:datetime";
    }
}
```

# Reconstructing a two-column layout with UiSplitLayout
## User
This article page has a main column and a legacy sidebar widget I need to keep alive. Map it to `UiSplitLayout`:

```html
<div id="article-layout">
  <div class="main-column">
    <h1 class="headline">Understanding Client-Side Layout Overrides</h1>
    <div class="body-copy">Full article content goes here...</div>
  </div>
  <aside id="legacy-related-links-widget">
    <h3>Related Links</h3>
  </aside>
</div>
```
## Assistant
Here is the Veneer Spec code to reconstruct the two-column article layout into `UiSplitLayout`, preserving the legacy sidebar widget in its own slot:

```vnr
reconstruct "#article-layout" -> UiSplitLayout {
    pageTitle: "Article";
    
    bind headline: "h1.headline | text";
    bind bodyHtml: ".body-copy | html";
    
    preserve {
        relatedLinksSlot: "#legacy-related-links-widget";
    }
}
```

# Replacing a scrollable legacy list with UiScrollPanel
## User
Write a `.vnr` selector block that replaces this changelog list with `UiScrollPanel`:

```html
<div class="changelog-box" id="release-notes-list">
  <div class="changelog-entry">
    <span class="version-tag">v2.4.0</span>
    <p class="entry-text">Added dark mode support.</p>
  </div>
  <div class="changelog-entry">
    <span class="version-tag">v2.3.1</span>
    <p class="entry-text">Fixed pagination bug on mobile.</p>
  </div>
</div>
```
## Assistant
Here is the Veneer Spec code to replace the changelog box with a scrollable `UiScrollPanel`, mapping each entry as a child item:

```vnr
selector "#release-notes-list" -> UiScrollPanel {
    action: replace;
    
    child entries {
        selector: ".changelog-entry";
        bind version: ".version-tag | text";
        bind description: ".entry-text | text";
    }
}
```

# Replacing an inline status label with UiTagBadge
## User
Write a `.vnr` selector block that swaps this order status flag for `UiTagBadge`:

```html
<span class="order-status-flag" data-status="shipped">Shipped</span>
```
## Assistant
Here is the Veneer Spec code to replace the status flag in place with `UiTagBadge`:

```vnr
selector ".order-status-flag" -> UiTagBadge {
    action: replace;
    bind label: "self | text";
    bind status: "self | attr:data-status";
}
```

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
    tagline: "Build Faster, Ship Sooner";
    subtext: "The toolkit for modern engineering teams.";
    ctaLabel: "Get Started";
    ctaUrl: "https://example.com/signup";
    
    child primaryLinks extends HeroNavLink {
        selector: "a.hero-nav-link";
    }
}
```

# Mapping a used-goods listing page into UiItemDetailsPage
## User
Reconstruct this book listing into `UiItemDetailsPage`, converting the price to a clean number and preserving the seller contact form:

```html
<div id="book-listing">
  <h1 class="book-title">The Pragmatic Programmer</h1>
  <span class="book-price">$ 34.50</span>
  <div class="book-condition">Condition: Like New</div>
  <form id="legacy-seller-contact-form" action="/contact-seller"></form>
</div>
```
## Assistant
Here is the Veneer Spec code to reconstruct the listing into `UiItemDetailsPage`, cleaning the price with `cleanNumber` and preserving the seller contact form:

```vnr
reconstruct "#book-listing" -> UiItemDetailsPage {
    pageTitle: "Book Details";
    
    bind title: "h1.book-title | text";
    bind price: ".book-price | text | cleanNumber";
    bind condition: ".book-condition | text";
    
    preserve {
        contactSellerSlot: "#legacy-seller-contact-form";
    }
}
```

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
Since the pager sits outside the matched `#forum-results` container, use `scope: "document"` on the `child` block so its selector queries the whole page instead of just the container's descendants:

```vnr
reconstruct "#forum-results" -> UiPaginationBar {
    pageTitle: "Forum Results";
    
    child pages {
        scope: "document";
        selector: "#global-forum-pager a.pager-link";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

# Reconstructing a Q&A post page into UiPostDetails with plain children
## User
Map this question-and-answers page into `UiPostDetails`, with the answers as a plain child list (no legacy widgets need to be preserved here):

```html
<div id="question-detail">
  <h1 class="question-title">How do I debounce an input in React?</h1>
  <div class="question-body">I want to delay firing a search request...</div>
  <div class="answer-row">
    <div class="answer-body">Use a useEffect with a setTimeout cleanup.</div>
    <span class="answer-votes">14</span>
  </div>
</div>
```
## Assistant
Here is the Veneer Spec code to reconstruct the question page into `UiPostDetails`, with the answers mapped as a `child` array:

```vnr
reconstruct "#question-detail" -> UiPostDetails {
    pageTitle: "Question Detail";
    
    bind title: "h1.question-title | text";
    bind bodyHtml: ".question-body | html";
    
    child answers {
        selector: ".answer-row";
        bind body: ".answer-body | text";
        bind votes: ".answer-votes | text | number";
    }
}
```

# Reconstructing a metrics sidebar into UiStatsDashboard with currency cleanup
## User
Map this revenue widget into `UiStatsDashboard`, cleaning the currency-formatted values:

```html
<aside id="revenue-widget">
  <div class="metric-tile">
    <span class="metric-label">MRR</span>
    <span class="metric-value">$ 48,200.00</span>
  </div>
  <div class="metric-tile">
    <span class="metric-label">Churn</span>
    <span class="metric-value">1.8%</span>
  </div>
</aside>
```
## Assistant
Here is the Veneer Spec code to reconstruct the revenue widget into `UiStatsDashboard`, using `cleanNumber` to strip the currency symbol and thousands separator:

```vnr
reconstruct "#revenue-widget" -> UiStatsDashboard {
    pageTitle: "Revenue";
    
    child metrics {
        selector: ".metric-tile";
        bind label: ".metric-label | text";
        bind value: ".metric-value | text | cleanNumber";
    }
}
```

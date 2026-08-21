# Mapping a blog post grid from HTML
## User
Based on the following HTML snippet of a blog listing page, write a Veneer Spec (.vnr) reconstruct that replaces the main section with a `UiModernGridPage` containing post cards.

```html
<section id="posts-feed">
  <div class="k-post-card" id="post-101">
    <div class="thumb-container">
      <img src="/assets/covers/unsloth-guide.png" alt="Unsloth Guide Cover" />
    </div>
    <div class="post-details">
      <h2 class="post-title"><a href="/posts/unsloth-guide-3-13">Fine-tuning Qwen on Python 3.13</a></h2>
    </div>
  </div>
  <div class="k-post-card" id="post-102">
    <div class="thumb-container">
      <img src="/assets/covers/veneer-layout.png" alt="Veneer Layout Spec Cover" />
    </div>
    <div class="post-details">
      <h2 class="post-title"><a href="/posts/veneer-layout-declarations">Declarative layout overrides with VNR</a></h2>
    </div>
  </div>
</section>
```
## Assistant
Here is the Veneer Spec (.vnr) code to reconstruct the blog grid into a `UiModernGridPage` targeting the `#posts-feed` container:

```vnr
class BlogCard {
    bind title: "h2.post-title a | text";
    bind linkUrl: "h2.post-title a | attr:href";
    bind imageUrl: ".thumb-container img | attr:src";
    bind id: "self | attr:id";
}

reconstruct "#posts-feed" -> UiModernGridPage {
    pageTitle: "Blog Feed";
    
    child items -> UiImageCard extends BlogCard {
        selector: ".k-post-card";
    }
}
```

---

# Mapping an e-commerce catalog from HTML
## User
Write a Veneer Spec (.vnr) to reconstruct this search results listing into a modern `UiTableListPage` containing prices parsed as clean floats:

```html
<div class="listing-container">
  <div class="search-item-row" id="item-902">
    <img class="lazy-load" src="https://static.shop.com/prod/902.jpg" />
    <div class="info-block">
      <a class="item-link" href="/product/premium-keyboard">Premium Mechanical Keyboard</a>
      <span class="price-label">USD 1,299.00</span>
      <span class="badge-status instock">In Stock</span>
    </div>
  </div>
  <div class="search-item-row" id="item-903">
    <img class="lazy-load" src="https://static.shop.com/prod/903.jpg" />
    <div class="info-block">
      <a class="item-link" href="/product/wireless-mouse">Ergonomic Wireless Mouse</a>
      <span class="price-label">USD 79.99</span>
      <span class="badge-status backorder">Backordered</span>
    </div>
  </div>
</div>
```
## Assistant
You can reconstruct this product listing using `UiTableListPage`. We will clean the currency prefix and thousands separator using the `cleanNumber` pipe operation, and specify the column schema structure:

```vnr
class ProductRow {
    bind title: "a.item-link | text";
    bind url: "a.item-link | attr:href";
    bind price: "span.price-label | text | cleanNumber";
    bind status: "span.badge-status | text";
}

reconstruct ".listing-container" -> UiTableListPage {
    pageTitle: "Search Results";
    columns: R"([
      { "key": "title", "header": "Product", "type": "link", "urlKey": "url" },
      { "key": "price", "header": "Price", "type": "currency" },
      { "key": "status", "header": "Status", "type": "badge", "badgeStyleKey": "status" }
    ])";
    
    child tableRows extends ProductRow {
        selector: ".search-item-row";
    }
}
```

---

# Replacing header elements in HTML
## User
Based on this header HTML, write a selector block that replaces the global header with a `UiNavHeader`:

```html
<header id="global-header">
  <div class="header-logo-wrap">
    <a href="/dashboard"><img src="/brand/logo.svg" alt="Company Logo"/></a>
  </div>
  <nav class="navigation-links">
    <a class="nav-item" href="/dashboard">Dashboard</a>
    <a class="nav-item" href="/reports">Reports</a>
    <a class="nav-item" href="/settings">Settings</a>
  </nav>
</header>
```
## Assistant
Here is the Veneer Spec block to replace the legacy header with `UiNavHeader`:

```vnr
selector "#global-header" -> UiNavHeader {
    action: replace;
    siteName: "Company Hub";
    logoHref: "/dashboard";
    
    bind logoUrl: ".header-logo-wrap img | attr:src";
    
    child primaryLinks {
        selector: "nav.navigation-links a.nav-item";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

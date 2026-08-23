# Real-World HTML → Veneer Spec Examples

---

# Amazon-style product listing page
## User
Here is the HTML structure of a product search results page. Write a Veneer Spec reconstruct that modernizes the listing into a `UiTableListPage` with name, price, rating, and availability columns:

```html
<div id="search-results-wrapper">
  <div data-component-type="s-search-result" data-asin="B09XKCD4XP" class="s-result-item">
    <div class="s-card-container">
      <div class="a-section a-spacing-base">
        <img class="s-image" src="https://m.media-amazon.com/images/I/71abc.jpg" alt="Logitech MX Master 3S" />
      </div>
      <div class="a-section">
        <h2 class="a-size-mini s-line-clamp-2">
          <a class="a-link-normal s-underline-text" href="/dp/B09XKCD4XP">Logitech MX Master 3S – Advanced Wireless Mouse</a>
        </h2>
        <div class="a-row a-size-small">
          <span class="a-icon-alt">4.7 out of 5 stars</span>
          <span class="a-size-base s-underline-text">12,847</span>
        </div>
        <div class="a-row a-price">
          <span class="a-price"><span class="a-offscreen">$99.99</span></span>
        </div>
        <div class="a-row">
          <span class="a-color-success">In Stock</span>
        </div>
      </div>
    </div>
  </div>
  <div data-component-type="s-search-result" data-asin="B08N5KWB9H" class="s-result-item">
    <div class="s-card-container">
      <div class="a-section a-spacing-base">
        <img class="s-image" src="https://m.media-amazon.com/images/I/71xyz.jpg" alt="Apple Magic Mouse" />
      </div>
      <div class="a-section">
        <h2 class="a-size-mini s-line-clamp-2">
          <a class="a-link-normal s-underline-text" href="/dp/B08N5KWB9H">Apple Magic Mouse – Wireless, Rechargeable</a>
        </h2>
        <div class="a-row a-size-small">
          <span class="a-icon-alt">4.3 out of 5 stars</span>
          <span class="a-size-base s-underline-text">8,201</span>
        </div>
        <div class="a-row a-price">
          <span class="a-price"><span class="a-offscreen">$79.00</span></span>
        </div>
        <div class="a-row">
          <span class="a-color-success">In Stock</span>
        </div>
      </div>
    </div>
  </div>
</div>
```
## Assistant
```vnr
class AmazonProduct {
    bind name: "h2.a-size-mini a | text";
    bind url: "h2.a-size-mini a | attr:href";
    bind imageUrl: "img.s-image | attr:src";
    bind rating: "span.a-icon-alt | text";
    bind reviews: "span.a-size-base.s-underline-text | text";
    bind price: "span.a-offscreen | text | cleanNumber";
    bind availability: "span.a-color-success | text";
    bind asin: "self | attr:data-asin";
}

reconstruct "#search-results-wrapper" -> UiTableListPage {
    pageTitle: "Search Results";
    columns: R"([
      { "key": "name", "header": "Product", "type": "link", "urlKey": "url" },
      { "key": "price", "header": "Price", "type": "currency" },
      { "key": "rating", "header": "Rating", "type": "text" },
      { "key": "availability", "header": "Stock", "type": "badge", "badgeStyleKey": "availability" }
    ])";

    child tableRows extends AmazonProduct {
        selector: "[data-component-type='s-search-result']";
    }
}
```

---

# Reddit-style community thread feed
## User
Below is the HTML of a Reddit-like forum thread listing. Write a Veneer Spec reconstruct mapping it to `UiCommentListPage` with user, score, tags and nested replies:

```html
<div id="thread-listing" class="listing">
  <div class="thing id-t3_abc123 link self" id="thing_t3_abc123">
    <div class="entry">
      <p class="title">
        <a class="title may-blank" href="/r/programming/comments/abc123/asking_about_rust">Asking about Rust memory safety</a>
        <span class="domain">self.programming</span>
      </p>
      <div class="tagline">
        submitted <time class="live-timestamp" datetime="2024-01-15T08:30:00Z">3 hours ago</time>
        by <a class="author" href="/user/rustacean42">rustacean42</a>
      </div>
      <div class="score unvoted">
        <span class="number">1,245</span>
        <span class="word">points</span>
      </div>
      <ul class="flat-list buttons">
        <li class="first"><a class="comments may-blank" href="/r/programming/comments/abc123">243 comments</a></li>
      </ul>
      <ul class="flat-list flair-list">
        <li><span class="linkflairlabel">Discussion</span></li>
        <li><span class="linkflairlabel">Rust</span></li>
      </ul>
    </div>
    <div class="child">
      <div class="commentarea">
        <div class="comment" id="comment_d1e2f3">
          <div class="author">
            <a class="author" href="/user/ferris_crab">ferris_crab</a>
          </div>
          <div class="usertext-body"><p class="md">Rust's borrow checker is brilliant once you get past the initial curve.</p></div>
          <time class="live-timestamp" datetime="2024-01-15T09:00:00Z">2 hours ago</time>
        </div>
        <div class="comment" id="comment_a4b5c6">
          <div class="author">
            <a class="author" href="/user/cppfan_99">cppfan_99</a>
          </div>
          <div class="usertext-body"><p class="md">Coming from C++, the concepts feel very familiar.</p></div>
          <time class="live-timestamp" datetime="2024-01-15T09:45:00Z">1 hour ago</time>
        </div>
      </div>
    </div>
  </div>
</div>
```
## Assistant
```vnr
class ForumThread {
    bind postUrl: "a.title | attr:href";
    bind postDate: "time.live-timestamp | attr:datetime";
    bind postUser: "a.author | attr:href";
    bind postScore: "div.score span.number | text | cleanNumber";

    child tags {
        selector: "ul.flair-list li span.linkflairlabel";
        bind label: "self | text";
    }

    child comments {
        selector: "div.commentarea div.comment";
        bind author: "a.author | text";
        bind authorUrl: "a.author | attr:href";
        bind date: "time.live-timestamp | attr:datetime";
        bind body: "div.usertext-body p | text";
    }
}

reconstruct "#thread-listing" -> UiCommentListPage {
    pageTitle: "Programming";
    height: "100vh";

    child threads extends ForumThread {
        selector: "div.thing.link";
    }
}
```

---

# GitHub repository search results
## User
This HTML is from a GitHub-style repository search result list. Map it to a `UiTableListPage` with repo name, description, language, stars, and last updated:

```html
<div id="search-results" data-pjax-container>
  <ul class="repo-list">
    <li class="repo-list-item hx_hit-repo col-12 d-flex flex-justify-start py-4 public source">
      <div class="flex-auto">
        <h3 class="wb-break-all">
          <a href="/torvalds/linux" class="v-align-middle">torvalds/<strong>linux</strong></a>
        </h3>
        <p class="mb-1 col-9 color-fg-muted">Linux kernel source tree</p>
        <div class="d-flex flex-wrap text-small color-fg-muted mt-2">
          <div class="mr-3">
            <span class="repo-language-color ml-0" style="background-color: #555555"></span>
            <span itemprop="programmingLanguage">C</span>
          </div>
          <a href="/torvalds/linux/stargazers" class="muted-link mr-3">
            <svg class="octicon"></svg>
            <span>173,542</span>
          </a>
          <span>Updated <relative-time datetime="2024-01-18T12:00:00Z">Jan 18, 2024</relative-time></span>
        </div>
      </div>
    </li>
    <li class="repo-list-item hx_hit-repo col-12 d-flex flex-justify-start py-4 public source">
      <div class="flex-auto">
        <h3 class="wb-break-all">
          <a href="/microsoft/vscode" class="v-align-middle">microsoft/<strong>vscode</strong></a>
        </h3>
        <p class="mb-1 col-9 color-fg-muted">Visual Studio Code</p>
        <div class="d-flex flex-wrap text-small color-fg-muted mt-2">
          <div class="mr-3">
            <span class="repo-language-color ml-0" style="background-color: #2b7489"></span>
            <span itemprop="programmingLanguage">TypeScript</span>
          </div>
          <a href="/microsoft/vscode/stargazers" class="muted-link mr-3">
            <svg class="octicon"></svg>
            <span>158,700</span>
          </a>
          <span>Updated <relative-time datetime="2024-01-19T08:00:00Z">Jan 19, 2024</relative-time></span>
        </div>
      </div>
    </li>
  </ul>
</div>
```
## Assistant
```vnr
class RepoResult {
    bind name: "h3 a | text";
    bind url: "h3 a | attr:href";
    bind description: "p.color-fg-muted | text";
    bind language: "[itemprop='programmingLanguage'] | text";
    bind stars: "a.muted-link span | text | cleanNumber";
    bind updatedAt: "relative-time | attr:datetime";
}

reconstruct "#search-results" -> UiTableListPage {
    pageTitle: "Repository Search";
    columns: R"([
      { "key": "name", "header": "Repository", "type": "link", "urlKey": "url" },
      { "key": "description", "header": "Description", "type": "text" },
      { "key": "language", "header": "Language", "type": "badge", "badgeStyleKey": "language" },
      { "key": "stars", "header": "Stars", "type": "text" },
      { "key": "updatedAt", "header": "Updated", "type": "date" }
    ])";

    child tableRows extends RepoResult {
        selector: "ul.repo-list li.repo-list-item";
    }
}
```

---

# Hacker News-style link aggregator
## User
This HTML is from a Hacker News-style submission feed. Convert it to a `UiCommentListPage` with ranked items, authors, scores, and tag labels:

```html
<table id="hnmain" border="0" cellpadding="0" cellspacing="0" width="85%" bgcolor="#f6f6ef">
  <tbody>
    <tr class="athing" id="38981776">
      <td align="right" valign="top" class="title"><span class="rank">1.</span></td>
      <td class="title">
        <span class="titleline">
          <a href="https://neovim.io/news/2024/01/nvim-0.10">Neovim 0.10 Released</a>
          <span class="sitebit comhead"><a href="from?site=neovim.io">(neovim.io)</a></span>
        </span>
      </td>
    </tr>
    <tr>
      <td class="subtext">
        <span class="score" id="score_38981776">847 points</span>
        by <a href="user?id=johndoe" class="hnuser">johndoe</a>
        <span class="age" title="2024-01-14T12:00:00"><a href="item?id=38981776">3 hours ago</a></span>
        | <a href="item?id=38981776">312 comments</a>
      </td>
    </tr>
    <tr class="athing" id="38981890">
      <td align="right" valign="top" class="title"><span class="rank">2.</span></td>
      <td class="title">
        <span class="titleline">
          <a href="https://blog.rust-lang.org/2024/01/12/Rust-1.75.0.html">Rust 1.75.0 Released</a>
          <span class="sitebit comhead"><a href="from?site=rust-lang.org">(rust-lang.org)</a></span>
        </span>
      </td>
    </tr>
    <tr>
      <td class="subtext">
        <span class="score" id="score_38981890">1,203 points</span>
        by <a href="user?id=rustlover" class="hnuser">rustlover</a>
        <span class="age" title="2024-01-12T08:00:00"><a href="item?id=38981890">2 days ago</a></span>
        | <a href="item?id=38981890">504 comments</a>
      </td>
    </tr>
  </tbody>
</table>
```
## Assistant
Since HN uses adjacent `<tr>` pairs (`.athing` for title, the next `<tr>` for metadata), the best approach is to target the title row and use sibling selectors for metadata. We reconstruct the feed as `UiCommentListPage`:

```vnr
reconstruct "#hnmain" -> UiCommentListPage {
    pageTitle: "Hacker News";
    height: "100vh";

    child threads {
        selector: "tr.athing";
        bind postUrl: "span.titleline a | attr:href";
        bind id: "self | attr:id";
        bind postScore: "span.score | text | cleanNumber";
        bind postUser: "a.hnuser | text";
        bind postDate: "span.age | attr:title";

        child tags {
            selector: "span.sitebit a";
            bind label: "self | text";
        }
    }
}
```

---

# Booking.com hotel search results
## User
This is the HTML from a Booking.com-style hotel search listing. Map it to a `UiModernGridPage` with hotel cards showing image, name, rating, price per night, and link:

```html
<div id="search_results_table" data-testid="property-list">
  <div data-testid="property-card" class="a826ba81c4 fe821aea6b" id="hotel_11290921">
    <div class="fcab3ed991 a23c043802">
      <img src="https://cf.bstatic.com/static/img/hotel_0001.jpg" alt="Grand Palace Hotel" class="f9671d49b3 e8f7c070a7" />
    </div>
    <div class="a62f4c39b8 aab2d8b07f">
      <div class="fcab3ed991 b9b5f1e26d">
        <div class="f6431b446c a15b38c233">
          <a href="/hotel/pt/grand-palace.en-us.html" data-testid="title-link">
            <div class="f6431b446c a15b38c233 b06b0fbaf5">Grand Palace Hotel</div>
          </a>
          <span class="b5cd09854e dir-ltr">Lisbon, Portugal</span>
        </div>
        <div class="b5cd09854e dc5041d860">
          <div class="a3b8729ab1 e6208ee469 cb2cbb3ccb" aria-label="Scored 8.9">
            <div class="d10a6220b4">8.9</div>
            <div class="b5cd09854e f0d4d6a2f5">Excellent</div>
          </div>
        </div>
      </div>
      <div class="fcab3ed991 c90c0a70d3 eb67815534">
        <div class="bui-price-display__value prco-f64921b4f5 prco-dec1aa15b4">€ 220</div>
        <div class="prd-taxes-and-fees-under-price">+€ 32 taxes and fees</div>
      </div>
    </div>
  </div>
  <div data-testid="property-card" class="a826ba81c4 fe821aea6b" id="hotel_22478012">
    <div class="fcab3ed991 a23c043802">
      <img src="https://cf.bstatic.com/static/img/hotel_0002.jpg" alt="Riverside Boutique Inn" class="f9671d49b3 e8f7c070a7" />
    </div>
    <div class="a62f4c39b8 aab2d8b07f">
      <div class="fcab3ed991 b9b5f1e26d">
        <div class="f6431b446c a15b38c233">
          <a href="/hotel/pt/riverside-boutique.en-us.html" data-testid="title-link">
            <div class="f6431b446c a15b38c233 b06b0fbaf5">Riverside Boutique Inn</div>
          </a>
          <span class="b5cd09854e dir-ltr">Porto, Portugal</span>
        </div>
        <div class="b5cd09854e dc5041d860">
          <div class="a3b8729ab1 e6208ee469 cb2cbb3ccb" aria-label="Scored 9.1">
            <div class="d10a6220b4">9.1</div>
            <div class="b5cd09854e f0d4d6a2f5">Superb</div>
          </div>
        </div>
      </div>
      <div class="fcab3ed991 c90c0a70d3 eb67815534">
        <div class="bui-price-display__value prco-f64921b4f5 prco-dec1aa15b4">€ 145</div>
        <div class="prd-taxes-and-fees-under-price">+€ 19 taxes and fees</div>
      </div>
    </div>
  </div>
</div>
```
## Assistant
```vnr
class HotelCard {
    bind title: "[data-testid='title-link'] div.b06b0fbaf5 | text";
    bind url: "[data-testid='title-link'] | attr:href";
    bind imageUrl: "img | attr:src";
    bind location: "span.dir-ltr | text";
    bind score: "div.d10a6220b4 | text";
    bind scoreLabel: "div.f0d4d6a2f5 | text";
    bind pricePerNight: "div.bui-price-display__value | text | cleanNumber";
    bind taxes: "div.prd-taxes-and-fees-under-price | text";
    bind id: "self | attr:id";
}

reconstruct "#search_results_table" -> UiModernGridPage {
    pageTitle: "Hotel Search";

    child items extends HotelCard {
        selector: "[data-testid='property-card']";
    }
}
```

---

# LinkedIn job postings feed
## User
This HTML comes from a LinkedIn-style job listing feed. Create a Veneer Spec that maps it to a `UiTableListPage` with job title, company, location, type, and date:

```html
<div id="jobs-search-results" class="scaffold-layout__list-detail-container">
  <ul class="scaffold-layout__list-container" role="list">
    <li class="jobs-search-results__list-item ember-view" data-occludable-job-id="3850112233">
      <div class="job-card-container--clickable job-card-list__entity-lockup">
        <div class="artdeco-entity-image">
          <img src="https://static.licdn.com/aero-v1/sc/h/company_0001.jpg" alt="Cloudflare" />
        </div>
        <div class="job-card-list__entity-lockup-content">
          <a class="job-card-list__title--link" href="/jobs/view/3850112233">
            <strong>Senior Software Engineer – Rust</strong>
          </a>
          <div class="job-card-container__company-name">Cloudflare</div>
          <ul class="job-card-container__metadata-wrapper">
            <li class="job-card-container__metadata-item">Remote</li>
            <li class="job-card-container__metadata-item job-card-container__metadata-item--workplace-type">Full-time</li>
          </ul>
        </div>
        <time class="job-card-container__listed-time" datetime="2024-01-16">2 days ago</time>
      </div>
    </li>
    <li class="jobs-search-results__list-item ember-view" data-occludable-job-id="3850445566">
      <div class="job-card-container--clickable job-card-list__entity-lockup">
        <div class="artdeco-entity-image">
          <img src="https://static.licdn.com/aero-v1/sc/h/company_0002.jpg" alt="Stripe" />
        </div>
        <div class="job-card-list__entity-lockup-content">
          <a class="job-card-list__title--link" href="/jobs/view/3850445566">
            <strong>Staff Platform Engineer</strong>
          </a>
          <div class="job-card-container__company-name">Stripe</div>
          <ul class="job-card-container__metadata-wrapper">
            <li class="job-card-container__metadata-item">San Francisco, CA</li>
            <li class="job-card-container__metadata-item job-card-container__metadata-item--workplace-type">Hybrid</li>
          </ul>
        </div>
        <time class="job-card-container__listed-time" datetime="2024-01-17">1 day ago</time>
      </div>
    </li>
  </ul>
</div>
```
## Assistant
```vnr
class JobPosting {
    bind title: "a.job-card-list__title--link strong | text";
    bind url: "a.job-card-list__title--link | attr:href";
    bind company: "div.job-card-container__company-name | text";
    bind companyLogo: "img | attr:src";
    bind location: "li.job-card-container__metadata-item:first-child | text";
    bind jobType: "li.job-card-container__metadata-item--workplace-type | text";
    bind postedDate: "time.job-card-container__listed-time | attr:datetime";
    bind id: "self | attr:data-occludable-job-id";
}

reconstruct "#jobs-search-results" -> UiTableListPage {
    pageTitle: "Job Search";
    columns: R"([
      { "key": "title", "header": "Position", "type": "link", "urlKey": "url" },
      { "key": "company", "header": "Company", "type": "text" },
      { "key": "location", "header": "Location", "type": "text" },
      { "key": "jobType", "header": "Type", "type": "badge", "badgeStyleKey": "jobType" },
      { "key": "postedDate", "header": "Posted", "type": "date" }
    ])";

    child tableRows extends JobPosting {
        selector: "li.jobs-search-results__list-item";
    }
}
```

---

# Stack Overflow-style questions list
## User
This is the HTML from a Stack Overflow-style questions list page. Map it to a `UiCommentListPage` including questions as threads, their tags, and voter counts:

```html
<div id="questions" class="question-summary-list">
  <div class="s-post-summary js-post-summary" id="question-summary-77821445" data-post-id="77821445">
    <div class="s-post-summary--stats">
      <div class="s-post-summary--stats-item s-post-summary--stats-item__emphasized">
        <span class="s-post-summary--stats-item-number">1,247</span>
        <span class="s-post-summary--stats-item-unit">votes</span>
      </div>
      <div class="s-post-summary--stats-item">
        <span class="s-post-summary--stats-item-number">18</span>
        <span class="s-post-summary--stats-item-unit">answers</span>
      </div>
    </div>
    <div class="s-post-summary--content">
      <h3 class="s-post-summary--content-title">
        <a href="/questions/77821445/how-does-rust-handle-async-lifetimes" class="s-link">How does Rust handle async lifetimes?</a>
      </h3>
      <div class="s-post-summary--content-excerpt">
        I'm trying to understand how the borrow checker interacts with async functions...
      </div>
      <div class="s-post-summary--meta">
        <div class="s-post-summary--meta-tags">
          <a href="/questions/tagged/rust" class="s-tag">rust</a>
          <a href="/questions/tagged/async" class="s-tag">async</a>
          <a href="/questions/tagged/lifetimes" class="s-tag">lifetimes</a>
        </div>
        <div class="s-post-summary--meta-info">
          <span class="s-user-card--time">
            asked <time datetime="2024-01-15T09:00:00Z">Jan 15</time>
            by <a href="/users/1234/rustacean42" class="s-user-card--link">rustacean42</a>
          </span>
        </div>
      </div>
    </div>
  </div>
</div>
```
## Assistant
```vnr
class SOQuestion {
    bind postUrl: "h3.s-post-summary--content-title a | attr:href";
    bind postScore: "div.s-post-summary--stats-item__emphasized span.s-post-summary--stats-item-number | text | cleanNumber";
    bind postUser: "a.s-user-card--link | text";
    bind postDate: "time | attr:datetime";
    bind id: "self | attr:data-post-id";

    child tags {
        selector: "div.s-post-summary--meta-tags a.s-tag";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}

reconstruct "#questions" -> UiCommentListPage {
    pageTitle: "Questions";
    height: "100vh";

    child threads extends SOQuestion {
        selector: "div.s-post-summary";
    }
}
```

---

# YouTube-style video grid
## User
This is HTML from a YouTube-style video browse grid. Create a Veneer Spec to render it as a `UiModernGridPage` with video thumbnails, titles, channel names, views, and timestamps:

```html
<div id="contents" class="ytd-rich-grid-renderer">
  <ytd-rich-item-renderer class="style-scope ytd-rich-grid-renderer" id="video-gH82qG3zMlc">
    <div id="content" class="style-scope ytd-rich-item-renderer">
      <ytd-rich-grid-media>
        <div id="thumbnail">
          <a id="thumbnail" class="yt-simple-endpoint" href="/watch?v=gH82qG3zMlc">
            <yt-image>
              <img src="https://i.ytimg.com/vi/gH82qG3zMlc/hqdefault.jpg" alt="Learn Rust in 10 minutes" />
            </yt-image>
            <div id="overlays">
              <ytd-thumbnail-overlay-time-status-renderer><span class="style-scope ytd-badge-supported-renderer">12:34</span></ytd-thumbnail-overlay-time-status-renderer>
            </div>
          </a>
        </div>
        <div id="meta">
          <h3 class="title-and-metadata-row">
            <a id="video-title-link" class="yt-simple-endpoint" href="/watch?v=gH82qG3zMlc">
              <yt-formatted-string id="video-title">Learn Rust in 10 Minutes</yt-formatted-string>
            </a>
          </h3>
          <ytd-channel-name id="channel-name">
            <a class="yt-simple-endpoint" href="/c/LetsGetRusty">Let's Get Rusty</a>
          </ytd-channel-name>
          <div id="metadata-line">
            <span class="inline-metadata-item style-scope ytd-video-meta-block">1.4M views</span>
            <span class="inline-metadata-item style-scope ytd-video-meta-block">2 weeks ago</span>
          </div>
        </div>
      </ytd-rich-grid-media>
    </div>
  </ytd-rich-item-renderer>
</div>
```
## Assistant
```vnr
class YouTubeVideo {
    bind title: "yt-formatted-string#video-title | text";
    bind url: "a#video-title-link | attr:href";
    bind imageUrl: "yt-image img | attr:src";
    bind channel: "ytd-channel-name a | text";
    bind channelUrl: "ytd-channel-name a | attr:href";
    bind views: "span.inline-metadata-item:first-child | text";
    bind postedAgo: "span.inline-metadata-item:last-child | text";
    bind duration: "ytd-thumbnail-overlay-time-status-renderer span | text";
    bind id: "self | attr:id";
}

reconstruct "#contents" -> UiModernGridPage {
    pageTitle: "Browse";

    child items extends YouTubeVideo {
        selector: "ytd-rich-item-renderer";
    }
}
```

---

# Airbnb-style accommodation listing
## User
This is the HTML from an Airbnb-style property listing page. Write a Veneer Spec to map it to a `UiModernGridPage` with property cards showing image, name, location, price, and rating:

```html
<div id="listingsContainer" data-section-id="EXPLORE_STRUCTURED_PAGE_CONTENT">
  <div itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem" class="_8ssblpx">
    <div class="c4mnd7m dir dir-ltr">
      <div class="g1qv1ctd dir dir-ltr">
        <div class="pmkl8re atm_h3_1y44olf dir dir-ltr">
          <picture>
            <img src="https://a0.muscache.com/im/pictures/hosting/Hosting-U3RheVN1cHBseUxpc3Rpbmc6NDM5MTE5Mzc=/original/photo1.jpg" alt="Cozy loft in Lisbon" class="itu7ddkm atm_e2_idpfg4" />
          </picture>
        </div>
      </div>
      <div class="g1qv1ctd dir dir-ltr">
        <div class="t1jojoys dir dir-ltr">
          <div class="cbheav2 dir dir-ltr">
            <a aria-label="Cozy loft in Alfama" class="rfexzly" href="/rooms/43911937">
              <div class="t6mzqp7">Cozy loft in Alfama</div>
              <div class="fb4nyux s1cjsi4j dir dir-ltr">Lisbon, Portugal</div>
            </a>
          </div>
          <div class="r4a59j5 dir dir-ltr">
            <span class="a8jt5op dir dir-ltr">
              <svg class="_1pns8vn" viewBox="0 0 32 32"><path d="M15.094 1.579l-4.124 8.885-9.86 1.27a1 1 0 0 0-.542 1.736l7.293 6.565-1.965 9.852a1 1 0 0 0 1.483 1.061L16 25.951l8.625 4.997a1 1 0 0 0 1.483-1.061l-1.965-9.852 7.293-6.565a1 1 0 0 0-.541-1.736l-9.86-1.27-4.124-8.885a1 1 0 0 0-1.812 0z"></path></svg>
              4.92
            </span>
            <span class="r4a59j5">(128)</span>
          </div>
        </div>
        <div class="lrl13de dir dir-ltr">
          <div class="p3oik3r dir dir-ltr">
            <span>€ 89</span>
            <span class="_tyxjp1"> / night</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```
## Assistant
```vnr
class AirbnbListing {
    bind title: "a.rfexzly div.t6mzqp7 | text";
    bind url: "a.rfexzly | attr:href";
    bind imageUrl: "img | attr:src";
    bind location: "div.fb4nyux | text";
    bind rating: "span.a8jt5op | text";
    bind reviews: "span.r4a59j5 | text";
    bind pricePerNight: "span.p3oik3r span:first-child | text | cleanNumber";
}

reconstruct "#listingsContainer" -> UiModernGridPage {
    pageTitle: "Stays";

    child items extends AirbnbListing {
        selector: "[itemprop='itemListElement']";
    }
}
```

---

# Wikipedia-style article table of countries
## User
This Wikipedia-style HTML table lists countries with area and population data. Convert it to a `UiTableListPage`:

```html
<div id="mw-content-text">
  <table class="wikitable sortable jquery-tablesorter" id="sortable-countries">
    <thead>
      <tr>
        <th>Country</th>
        <th>Population</th>
        <th>Area (km²)</th>
        <th>Density</th>
        <th>Capital</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="/wiki/China" title="China">China</a></td>
        <td><span class="sortkey">1411778724</span> 1,411,778,724</td>
        <td>9,596,960</td>
        <td>147</td>
        <td><a href="/wiki/Beijing">Beijing</a></td>
      </tr>
      <tr>
        <td><a href="/wiki/India" title="India">India</a></td>
        <td><span class="sortkey">1428627663</span> 1,428,627,663</td>
        <td>3,287,263</td>
        <td>434</td>
        <td><a href="/wiki/New_Delhi">New Delhi</a></td>
      </tr>
      <tr>
        <td><a href="/wiki/United_States" title="United States">United States</a></td>
        <td><span class="sortkey">335893238</span> 335,893,238</td>
        <td>9,833,517</td>
        <td>34</td>
        <td><a href="/wiki/Washington,_D.C.">Washington D.C.</a></td>
      </tr>
    </tbody>
  </table>
</div>
```
## Assistant
```vnr
reconstruct "#mw-content-text" -> UiTableListPage {
    pageTitle: "Countries by Population";
    columns: R"([
      { "key": "country", "header": "Country", "type": "link", "urlKey": "countryUrl" },
      { "key": "population", "header": "Population", "type": "text" },
      { "key": "area", "header": "Area (km²)", "type": "text" },
      { "key": "density", "header": "Density", "type": "text" },
      { "key": "capital", "header": "Capital", "type": "link", "urlKey": "capitalUrl" }
    ])";

    child tableRows {
        selector: "table.wikitable tbody tr";
        bind country: "td:nth-child(1) a | text";
        bind countryUrl: "td:nth-child(1) a | attr:href";
        bind population: "td:nth-child(2) | text";
        bind area: "td:nth-child(3) | text";
        bind density: "td:nth-child(4) | text";
        bind capital: "td:nth-child(5) a | text";
        bind capitalUrl: "td:nth-child(5) a | attr:href";
    }
}
```

---

# NPM package search results
## User
Here is HTML from an NPM-style package registry search page. Map it to a `UiTableListPage` with package name, description, version, weekly downloads, and author:

```html
<div id="packages" class="flex-grow-1">
  <section class="ph3 pv3">
    <div class="w-100 bb b--black-10 flex items-start">
      <div class="flex-auto">
        <h3 class="f4 fw6 mb2">
          <a class="fw6 black no-underline link" href="/package/lodash">lodash</a>
        </h3>
        <p class="f6 dark-gray lh-copy mv1">Lodash modular utilities.</p>
        <p class="f6 dark-gray lh-copy mv1">
          published <strong>4.17.21</strong>
          &bull; 3 years ago
          &bull; <a href="/~jdalton" class="fw6 black no-underline link">jdalton</a>
        </p>
      </div>
      <div class="flex-none tr ml3 f6 dark-gray">
        <span class="fw6">48,792,101</span> weekly downloads
      </div>
    </div>
    <div class="w-100 bb b--black-10 flex items-start mt3">
      <div class="flex-auto">
        <h3 class="f4 fw6 mb2">
          <a class="fw6 black no-underline link" href="/package/react">react</a>
        </h3>
        <p class="f6 dark-gray lh-copy mv1">React is a JavaScript library for building user interfaces.</p>
        <p class="f6 dark-gray lh-copy mv1">
          published <strong>18.2.0</strong>
          &bull; 2 years ago
          &bull; <a href="/~acdlite" class="fw6 black no-underline link">acdlite</a>
        </p>
      </div>
      <div class="flex-none tr ml3 f6 dark-gray">
        <span class="fw6">22,413,897</span> weekly downloads
      </div>
    </div>
  </section>
</div>
```
## Assistant
```vnr
class NpmPackage {
    bind name: "h3 a | text";
    bind url: "h3 a | attr:href";
    bind description: "p.lh-copy:first-of-type | text";
    bind version: "p.lh-copy:last-of-type strong | text";
    bind author: "p.lh-copy:last-of-type a | text";
    bind authorUrl: "p.lh-copy:last-of-type a | attr:href";
    bind weeklyDownloads: "div.flex-none span.fw6 | text | cleanNumber";
}

reconstruct "#packages" -> UiTableListPage {
    pageTitle: "Package Search";
    columns: R"([
      { "key": "name", "header": "Package", "type": "link", "urlKey": "url" },
      { "key": "description", "header": "Description", "type": "text" },
      { "key": "version", "header": "Version", "type": "text" },
      { "key": "weeklyDownloads", "header": "Weekly DL", "type": "text" },
      { "key": "author", "header": "Author", "type": "link", "urlKey": "authorUrl" }
    ])";

    child tableRows extends NpmPackage {
        selector: "section.ph3 div.bb";
    }
}
```

---

# Medium-style article blog feed
## User
This HTML is from a Medium-style blog feed page. Map it to a `UiModernGridPage` with article cards showing title, author, publication, tags, reading time, and claps:

```html
<div id="root">
  <div class="ab bc cd">
    <article class="postItem">
      <div class="postItem-header">
        <div class="postAuthor">
          <img class="avatar" src="https://miro.medium.com/fit/c/40/40/1*abc.jpg" alt="John Doe" />
          <a class="authorName" href="/@johndoe">John Doe</a>
          <span class="pubName">in <a href="/pub/towards-data-science">Towards Data Science</a></span>
        </div>
      </div>
      <div class="postItem-body">
        <h2 class="postTitle"><a href="/p/understanding-transformers-9c1b2e3d" class="postTitleLink">Understanding Transformers from Scratch</a></h2>
        <p class="postSubtitle">A visual guide to attention mechanisms and why they changed everything</p>
      </div>
      <div class="postItem-footer">
        <div class="postTags">
          <a href="/tag/machine-learning" class="tag">Machine Learning</a>
          <a href="/tag/deep-learning" class="tag">Deep Learning</a>
        </div>
        <div class="postMeta">
          <span class="readingTime">8 min read</span>
          <span class="claps">1.2K claps</span>
        </div>
      </div>
    </article>
    <article class="postItem">
      <div class="postItem-header">
        <div class="postAuthor">
          <img class="avatar" src="https://miro.medium.com/fit/c/40/40/1*xyz.jpg" alt="Jane Smith" />
          <a class="authorName" href="/@janesmith">Jane Smith</a>
          <span class="pubName">in <a href="/pub/better-programming">Better Programming</a></span>
        </div>
      </div>
      <div class="postItem-body">
        <h2 class="postTitle"><a href="/p/rust-vs-go-2024" class="postTitleLink">Rust vs Go in 2024: The Definitive Comparison</a></h2>
        <p class="postSubtitle">After using both in production, here's what I learned</p>
      </div>
      <div class="postItem-footer">
        <div class="postTags">
          <a href="/tag/rust" class="tag">Rust</a>
          <a href="/tag/go" class="tag">Go</a>
          <a href="/tag/programming" class="tag">Programming</a>
        </div>
        <div class="postMeta">
          <span class="readingTime">12 min read</span>
          <span class="claps">3.8K claps</span>
        </div>
      </div>
    </article>
  </div>
</div>
```
## Assistant
```vnr
class MediumArticle {
    bind title: "h2.postTitle a | text";
    bind url: "h2.postTitle a | attr:href";
    bind subtitle: "p.postSubtitle | text";
    bind author: "a.authorName | text";
    bind authorUrl: "a.authorName | attr:href";
    bind authorAvatar: "img.avatar | attr:src";
    bind publication: "span.pubName a | text";
    bind readingTime: "span.readingTime | text";
    bind claps: "span.claps | text";

    child tags {
        selector: "div.postTags a.tag";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}

reconstruct "#root" -> UiModernGridPage {
    pageTitle: "Feed";

    child items extends MediumArticle {
        selector: "article.postItem";
    }
}
```

---

# Goodreads-style book listing
## User
This HTML is from a Goodreads-style book database listing. Write a Veneer Spec to reconstruct it as a `UiTableListPage` with book title, author, average rating, ratings count, and genre tags:

```html
<div id="booksSection">
  <table id="books" class="tablesorter bookList">
    <thead>
      <tr>
        <th>Cover</th>
        <th>Title / Author</th>
        <th>Rating</th>
        <th>Ratings</th>
        <th>Genre</th>
      </tr>
    </thead>
    <tbody>
      <tr itemscope itemtype="http://schema.org/Book">
        <td class="cover">
          <a href="/book/show/2767052-the-hunger-games">
            <img src="https://images.gr-assets.com/books/1447303603s/2767052.jpg" alt="The Hunger Games" class="bookCover" />
          </a>
        </td>
        <td class="title">
          <a class="bookTitle" href="/book/show/2767052-the-hunger-games" itemprop="url">
            <span itemprop="name">The Hunger Games</span>
          </a>
          <br/>
          <span class="by">by</span>
          <a class="authorName" href="/author/show/153394.Suzanne_Collins" itemprop="author">Suzanne Collins</a>
        </td>
        <td class="rating">
          <span class="minirating">
            <span class="average_rating">4.33</span>
          </span>
        </td>
        <td class="num_ratings"><span class="count value-title">8,745,231</span></td>
        <td class="genre">
          <a href="/genres/dystopia" class="gradelement actionLinkLite bookPageGenreLink">dystopia</a>
          <a href="/genres/young-adult" class="gradelement actionLinkLite bookPageGenreLink">young-adult</a>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```
## Assistant
```vnr
class BookRow {
    bind title: "span[itemprop='name'] | text";
    bind url: "a.bookTitle | attr:href";
    bind coverImage: "img.bookCover | attr:src";
    bind author: "a.authorName | text";
    bind authorUrl: "a.authorName | attr:href";
    bind rating: "span.average_rating | text";
    bind ratingsCount: "span.count | text | cleanNumber";

    child tags {
        selector: "td.genre a.bookPageGenreLink";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}

reconstruct "#booksSection" -> UiTableListPage {
    pageTitle: "Book Database";
    columns: R"([
      { "key": "title", "header": "Book", "type": "link", "urlKey": "url" },
      { "key": "author", "header": "Author", "type": "link", "urlKey": "authorUrl" },
      { "key": "rating", "header": "Rating", "type": "text" },
      { "key": "ratingsCount", "header": "Reviews", "type": "text" }
    ])";

    child tableRows extends BookRow {
        selector: "table#books tbody tr";
    }
}
```

---

# Legacy admin dashboard with stats and nav
## User
This legacy admin dashboard HTML has a top navigation bar and KPI stat cards. Replace the nav with `UiNavHeader` and the stats panel with `UiStatsDashboard`:

```html
<nav id="admin-topbar">
  <div class="brand">
    <a href="/admin"><img src="/assets/admin-logo.svg" alt="AdminPro" /></a>
  </div>
  <ul class="nav-links">
    <li><a href="/admin/overview">Overview</a></li>
    <li><a href="/admin/users">Users</a></li>
    <li><a href="/admin/reports">Reports</a></li>
    <li><a href="/admin/settings">Settings</a></li>
  </ul>
  <div class="user-menu">
    <img src="/avatars/admin.jpg" alt="Admin User" />
    <a href="/admin/profile">Admin User</a>
  </div>
</nav>

<div id="kpi-dashboard">
  <div class="period-tab-row">
    <a href="/admin/stats?period=day" class="tab active">Today</a>
    <a href="/admin/stats?period=week" class="tab">This Week</a>
    <a href="/admin/stats?period=month" class="tab">This Month</a>
  </div>
  <div class="stat-card">
    <h3 class="stat-title">Top Pages</h3>
    <table class="stat-table">
      <tbody>
        <tr>
          <td class="rank">#1</td>
          <td class="stat-name"><a href="/pricing">Pricing</a></td>
          <td class="stat-value">24,891 views</td>
        </tr>
        <tr>
          <td class="rank">#2</td>
          <td class="stat-name"><a href="/blog">Blog</a></td>
          <td class="stat-value">18,342 views</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```
## Assistant
```vnr
selector "#admin-topbar" -> UiNavHeader {
    action: replace;
    sticky: true;

    bind logoUrl: "div.brand img | attr:src";
    logoHref: "/admin";

    child primaryLinks {
        selector: "ul.nav-links li a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}

reconstruct "#kpi-dashboard" -> UiStatsDashboard {
    pageTitle: "Admin Dashboard";

    child navLinks {
        selector: "div.period-tab-row a.tab";
        bind label: "self | text";
        bind url: "self | attr:href";
    }

    child sections {
        selector: "div.stat-card";
        bind title: "h3.stat-title | text";

        child items {
            selector: "table.stat-table tbody tr";
            bind place: "td.rank | text";
            bind name: "td.stat-name a | text";
            bind profileUrl: "td.stat-name a | attr:href";
            bind amount: "td.stat-value | text";
        }
    }
}
```

---

# E-commerce product category page with sidebar and grid
## User
This HTML has a sidebar category filter and a main product grid. Replace the nav sidebar with `UiNavSidebar` and the product grid with `UiModernGridPage`:

```html
<nav id="category-sidebar">
  <div class="sidebar-header">
    <h2>Categories</h2>
  </div>
  <ul class="category-tree">
    <li class="cat-item cat-item-12">
      <a href="/category/electronics">Electronics</a>
      <ul class="children">
        <li class="cat-item cat-item-15"><a href="/category/laptops">Laptops</a></li>
        <li class="cat-item cat-item-16"><a href="/category/phones">Phones</a></li>
      </ul>
    </li>
    <li class="cat-item cat-item-20">
      <a href="/category/clothing">Clothing</a>
    </li>
  </ul>
</nav>

<main id="product-grid-container">
  <h1 class="page-heading">Electronics</h1>
  <div class="products-grid row">
    <div class="product-item col-lg-3" data-pid="5512">
      <a class="product-thumb-link" href="/product/macbook-pro-16-m3">
        <img class="product-image" src="/products/mbp16-m3.jpg" alt="MacBook Pro 16" />
      </a>
      <div class="product-info">
        <h3 class="product-name"><a href="/product/macbook-pro-16-m3">MacBook Pro 16" M3 Pro</a></h3>
        <div class="product-rating">
          <span class="stars" data-score="4.8">★★★★★</span>
          <span class="count">(382)</span>
        </div>
        <div class="product-price">
          <span class="price-current">R$ 23.499,00</span>
          <span class="price-old">R$ 25.999,00</span>
        </div>
        <span class="badge badge-new">New</span>
      </div>
    </div>
    <div class="product-item col-lg-3" data-pid="5513">
      <a class="product-thumb-link" href="/product/dell-xps-15-oled">
        <img class="product-image" src="/products/xps15-oled.jpg" alt="Dell XPS 15 OLED" />
      </a>
      <div class="product-info">
        <h3 class="product-name"><a href="/product/dell-xps-15-oled">Dell XPS 15 OLED</a></h3>
        <div class="product-rating">
          <span class="stars" data-score="4.6">★★★★☆</span>
          <span class="count">(219)</span>
        </div>
        <div class="product-price">
          <span class="price-current">R$ 17.999,00</span>
        </div>
        <span class="badge badge-sale">Sale</span>
      </div>
    </div>
  </div>
</main>
```
## Assistant
```vnr
selector "#category-sidebar" -> UiNavSidebar {
    action: replace;

    child navItems {
        selector: "ul.category-tree > li.cat-item > a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}

class ProductCard {
    bind title: "h3.product-name a | text";
    bind url: "h3.product-name a | attr:href";
    bind imageUrl: "img.product-image | attr:src";
    bind rating: "span.stars | attr:data-score";
    bind reviewCount: "span.count | text";
    bind price: "span.price-current | text | cleanNumber";
    bind originalPrice: "span.price-old | text | cleanNumber";
    bind badge: "span.badge | text";
    bind id: "self | attr:data-pid";
}

reconstruct "#product-grid-container" -> UiModernGridPage {
    pageTitle: "h1.page-heading | text";

    child items extends ProductCard {
        selector: "div.product-item";
    }
}
```

---

# CrunchBase-style startup directory
## User
This HTML is from a CrunchBase-style startup directory. Map it to a `UiTableListPage` with startup name, industry tags, funding stage, amount raised, and last funded date:

```html
<div id="org-search-results">
  <ul class="cb-org-list">
    <li class="org-card" data-org-id="openai">
      <div class="org-card-header">
        <img class="org-logo" src="https://assets.crunchbase.com/org/openai.jpg" alt="OpenAI" />
        <div class="org-name-block">
          <a class="org-name-link" href="/organization/openai">OpenAI</a>
          <span class="org-location">San Francisco, CA, USA</span>
        </div>
      </div>
      <p class="org-description">Artificial intelligence research lab developing AGI for the benefit of humanity.</p>
      <div class="org-categories">
        <a href="/search/organizations?category_uids=artificial-intelligence" class="cb-category-tag">Artificial Intelligence</a>
        <a href="/search/organizations?category_uids=machine-learning" class="cb-category-tag">Machine Learning</a>
      </div>
      <div class="org-funding">
        <span class="funding-stage">Series E</span>
        <span class="funding-amount">$11.3B raised</span>
        <span class="funding-date">Jan 2024</span>
      </div>
    </li>
    <li class="org-card" data-org-id="anthropic">
      <div class="org-card-header">
        <img class="org-logo" src="https://assets.crunchbase.com/org/anthropic.jpg" alt="Anthropic" />
        <div class="org-name-block">
          <a class="org-name-link" href="/organization/anthropic">Anthropic</a>
          <span class="org-location">San Francisco, CA, USA</span>
        </div>
      </div>
      <p class="org-description">AI safety company working on interpretable, steerable, and reliable AI systems.</p>
      <div class="org-categories">
        <a href="/search/organizations?category_uids=artificial-intelligence" class="cb-category-tag">Artificial Intelligence</a>
        <a href="/search/organizations?category_uids=ai-safety" class="cb-category-tag">AI Safety</a>
      </div>
      <div class="org-funding">
        <span class="funding-stage">Series D</span>
        <span class="funding-amount">$7.7B raised</span>
        <span class="funding-date">Dec 2023</span>
      </div>
    </li>
  </ul>
</div>
```
## Assistant
```vnr
class StartupEntry {
    bind name: "a.org-name-link | text";
    bind url: "a.org-name-link | attr:href";
    bind logoUrl: "img.org-logo | attr:src";
    bind location: "span.org-location | text";
    bind description: "p.org-description | text";
    bind fundingStage: "span.funding-stage | text";
    bind amountRaised: "span.funding-amount | text";
    bind lastFundedDate: "span.funding-date | text";
    bind id: "self | attr:data-org-id";

    child tags {
        selector: "div.org-categories a.cb-category-tag";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}

reconstruct "#org-search-results" -> UiTableListPage {
    pageTitle: "Organization Search";
    columns: R"([
      { "key": "name", "header": "Company", "type": "link", "urlKey": "url" },
      { "key": "description", "header": "Description", "type": "text" },
      { "key": "fundingStage", "header": "Stage", "type": "badge", "badgeStyleKey": "fundingStage" },
      { "key": "amountRaised", "header": "Total Raised", "type": "text" },
      { "key": "lastFundedDate", "header": "Last Funded", "type": "text" }
    ])";

    child tableRows extends StartupEntry {
        selector: "li.org-card";
    }
}
```

---

# Productboard-style feature roadmap
## User
This HTML is from a product roadmap board. Map it to a `UiDashboardPage` with feature cards showing title, status, owner, and priority:

```html
<div id="roadmap-board" data-view="board">
  <div class="roadmap-header">
    <h1>Q1 2024 Product Roadmap</h1>
    <p class="roadmap-sub">Engineering features in progress and planned</p>
  </div>
  <div class="features-container">
    <div class="feature-card" data-feature-id="feat-001" data-status="in-progress">
      <div class="feature-header">
        <span class="priority-badge high">High</span>
        <span class="status-label">In Progress</span>
      </div>
      <h3 class="feature-title"><a href="/features/feat-001">Native C++ Validation Engine</a></h3>
      <p class="feature-desc">Replace Node.js validate.js subprocess with a 100% native C++ engine embedded in spm-cli.</p>
      <div class="feature-meta">
        <span class="owner">
          <img src="/avatars/eng01.jpg" alt="Alice" class="owner-avatar" />
          Alice Chen
        </span>
        <span class="feature-date">Due: Jan 31, 2024</span>
      </div>
    </div>
    <div class="feature-card" data-feature-id="feat-002" data-status="planned">
      <div class="feature-header">
        <span class="priority-badge medium">Medium</span>
        <span class="status-label">Planned</span>
      </div>
      <h3 class="feature-title"><a href="/features/feat-002">LoRA Dataset Expansion</a></h3>
      <p class="feature-desc">Expand training dataset to 300+ real-world HTML examples for improved first-pass accuracy.</p>
      <div class="feature-meta">
        <span class="owner">
          <img src="/avatars/eng02.jpg" alt="Bob" class="owner-avatar" />
          Bob Santos
        </span>
        <span class="feature-date">Due: Feb 15, 2024</span>
      </div>
    </div>
  </div>
</div>
```
## Assistant
```vnr
reconstruct "#roadmap-board" -> UiDashboardPage {
    pageTitle: "h1 | text";
    subTitle: "p.roadmap-sub | text";

    child cards {
        selector: "div.feature-card";
        bind title: "h3.feature-title a | text";
        bind url: "h3.feature-title a | attr:href";
        bind description: "p.feature-desc | text";
        bind urlLabel: "span.status-label | text";
    }
}
```

---

# Disqus-style comment section
## User
This HTML is a Disqus-style nested comments thread. Map it to a `UiCommentListPage` with threads including author, date, body, and nested replies:

```html
<div id="disqus_thread" class="dsq-comments">
  <ul class="post-list dsq-comment-list">
    <li class="dsq-post-item" id="post-112233" data-comment-id="112233">
      <div class="dsq-post-header">
        <span class="dsq-avatar">
          <img src="https://disqus.com/api/users/avatars/alice.jpg" alt="alice_dev" />
        </span>
        <div class="dsq-post-user">
          <a href="https://disqus.com/by/alice_dev" class="dsq-user-name">alice_dev</a>
          <span class="dsq-post-date" title="2024-01-18T10:30:00Z">2 hours ago</span>
        </div>
      </div>
      <div class="dsq-post-content">
        <span class="dsq-post-message">This is a really insightful post. The C++ approach makes total sense for performance-critical tooling.</span>
      </div>
      <ul class="dsq-children">
        <li class="dsq-post-item" id="post-112244" data-comment-id="112244">
          <div class="dsq-post-header">
            <span class="dsq-avatar">
              <img src="https://disqus.com/api/users/avatars/bob_coder.jpg" alt="bob_coder" />
            </span>
            <div class="dsq-post-user">
              <a href="https://disqus.com/by/bob_coder" class="dsq-user-name">bob_coder</a>
              <span class="dsq-post-date" title="2024-01-18T11:00:00Z">1 hour ago</span>
            </div>
          </div>
          <div class="dsq-post-content">
            <span class="dsq-post-message">Agreed! Shipping node.js alongside a CLI binary is a major red flag for distribution.</span>
          </div>
        </li>
      </ul>
    </li>
  </ul>
</div>
```
## Assistant
```vnr
reconstruct "#disqus_thread" -> UiCommentListPage {
    pageTitle: "Discussion";
    height: "100vh";

    child threads {
        selector: "ul.post-list > li.dsq-post-item";
        bind id: "self | attr:data-comment-id";
        bind postUser: "a.dsq-user-name | text";
        bind postDate: "span.dsq-post-date | attr:title";

        child comments {
            selector: "ul.dsq-children li.dsq-post-item";
            bind author: "a.dsq-user-name | text";
            bind authorUrl: "a.dsq-user-name | attr:href";
            bind date: "span.dsq-post-date | attr:title";
            bind body: "span.dsq-post-message | text";
        }
    }
}
```

---

# SoundCloud-style track listing
## User
Below is the HTML of a SoundCloud-style track listing page. Map it to a `UiTableListPage` with track name, artist, duration, plays, and likes:

```html
<div id="stream" class="stream sc-list-nostyle">
  <li class="soundList__item sc-border-light-bottom">
    <div class="sound streamContext" data-track-id="1734822110">
      <div class="image sc-media-image">
        <a href="/johndoe/summer-sunset" class="sound__coverArt">
          <img src="https://i1.sndcdn.com/artworks-abc-large.jpg" alt="Summer Sunset" class="image__full" />
        </a>
      </div>
      <div class="sound__content">
        <div class="soundTitle">
          <a href="/johndoe" class="soundTitle__username sc-link-light">John Doe</a>
          <a href="/johndoe/summer-sunset" class="soundTitle__title sc-link-dark">Summer Sunset</a>
        </div>
        <div class="sc-ministats">
          <span class="sc-ministats-item" title="Plays">
            <span class="sc-ministats-count">248,912</span>
          </span>
          <span class="sc-ministats-item" title="Likes">
            <span class="sc-ministats-count">3,401</span>
          </span>
        </div>
        <span class="sc-duration soundBadge__duration">4:32</span>
      </div>
    </div>
  </li>
</div>
```
## Assistant
```vnr
class TrackItem {
    bind title: "a.soundTitle__title | text";
    bind url: "a.soundTitle__title | attr:href";
    bind artist: "a.soundTitle__username | text";
    bind artistUrl: "a.soundTitle__username | attr:href";
    bind coverArt: "img.image__full | attr:src";
    bind plays: "span[title='Plays'] span.sc-ministats-count | text | cleanNumber";
    bind likes: "span[title='Likes'] span.sc-ministats-count | text | cleanNumber";
    bind duration: "span.sc-duration | text";
    bind id: "self | attr:data-track-id";
}

reconstruct "#stream" -> UiTableListPage {
    pageTitle: "Track Stream";
    columns: R"([
      { "key": "title", "header": "Track", "type": "link", "urlKey": "url" },
      { "key": "artist", "header": "Artist", "type": "link", "urlKey": "artistUrl" },
      { "key": "duration", "header": "Duration", "type": "text" },
      { "key": "plays", "header": "Plays", "type": "text" },
      { "key": "likes", "header": "Likes", "type": "text" }
    ])";

    child tableRows extends TrackItem {
        selector: "li.soundList__item";
    }
}
```

---

# Eventbrite-style event listings
## User
This HTML is from an Eventbrite-style event listing page. Map it to a `UiModernGridPage` with event cards showing image, title, date, organizer, location, and price:

```html
<div id="event-search-results" data-testid="search-result-container">
  <ul class="search-results-list" data-automation="event-cards-list">
    <li class="eds-event-card-content eds-event-card-content--standard" data-event-id="845921034847">
      <div class="eds-event-card-content__info-container">
        <div class="eds-event-card-content__image-container">
          <img class="eds-event-card-content__img" src="https://img.evbuc.com/events/845921034847/cover.jpg" alt="AI Summit 2024" />
        </div>
        <div class="eds-event-card-content__content">
          <h3 class="eds-event-card-content__title">
            <a class="eds-event-card-content__title-link" href="/e/ai-summit-2024-tickets-845921034847">AI Summit 2024</a>
          </h3>
          <div class="eds-text-bs eds-text-color--ui-600">
            <p class="eds-event-card-content__sub-title">
              <span class="eds-event-card-content__date">Sat, Feb 10 • 9:00 AM</span>
            </p>
          </div>
          <div class="location-info__address">
            <span class="location-info__address-text">Moscone Center • San Francisco, CA</span>
          </div>
          <div class="eds-event-card-content__footer">
            <div class="eds-event-card-content__organizer">Organized by TechCon Inc.</div>
            <div class="eds-event-card-content__price-container">
              <span class="eds-text-bs eds-text-weight--heavy">$299.00</span>
            </div>
          </div>
        </div>
      </div>
    </li>
  </ul>
</div>
```
## Assistant
```vnr
class EventCard {
    bind title: "h3.eds-event-card-content__title a | text";
    bind url: "h3.eds-event-card-content__title a | attr:href";
    bind imageUrl: "img.eds-event-card-content__img | attr:src";
    bind eventDate: "span.eds-event-card-content__date | text";
    bind location: "span.location-info__address-text | text";
    bind organizer: "div.eds-event-card-content__organizer | text";
    bind price: "span.eds-text-weight--heavy | text | cleanNumber";
    bind id: "self | attr:data-event-id";
}

reconstruct "#event-search-results" -> UiModernGridPage {
    pageTitle: "Events";

    child items extends EventCard {
        selector: "li.eds-event-card-content";
    }
}
```

---

# Glassdoor-style company reviews listing
## User
This HTML is from a Glassdoor-style employer review listing. Write a Veneer Spec to map it to a `UiCommentListPage` with company name, overall rating, pros, cons, and reviewer details as threads:

```html
<div id="ReviewsFeed" data-testid="reviews-feed">
  <ol class="cmp-reviews-list" aria-label="Company Reviews">
    <li class="cmp-review" data-review-id="78901234" itemscope itemtype="https://schema.org/Review">
      <div class="review-header">
        <div class="review-meta">
          <span class="reviewer-title">Senior Software Engineer</span>
          <span class="reviewer-location">Remote</span>
        </div>
        <div class="review-rating-block">
          <span class="review-rating" data-rating="4.0" aria-label="4.0 out of 5">
            <span class="rating-label">4.0</span>
          </span>
          <span class="review-date">Jan 2024</span>
        </div>
      </div>
      <div class="review-body">
        <h2 class="review-headline" itemprop="name">"Great engineering culture, weak management"</h2>
        <div class="review-section pros">
          <h3 class="section-heading">Pros</h3>
          <p class="v2__EIReviewDetailsV2__bodySubdivision" itemprop="reviewBody">
            Remote-first, excellent tooling and autonomy. Engineers are treated as professionals.
          </p>
        </div>
        <div class="review-section cons">
          <h3 class="section-heading">Cons</h3>
          <p class="v2__EIReviewDetailsV2__bodySubdivision">
            Middle management is chaotic and communication from leadership is poor.
          </p>
        </div>
      </div>
    </li>
  </ol>
</div>
```
## Assistant
```vnr
reconstruct "#ReviewsFeed" -> UiCommentListPage {
    pageTitle: "Company Reviews";
    height: "100vh";

    child threads {
        selector: "li.cmp-review";
        bind id: "self | attr:data-review-id";
        bind postUser: "span.reviewer-title | text";
        bind postDate: "span.review-date | text";
        bind postScore: "span.rating-label | text";
        bind postRating: "span.reviewer-location | text";

        child comments {
            selector: "div.review-section";
            bind author: "h3.section-heading | text";
            bind body: "p.v2__EIReviewDetailsV2__bodySubdivision | text";
        }
    }
}
```

---

# WooCommerce-style checkout cart summary
## User
This HTML is from a WooCommerce-style shopping cart summary. Map the cart items to a `UiTableListPage` with product name, quantity, unit price, and subtotal. Hide the legacy totals div:

```html
<div id="woocommerce-cart">
  <table class="shop_table cart woocommerce-cart-form__contents">
    <thead>
      <tr>
        <th class="product-remove"></th>
        <th class="product-thumbnail"></th>
        <th class="product-name">Product</th>
        <th class="product-price">Price</th>
        <th class="product-quantity">Quantity</th>
        <th class="product-subtotal">Subtotal</th>
      </tr>
    </thead>
    <tbody>
      <tr class="woocommerce-cart-form__cart-item cart_item">
        <td class="product-thumbnail">
          <a href="/product/macbook-air-m2"><img src="/images/macbook-air-m2.jpg" alt="MacBook Air M2" /></a>
        </td>
        <td class="product-name" data-title="Product">
          <a href="/product/macbook-air-m2">MacBook Air 13" M2</a>
        </td>
        <td class="product-price" data-title="Price">
          <span class="woocommerce-Price-amount amount"><bdi>R$&nbsp;10.999,00</bdi></span>
        </td>
        <td class="product-quantity" data-title="Quantity">
          <input class="input-text qty text" type="number" value="1" />
        </td>
        <td class="product-subtotal" data-title="Subtotal">
          <span class="woocommerce-Price-amount amount"><bdi>R$&nbsp;10.999,00</bdi></span>
        </td>
      </tr>
    </tbody>
  </table>
  <div class="cart-collaterals" id="legacy-cart-totals">
    <div class="cart_totals">
      <h2>Cart totals</h2>
    </div>
  </div>
</div>
```
## Assistant
```vnr
selector "#legacy-cart-totals" -> UiNavHeader {
    action: hide;
}

reconstruct "#woocommerce-cart" -> UiTableListPage {
    pageTitle: "Your Cart";
    columns: R"([
      { "key": "name", "header": "Product", "type": "link", "urlKey": "url" },
      { "key": "unitPrice", "header": "Unit Price", "type": "currency" },
      { "key": "quantity", "header": "Qty", "type": "text" },
      { "key": "subtotal", "header": "Subtotal", "type": "currency" }
    ])";

    child tableRows {
        selector: "table.cart tbody tr.cart_item";
        bind name: "td.product-name a | text";
        bind url: "td.product-name a | attr:href";
        bind imageUrl: "td.product-thumbnail img | attr:src";
        bind unitPrice: "td.product-price span.woocommerce-Price-amount | text | cleanNumber";
        bind quantity: "td.product-quantity input | attr:value";
        bind subtotal: "td.product-subtotal span.woocommerce-Price-amount | text | cleanNumber";
    }
}
```

---

# Trello-style kanban board
## User
This is the HTML from a Trello-style kanban board with multiple columns. Map the board to a `UiSplitLayout` with a `UiDashboardPage` on the left for backlog and a main reconstruction for "In Progress" tasks:

```html
<div id="board" class="js-board-scrollable-container">
  <div class="board-column" data-list-id="list-backlog">
    <h2 class="list-name">Backlog</h2>
    <ul class="cards-list">
      <li class="card-container" data-card-id="card-001">
        <div class="card js-member-droppable">
          <span class="card-title"><a href="/c/abc123/native-validation">Native Validation Engine</a></span>
          <div class="card-labels">
            <span class="card-label color-green">Backend</span>
            <span class="card-label color-orange">High Priority</span>
          </div>
          <div class="card-footer">
            <span class="due-date icon-clock">Jan 31</span>
          </div>
        </div>
      </li>
      <li class="card-container" data-card-id="card-002">
        <div class="card js-member-droppable">
          <span class="card-title"><a href="/c/def456/dataset-expansion">Dataset Expansion</a></span>
          <div class="card-labels">
            <span class="card-label color-blue">ML</span>
          </div>
        </div>
      </li>
    </ul>
  </div>
</div>
```
## Assistant
```vnr
class KanbanCard {
    bind title: "span.card-title a | text";
    bind url: "span.card-title a | attr:href";
    bind description: "span.due-date | text";
    bind urlLabel: "span.due-date | text";
    bind id: "self | attr:data-card-id";
}

reconstruct "#board" -> UiDashboardPage {
    pageTitle: "h2.list-name | text";

    child cards extends KanbanCard {
        selector: "ul.cards-list li.card-container";
    }
}
```

---

# Coinmarketcap-style crypto price table
## User
This HTML is from a cryptocurrency price listing. Map it to a `UiTableListPage` with rank, name, ticker, price, 24h change, market cap, and volume:

```html
<div id="__next">
  <div class="sc-4c15f6ff-0 kKpPOn cmc-table-homepage">
    <table class="sc-a0353bbc-0 eCgTDP">
      <tbody>
        <tr class="sc-a0353bbc-8 NfFSn" data-row-index="1">
          <td class="sc-a0353bbc-9 iBlefm">1</td>
          <td class="sc-a0353bbc-9 iBlefm">
            <a class="cmc-link" href="/currencies/bitcoin/">
              <img src="https://s2.coinmarketcap.com/static/img/coins/64x64/1.png" alt="BTC" loading="lazy" class="coin-logo" />
              <span>Bitcoin</span>
              <small class="coin-code">BTC</small>
            </a>
          </td>
          <td class="sc-a0353bbc-9 iBlefm price-cell" data-sort="46821.32">$46,821.32</td>
          <td class="sc-a0353bbc-9 iBlefm up">+2.34%</td>
          <td class="sc-a0353bbc-9 iBlefm" data-sort="917210000000">$917.21B</td>
          <td class="sc-a0353bbc-9 iBlefm" data-sort="24187000000">$24.19B</td>
        </tr>
        <tr class="sc-a0353bbc-8 NfFSn" data-row-index="2">
          <td class="sc-a0353bbc-9 iBlefm">2</td>
          <td class="sc-a0353bbc-9 iBlefm">
            <a class="cmc-link" href="/currencies/ethereum/">
              <img src="https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png" alt="ETH" loading="lazy" class="coin-logo" />
              <span>Ethereum</span>
              <small class="coin-code">ETH</small>
            </a>
          </td>
          <td class="sc-a0353bbc-9 iBlefm price-cell" data-sort="2503.18">$2,503.18</td>
          <td class="sc-a0353bbc-9 iBlefm up">+1.87%</td>
          <td class="sc-a0353bbc-9 iBlefm" data-sort="300870000000">$300.87B</td>
          <td class="sc-a0353bbc-9 iBlefm" data-sort="14320000000">$14.32B</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```
## Assistant
```vnr
class CryptoRow {
    bind rank: "td:nth-child(1) | text";
    bind name: "td:nth-child(2) a span | text";
    bind url: "td:nth-child(2) a | attr:href";
    bind ticker: "td:nth-child(2) a small.coin-code | text";
    bind logoUrl: "td:nth-child(2) a img | attr:src";
    bind price: "td.price-cell | attr:data-sort | number";
    bind change24h: "td:nth-child(4) | text";
    bind marketCap: "td:nth-child(5) | text";
    bind volume: "td:nth-child(6) | text";
}

reconstruct "#__next" -> UiTableListPage {
    pageTitle: "Cryptocurrency Prices";
    columns: R"([
      { "key": "rank", "header": "#", "width": "60px", "align": "center" },
      { "key": "name", "header": "Name", "type": "link", "urlKey": "url" },
      { "key": "ticker", "header": "Symbol", "type": "badge", "badgeStyleKey": "ticker" },
      { "key": "price", "header": "Price", "type": "currency" },
      { "key": "change24h", "header": "24h %", "type": "text" },
      { "key": "marketCap", "header": "Market Cap", "type": "text" },
      { "key": "volume", "header": "Volume (24h)", "type": "text" }
    ])";

    child tableRows extends CryptoRow {
        selector: "table tbody tr";
    }
}
```

---

# Yelp-style restaurant listing
## User
This HTML is from a Yelp-style restaurant directory. Write a Veneer Spec to map it to a `UiModernGridPage` with restaurant cards showing image, name, category tags, rating, review count, and price range:

```html
<div class="arrange-unit-fill__09f24__FeNib">
  <ul id="RestaurantSearchResults" class="lemon--ul__373c0__1_cxs undefined undefined undefined undefined">
    <li class="lemon--li__373c0__1r9wz">
      <div class="businessName__373c0__Wm_mS">
        <span class="css-1m051bw"><a href="/biz/the-progress-san-francisco" class="css-19v1rkv">The Progress</a></span>
        <div class="priceCategory__373c0__3dT4H">
          <span class="priceRange__373c0__2rnFy">$$</span>
          <span class="businessCategory__373c0__2f1NK">
            <a href="/category/newamerican">New American</a>,
            <a href="/category/cocktailbars">Cocktail Bars</a>
          </span>
        </div>
      </div>
      <div class="i-stars__373c0__Y7Ir8">
        <div class="lemon--div__373c0__1mboc" aria-label="4.2 star rating">
          <span>4.2</span>
        </div>
        <span class="reviewCount__373c0__1b_Hy">(1,349)</span>
      </div>
      <div class="photoBox__373c0__nyKaP">
        <a href="/biz/the-progress-san-francisco">
          <img src="https://s3-media1.fl.yelpcdn.com/bphoto/progress_main.jpg" alt="The Progress exterior" class="css-xlzvdl" />
        </a>
      </div>
    </li>
  </ul>
</div>
```
## Assistant
```vnr
class RestaurantCard {
    bind name: "span.css-1m051bw a | text";
    bind url: "span.css-1m051bw a | attr:href";
    bind imageUrl: "img.css-xlzvdl | attr:src";
    bind priceRange: "span.priceRange__373c0__2rnFy | text";
    bind rating: "div[aria-label] span | text";
    bind reviewCount: "span.reviewCount__373c0__1b_Hy | text";

    child tags {
        selector: "span.businessCategory__373c0__2f1NK a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}

reconstruct "#RestaurantSearchResults" -> UiModernGridPage {
    pageTitle: "Restaurants";

    child items extends RestaurantCard {
        selector: "ul#RestaurantSearchResults > li";
    }
}
```

---

# Twitter/X-style trending topics sidebar
## User
This HTML is from a Twitter/X-style trending topics sidebar. Map the trending items to a `UiTagCloud` component and hide the legacy sidebar wrapper:

```html
<div id="trending-sidebar" class="r-1awozwy r-1manafd">
  <div class="css-1dbjc4n r-j5o65s r-qklmqi r-1yyt5" data-testid="sidebarColumn">
    <div class="css-1dbjc4n r-1adg3ll">
      <section class="css-1dbjc4n r-kemksi r-1kqtdi0" aria-labelledby="accessible-list-4">
        <h1 id="accessible-list-4">Trends for you</h1>
        <div class="css-1dbjc4n">
          <div class="css-1dbjc4n r-1loqt21 r-18u37iz r-1h3ijdo r-1ny4l3l trending-item" data-testid="trend">
            <div class="css-1dbjc4n r-1kqtdi0 r-1ua0a9z">
              <span class="css-901oao r-1fmj7o5">#RustLang</span>
              <span class="css-901oao r-1fmj7o5 r-1qlqyl8 trending-count">48.2K Tweets</span>
            </div>
            <a href="/search?q=%23RustLang" class="trending-link"></a>
          </div>
          <div class="css-1dbjc4n r-1loqt21 r-18u37iz r-1h3ijdo r-1ny4l3l trending-item" data-testid="trend">
            <div class="css-1dbjc4n r-1kqtdi0 r-1ua0a9z">
              <span class="css-901oao r-1fmj7o5">#OpenSourceAI</span>
              <span class="css-901oao r-1fmj7o5 r-1qlqyl8 trending-count">31.7K Tweets</span>
            </div>
            <a href="/search?q=%23OpenSourceAI" class="trending-link"></a>
          </div>
        </div>
      </section>
    </div>
  </div>
</div>
```
## Assistant
```vnr
selector "#trending-sidebar" -> UiNavSidebar {
    action: replace;

    child navItems {
        selector: "div[data-testid='trend']";
        bind label: "span.r-1fmj7o5:first-child | text";
        bind url: "a.trending-link | attr:href";
        bind description: "span.trending-count | text";
    }
}
```

---

# Figma Community plugin directory
## User
This HTML is from a Figma Community plugin directory listing. Map it to a `UiDashboardPage` with plugin cards showing title, description, creator, installs, and link:

```html
<div id="plugin-listing-container" class="resource_resource__container__6NGRM">
  <div class="resource_resource__container--list__fA9xe">
    <div class="resource_resource__card__ZyoFp" data-plugin-id="plugin-iconify">
      <a href="/community/plugin/735098390272716381" class="resource_resource__card-link__YFSMR">
        <div class="resource_resource__card-preview__lNSSy">
          <img class="resource_resource__preview-image__r5n6e" src="https://figma-plugin-ds.netlify.app/icons/iconify.png" alt="Iconify plugin preview" />
        </div>
        <div class="resource_resource__card-meta__p7Mxh">
          <p class="resource_resource__name__2tRwF">Iconify</p>
          <p class="resource_resource__creator-name__nPb3p">by Vjacheslav Trushkin</p>
          <p class="resource_resource__description__FiPFI">Import icons from all popular icon sets with Iconify</p>
          <div class="resource_resource__stats__HxvPQ">
            <span>2.1M installs</span>
          </div>
        </div>
      </a>
    </div>
    <div class="resource_resource__card__ZyoFp" data-plugin-id="plugin-unsplash">
      <a href="/community/plugin/738454987945972471" class="resource_resource__card-link__YFSMR">
        <div class="resource_resource__card-preview__lNSSy">
          <img class="resource_resource__preview-image__r5n6e" src="https://figma-plugin-ds.netlify.app/icons/unsplash.png" alt="Unsplash plugin preview" />
        </div>
        <div class="resource_resource__card-meta__p7Mxh">
          <p class="resource_resource__name__2tRwF">Unsplash</p>
          <p class="resource_resource__creator-name__nPb3p">by Unsplash</p>
          <p class="resource_resource__description__FiPFI">Insert beautiful images from Unsplash directly into your designs</p>
          <div class="resource_resource__stats__HxvPQ">
            <span>1.8M installs</span>
          </div>
        </div>
      </a>
    </div>
  </div>
</div>
```
## Assistant
```vnr
class FigmaPlugin {
    bind title: "p.resource_resource__name__2tRwF | text";
    bind url: "a.resource_resource__card-link__YFSMR | attr:href";
    bind description: "p.resource_resource__description__FiPFI | text";
    bind urlLabel: "div.resource_resource__stats__HxvPQ span | text";
    bind imageUrl: "img.resource_resource__preview-image__r5n6e | attr:src";
}

reconstruct "#plugin-listing-container" -> UiDashboardPage {
    pageTitle: "Figma Plugins";

    child cards extends FigmaPlugin {
        selector: "div.resource_resource__card__ZyoFp";
    }
}
```

---

# BugReports tracker / issue list
## User
This HTML shows a classic Jira-style bug tracker issue list. Map it to a `UiTableListPage` with issue ID, title, assignee, priority, status, and creation date:

```html
<div id="issuetable" class="issue-table-container">
  <table class="aui issue-table">
    <thead>
      <tr>
        <th class="colHeaderT issuetype"></th>
        <th class="colHeaderT issuekey">T</th>
        <th class="colHeaderT summary">Summary</th>
        <th class="colHeaderT assignee">Assignee</th>
        <th class="colHeaderT priority">P</th>
        <th class="colHeaderT status">Status</th>
        <th class="colHeaderT created">Created</th>
      </tr>
    </thead>
    <tbody class="ui-sortable">
      <tr id="issuerow-12001" rel="12001" data-issue-key="SPM-42" class="issuerow">
        <td class="issuetype"><img src="/images/icons/issuetypes/bug.png" alt="Bug" /></td>
        <td class="issuekey"><a href="/browse/SPM-42" class="issue-link">SPM-42</a></td>
        <td class="summary"><p class="issue-link"><a href="/browse/SPM-42">validate.js fails on deeply nested DOMs</a></p></td>
        <td class="assignee"><a href="/user/alice">Alice Chen</a></td>
        <td class="priority"><img src="/images/icons/priorities/high.png" alt="High" /></td>
        <td class="status"><span class="aui-lozenge aui-lozenge-error">Open</span></td>
        <td class="created"><time class="date user-tz" datetime="2024-01-15">Jan 15, 2024</time></td>
      </tr>
      <tr id="issuerow-12002" rel="12002" data-issue-key="SPM-43" class="issuerow">
        <td class="issuetype"><img src="/images/icons/issuetypes/improvement.png" alt="Improvement" /></td>
        <td class="issuekey"><a href="/browse/SPM-43" class="issue-link">SPM-43</a></td>
        <td class="summary"><p class="issue-link"><a href="/browse/SPM-43">Add cleanNumber pipe to support BRL locale</a></p></td>
        <td class="assignee"><a href="/user/bob">Bob Santos</a></td>
        <td class="priority"><img src="/images/icons/priorities/medium.png" alt="Medium" /></td>
        <td class="status"><span class="aui-lozenge aui-lozenge-success">In Progress</span></td>
        <td class="created"><time class="date user-tz" datetime="2024-01-16">Jan 16, 2024</time></td>
      </tr>
    </tbody>
  </table>
</div>
```
## Assistant
```vnr
class IssueRow {
    bind issueKey: "td.issuekey a | text";
    bind url: "td.issuekey a | attr:href";
    bind title: "td.summary a | text";
    bind assignee: "td.assignee a | text";
    bind assigneeUrl: "td.assignee a | attr:href";
    bind priority: "td.priority img | attr:alt";
    bind status: "td.status span | text";
    bind statusKey: "td.status span | attr:class";
    bind createdDate: "td.created time | attr:datetime";
}

reconstruct "#issuetable" -> UiTableListPage {
    pageTitle: "Issue Tracker";
    columns: R"([
      { "key": "issueKey", "header": "Key", "type": "link", "urlKey": "url", "width": "90px" },
      { "key": "title", "header": "Summary", "type": "text" },
      { "key": "assignee", "header": "Assignee", "type": "link", "urlKey": "assigneeUrl" },
      { "key": "priority", "header": "Priority", "type": "badge", "badgeStyleKey": "priority" },
      { "key": "status", "header": "Status", "type": "badge", "badgeStyleKey": "statusKey" },
      { "key": "createdDate", "header": "Created", "type": "date" }
    ])";

    child tableRows extends IssueRow {
        selector: "table.issue-table tbody tr.issuerow";
    }
}
```

---

# Kaggle-style competition listing
## User
This HTML is from a Kaggle-style data science competition listing. Map it to a `UiTableListPage` with competition name, category, prize, deadline, and team count:

```html
<div class="sc-bwzfXH iSAVrt competitions-list" id="competitions-list">
  <div class="sc-AxjAm gfoLXb competition-list-item" data-competition-slug="titanic">
    <div class="sc-fzoXzr iFfrxW competition-thumbnail">
      <img src="https://storage.googleapis.com/kaggle-competitions/kaggle/3136/logos/header.png" alt="Titanic: ML from Disaster" />
    </div>
    <div class="sc-fzoiuh fIBnXE competition-meta">
      <a href="/c/titanic" class="competition-title">Titanic – Machine Learning from Disaster</a>
      <div class="sc-fznxsB lhRyqj competition-categories">
        <span class="sc-fznMVU category-tag">Getting Started</span>
        <span class="sc-fznMVU category-tag">Binary Classification</span>
      </div>
      <div class="sc-fznWqX eDcSgj competition-stats">
        <span class="prize">No Prize</span>
        <span class="deadline" data-deadline="2030-01-01T00:00:00Z">Ends Jan 1, 2030</span>
        <span class="teams">15,342 teams</span>
      </div>
    </div>
  </div>
  <div class="sc-AxjAm gfoLXb competition-list-item" data-competition-slug="playground-series-s4e1">
    <div class="sc-fzoXzr iFfrxW competition-thumbnail">
      <img src="https://storage.googleapis.com/kaggle-competitions/kaggle/60978/logos/header.png" alt="Playground Series - Season 4" />
    </div>
    <div class="sc-fzoiuh fIBnXE competition-meta">
      <a href="/c/playground-series-s4e1" class="competition-title">Playground Series – Season 4, Episode 1</a>
      <div class="sc-fznxsB lhRyqj competition-categories">
        <span class="sc-fznMVU category-tag">Tabular</span>
        <span class="sc-fznMVU category-tag">Regression</span>
      </div>
      <div class="sc-fznWqX eDcSgj competition-stats">
        <span class="prize">Prizes</span>
        <span class="deadline" data-deadline="2024-01-31T00:00:00Z">Ends Jan 31, 2024</span>
        <span class="teams">3,201 teams</span>
      </div>
    </div>
  </div>
</div>
```
## Assistant
```vnr
class CompetitionItem {
    bind name: "a.competition-title | text";
    bind url: "a.competition-title | attr:href";
    bind thumbnailUrl: "img | attr:src";
    bind prize: "span.prize | text";
    bind deadline: "span.deadline | attr:data-deadline";
    bind teams: "span.teams | text";
    bind slug: "self | attr:data-competition-slug";

    child tags {
        selector: "span.sc-fznMVU.category-tag";
        bind label: "self | text";
    }
}

reconstruct "#competitions-list" -> UiTableListPage {
    pageTitle: "Competitions";
    columns: R"([
      { "key": "name", "header": "Competition", "type": "link", "urlKey": "url" },
      { "key": "prize", "header": "Prize", "type": "badge", "badgeStyleKey": "prize" },
      { "key": "deadline", "header": "Deadline", "type": "date" },
      { "key": "teams", "header": "Teams", "type": "text" }
    ])";

    child tableRows extends CompetitionItem {
        selector: "div.competition-list-item";
    }
}
```

---

# WordPress blog index with comments
## User
This HTML is a typical WordPress blog index page. Replace the site header, map the post list to `UiModernGridPage`, and hide the legacy sidebar:

```html
<header id="site-header" class="site-header sticky-header">
  <div class="site-branding">
    <a href="/" class="site-logo-link">
      <img src="/wp-content/uploads/logo.png" alt="Tech Musings" class="site-logo" />
    </a>
    <h1 class="site-title"><a href="/">Tech Musings</a></h1>
  </div>
  <nav id="primary-menu" class="primary-navigation">
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/about">About</a></li>
      <li><a href="/category/tech">Tech</a></li>
      <li><a href="/category/ai">AI</a></li>
    </ul>
  </nav>
</header>

<main id="main-content">
  <div id="archive-grid" class="post-grid">
    <article class="post type-post status-publish format-standard hentry category-tech" id="post-881">
      <div class="post-thumbnail">
        <a href="/2024/01/native-cpp-deep-dive"><img src="/wp-content/uploads/2024/01/cpp-header.jpg" alt="C++ Header Image" /></a>
      </div>
      <header class="entry-header">
        <h2 class="entry-title"><a href="/2024/01/native-cpp-deep-dive">Deep Dive: Native C++ CLI Tools</a></h2>
        <div class="entry-meta">
          <span class="posted-on"><time class="entry-date published" datetime="2024-01-18">January 18, 2024</time></span>
          <span class="byline"> by <a href="/author/alice" class="author-link">Alice</a></span>
          <span class="comments-link"><a href="/2024/01/native-cpp-deep-dive#comments">14 comments</a></span>
        </div>
      </header>
      <div class="entry-summary"><p>This week I explored replacing scripting dependencies in CLI tools with native implementations...</p></div>
    </article>
    <article class="post type-post status-publish format-standard hentry category-ai" id="post-882">
      <div class="post-thumbnail">
        <a href="/2024/01/lora-fine-tuning"><img src="/wp-content/uploads/2024/01/lora-header.jpg" alt="LoRA Fine-tuning" /></a>
      </div>
      <header class="entry-header">
        <h2 class="entry-title"><a href="/2024/01/lora-fine-tuning">LoRA Fine-Tuning Demystified</a></h2>
        <div class="entry-meta">
          <span class="posted-on"><time class="entry-date published" datetime="2024-01-15">January 15, 2024</time></span>
          <span class="byline"> by <a href="/author/bob" class="author-link">Bob</a></span>
          <span class="comments-link"><a href="/2024/01/lora-fine-tuning#comments">9 comments</a></span>
        </div>
      </header>
      <div class="entry-summary"><p>LoRA adapters offer an efficient path to fine-tuning large language models without full gradient updates...</p></div>
    </article>
  </div>
</main>

<aside id="secondary" class="widget-area sidebar">
  <section class="widget widget_recent_posts">
    <h2 class="widget-title">Recent Posts</h2>
  </section>
</aside>
```
## Assistant
```vnr
selector "#site-header" -> UiNavHeader {
    action: replace;
    sticky: true;
    siteName: "h1.site-title a | text";

    bind logoUrl: "img.site-logo | attr:src";
    logoHref: "/";

    child primaryLinks {
        selector: "nav#primary-menu ul li a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}

selector "#secondary" -> UiNavHeader {
    action: hide;
}

class WpPost {
    bind title: "h2.entry-title a | text";
    bind url: "h2.entry-title a | attr:href";
    bind imageUrl: "div.post-thumbnail img | attr:src";
    bind publishDate: "time.entry-date | attr:datetime";
    bind author: "a.author-link | text";
    bind authorUrl: "a.author-link | attr:href";
    bind excerpt: "div.entry-summary p | text";
    bind id: "self | attr:id";
}

reconstruct "#archive-grid" -> UiModernGridPage {
    pageTitle: "Latest Posts";

    child items extends WpPost {
        selector: "article.post";
    }
}
```

---

# Stripe dashboard transactions table
## User
This HTML represents a Stripe-style payment transactions table inside an admin dashboard. Map transactions to a `UiTableListPage` and the top navigation to `UiNavHeader`. Hide the legacy breadcrumb bar:

```html
<header id="dashboard-nav" class="db-nav-bar">
  <div class="brand">
    <img src="/assets/stripe-logo.svg" alt="Stripe" />
  </div>
  <nav class="main-links">
    <a href="/dashboard">Dashboard</a>
    <a href="/payments">Payments</a>
    <a href="/customers">Customers</a>
    <a href="/products">Products</a>
    <a href="/reports">Reports</a>
  </nav>
</header>

<div id="breadcrumb-bar" class="legacy-crumb-nav">
  <a href="/payments">Payments</a> / All Transactions
</div>

<div id="transactions-table-wrapper" class="db-card db-card--no-pad">
  <table class="db-table" data-table-id="transactions">
    <thead>
      <tr>
        <th>ID</th>
        <th>Amount</th>
        <th>Currency</th>
        <th>Status</th>
        <th>Customer</th>
        <th>Date</th>
      </tr>
    </thead>
    <tbody>
      <tr class="db-row" data-txn-id="pi_3OaGQCLP2UuV6cIu0abcdefg">
        <td class="db-cell"><a href="/payments/pi_3OaGQCLP2UuV6cIu0abcdefg">pi_3OaGQCLP2UuV6cIu0abcdefg</a></td>
        <td class="db-cell amount-cell" data-amount="99900">$999.00</td>
        <td class="db-cell">USD</td>
        <td class="db-cell"><span class="badge badge--success">Succeeded</span></td>
        <td class="db-cell"><a href="/customers/cus_PaBXjkL3mN">john.doe@example.com</a></td>
        <td class="db-cell"><time datetime="2024-01-18T14:32:00Z">Jan 18, 2024</time></td>
      </tr>
      <tr class="db-row" data-txn-id="pi_3OaHFGLP2UuV6cIu0xyz9876">
        <td class="db-cell"><a href="/payments/pi_3OaHFGLP2UuV6cIu0xyz9876">pi_3OaHFGLP2UuV6cIu0xyz9876</a></td>
        <td class="db-cell amount-cell" data-amount="4900">$49.00</td>
        <td class="db-cell">USD</td>
        <td class="db-cell"><span class="badge badge--warning">Pending</span></td>
        <td class="db-cell"><a href="/customers/cus_QcCYklM4nP">jane.smith@company.io</a></td>
        <td class="db-cell"><time datetime="2024-01-18T09:15:00Z">Jan 18, 2024</time></td>
      </tr>
    </tbody>
  </table>
</div>
```
## Assistant
```vnr
selector "#dashboard-nav" -> UiNavHeader {
    action: replace;
    sticky: true;

    bind logoUrl: "div.brand img | attr:src";
    logoHref: "/dashboard";

    child primaryLinks {
        selector: "nav.main-links a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}

selector "#breadcrumb-bar" -> UiNavHeader {
    action: hide;
}

class TransactionRow {
    bind txnId: "td:nth-child(1) a | text";
    bind url: "td:nth-child(1) a | attr:href";
    bind amount: "td.amount-cell | attr:data-amount | number";
    bind currency: "td:nth-child(3) | text";
    bind status: "td:nth-child(4) span | text";
    bind statusKey: "td:nth-child(4) span | attr:class";
    bind customer: "td:nth-child(5) a | text";
    bind customerUrl: "td:nth-child(5) a | attr:href";
    bind date: "td:nth-child(6) time | attr:datetime";
    bind id: "self | attr:data-txn-id";
}

reconstruct "#transactions-table-wrapper" -> UiTableListPage {
    pageTitle: "Transactions";
    columns: R"([
      { "key": "txnId", "header": "Payment ID", "type": "link", "urlKey": "url" },
      { "key": "amount", "header": "Amount", "type": "currency" },
      { "key": "currency", "header": "Currency", "type": "text" },
      { "key": "status", "header": "Status", "type": "badge", "badgeStyleKey": "statusKey" },
      { "key": "customer", "header": "Customer", "type": "link", "urlKey": "customerUrl" },
      { "key": "date", "header": "Date", "type": "date" }
    ])";

    child tableRows extends TransactionRow {
        selector: "table tbody tr.db-row";
    }
}
```

# Multi-slot preserve block mapping
## User
Based on the following forum layout HTML, write a reconstruct block targeting `#discussion-thread` that mounts a `UiPostDetails` component and preserves both the reply form and the user profile widget into named slots:

```html
<div id="discussion-thread">
  <div class="legacy-post-meta">
    <h1>Thread Title</h1>
  </div>
  <aside id="member-card-widget">
    <h3>Author Profile</h3>
    <p>User stats...</p>
  </aside>
  <div class="legacy-content">
    Post body content...
  </div>
  <form id="legacy-comment-editor" action="/submit-comment">
    <textarea name="comment"></textarea>
    <button>Submit</button>
  </form>
</div>
```
## Assistant
Here is the Veneer Spec (.vnr) code to reconstruct the discussion area while preserving interactive legacy inputs:

```vnr
reconstruct "#discussion-thread" -> UiPostDetails {
    pageTitle: "Discussion Thread";
    
    preserve {
        commentFormSlot: "#legacy-comment-editor";
        profileCardSlot: "#member-card-widget";
    }
}
```

# String delimiter splitting using the split pipe
## User
Write a Veneer Spec (.vnr) to map a gallery item row where the tag list is extracted from a space-separated data attribute:

```html
<div class="gallery-item" data-tags="scenery wallpaper clouds sky green_grass">
  <a class="preview-link" href="/view/100492">
    <img src="/thumbs/100492.jpg" alt="Preview" />
  </a>
</div>
```
## Assistant
You can extract space-separated data tags into a JSON array using the `split` pipe operation. The default behavior of `split` without arguments splits by space:

```vnr
class GalleryCard {
    bind tags: "self | attr:data-tags | split";
    bind viewUrl: "a.preview-link | attr:href";
    bind imageUrl: "img | attr:src";
}

reconstruct ".gallery-item-container" -> UiModernGridPage {
    pageTitle: "Wallpaper Gallery";
    
    child items extends GalleryCard {
        selector: ".gallery-item";
    }
}
```

# Using split with a custom delimiter
## User
Write a VNR class mapping a row where category hierarchies are joined by ` > ` characters in a breadcrumb link:

```html
<div class="breadcrumb-trail">
  <span class="hierarchy">Home > Hardware > Storage > Solid State Drives</span>
</div>
```
## Assistant
You can specify a custom delimiter by passing arguments to the `split` pipe, like `split:' > '`:

```vnr
class CategoryBreadcrumb {
    bind pathSegments: "span.hierarchy | text | split:' > '";
}
```

# Numeric conversions with number and cleanNumber
## User
I have the following item metadata HTML:
```html
<div class="meta-row">
  <span class="item-count">Count: 42 items</span>
  <span class="item-rating">Rating: 4.85 stars</span>
  <span class="item-price">$ 2,450.99</span>
</div>
```
Write VNR bindings that convert these fields to clean numbers.
## Assistant
You can parse digits and float values from text segments containing extra characters using the `number` and `cleanNumber` extractor pipes:

```vnr
class MetadataCard {
    bind count: "span.item-count | text | number";
    bind rating: "span.item-rating | text | number";
    bind price: "span.item-price | text | cleanNumber";
}
```

# Hierarchical scoping with document scope
## User
Write a `.vnr` spec to replace a sidebar widget with `UiStatsDashboard`. It must grab the user's login name from a top-bar user menu that resides outside the sidebar wrapper.

```html
<div id="top-bar">
  <span class="user-name-display">admin_user</span>
</div>
<aside id="legacy-sidebar">
  <div class="widget-box">
    <h3>Legacy Widget</h3>
    <p>Values...</p>
  </div>
</aside>
```
## Assistant
By default, bindings look inside the matched container block. To fetch properties from elements physically outside the matched container, use `scope: "document";`:

```vnr
selector "#legacy-sidebar" -> UiStatsDashboard {
    action: replace;
    
    bind currentUser: {
        scope: "document";
        selector: "#top-bar span.user-name-display | text";
    }
}
```

# URL routing regex configurations
## User
How do I configure a reconstruct block to only trigger on gallery pages with specific numeric URL path matches? Show an example VNR.
## Assistant
You can constrain a `reconstruct` block to trigger only on pages matching a specific URL regex pattern using the `urlPattern` property and a C++ raw string literal to avoid backslash escape overhead:

```vnr
reconstruct "#gallery-feed-wrapper" -> UiModernGridPage {
    urlPattern: R"(\/gallery\/\d+)";
    pageTitle: "Image Gallery Feed";
    
    child items {
        selector: ".thumbnail-card";
        bind imageUrl: "img | attr:src";
    }
}
```

# Reconstructing a tabular admin dashboard
## User
Map the following table grid structure into a VNR spec targeting `UiTableListPage`:

```html
<table class="data-table">
  <thead>
    <tr><th>User</th><th>Role</th><th>Activity</th></tr>
  </thead>
  <tbody>
    <tr class="user-record">
      <td><a class="username" href="/user/alice">Alice Smith</a></td>
      <td><span class="label">Developer</span></td>
      <td><time datetime="2026-08-21T12:00:00Z">Active</time></td>
    </tr>
  </tbody>
</table>
```
## Assistant
Here is the `.vnr` code to reconstruct the HTML data-table into a React-based `UiTableListPage`:

```vnr
class UserRow {
    bind name: "a.username | text";
    bind profileUrl: "a.username | attr:href";
    bind role: "span.label | text";
    bind lastSeen: "time | attr:datetime";
}

reconstruct "table.data-table" -> UiTableListPage {
    pageTitle: "User Accounts Directory";
    
    child tableRows extends UserRow {
        selector: "tr.user-record";
    }
}
```

# In-place widget replacements
## User
Write VNR code to replace a legacy video sidebar box with a `UiImageViewer` component, binding the image source from an attributes placeholder:

```html
<div class="video-preview-widget" data-video-id="9202" data-poster-url="/covers/9202.png">
  <div class="play-icon">Play Video</div>
</div>
```
## Assistant
You can perform in-place replacements using `selector` blocks with `action: replace;`:

```vnr
selector ".video-preview-widget" -> UiImageViewer {
    action: replace;
    imageSrc: "self | attr:data-poster-url";
    videoId: "self | attr:data-video-id | number";
}
```

# Setting up theme design tokens
## User
Write a complete VNR theme declaration setting up dark-mode variables and global overrides:
## Assistant
Use a `theme` block with nested `variables` and `customStyles` blocks:

```vnr
theme "ThemeDarkDefault" {
    variables {
        --spm-bg-primary: "#0b0c10";
        --spm-bg-secondary: "#1f2833";
        --spm-accent: "#66fcf1";
        --spm-text-primary: "#c5c6c7";
    }
    customStyles {
        "body { font-family: 'Inter', sans-serif !important; }"
        ".ad-space { display: none !important; }"
    }
}
```

# Complex child class inheritance mapping
## User
Write a VNR spec where two different classes extend a common `BaseItem` to map listing properties:
## Assistant
Use the `extends` keyword in your class declarations:

```vnr
class BaseItem {
    bind id: "self | attr:data-item-id | number";
    bind title: "a.title-link | text";
    bind url: "a.title-link | attr:href";
}

class ClassifiedItem extends BaseItem {
    bind price: ".price-tag | text | cleanNumber";
    bind location: ".location | text";
}

class JobItem extends BaseItem {
    bind company: ".company-name | text";
    bind remote: ".remote-tag | text";
}
```

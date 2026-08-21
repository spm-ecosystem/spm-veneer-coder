# Two-level class inheritance chain resolution
## User
Based on this audit log markup, write a `.vnr` reconstruct targeting `UiTableListPage` that uses a three-level class inheritance chain (`Interactive` → `Clickable` → `TrackedClickable`) to map each row's link:

```html
<table class="audit-table">
  <tbody>
    <tr class="audit-row">
      <td><a class="audit-link" href="/audit/901" data-track-id="trk-901">View #901</a></td>
    </tr>
  </tbody>
</table>
```
## Assistant
When classes extend each other across multiple levels, the resolver merges every ancestor's bindings into the final class:

```vnr
class Interactive {
    bind isDisabled: "self | attr:disabled";
}

class Clickable extends Interactive {
    bind url: "self | attr:href";
}

class TrackedClickable extends Clickable {
    bind trackingId: "self | attr:data-track-id";
}

reconstruct ".audit-table" -> UiTableListPage {
    pageTitle: "Audit Log";
    columns: R"([
      { "key": "isDisabled", "header": "Disabled", "type": "checkbox" },
      { "key": "url", "header": "Link URL", "type": "link", "urlKey": "url" },
      { "key": "trackingId", "header": "Track ID", "type": "text" }
    ])";
    
    child tableRows extends TrackedClickable {
        selector: "tr.audit-row a.audit-link";
    }
}
```

---

# Overriding a parent class binding for lazy-loaded images
## User
Write VNR classes for this deal card, where the real image lives in `data-src` instead of `src` because it's lazy-loaded:

```html
<div class="deal-card" id="deal-1">
  <span class="title">Weekend Flash Sale</span>
  <img data-src="/img/deals/flash-sale.jpg" src="/img/placeholder.png" />
  <a class="buy-link" href="/buy/1">Buy Now</a>
</div>
```
## Assistant
Declare a generic base class first, then extend it with a specialized class that overrides just the `imageUrl` binding:

```vnr
class GenericCard {
    bind title: ".title | text";
    bind imageUrl: "img | attr:src";
    bind linkUrl: "a.buy-link | attr:href";
    bind id: "self | attr:id";
}

class LazyLoadedCard extends GenericCard {
    bind imageUrl: "img | attr:data-src";
}

reconstruct "#deals-feed" -> UiModernGridPage {
    pageTitle: "Flash Deals";
    
    child items extends LazyLoadedCard {
        selector: ".deal-card";
    }
}
```

---

# Class used purely for document scope, extended elsewhere
## User
This legal center page has its footer links physically outside the main container. Map both into `UiSplitLayout`, reusing a document-scoped link class:

```html
<div id="policy-hub">
  <h1 class="hub-title">Legal Center</h1>
</div>
<footer id="site-footer">
  <a class="legal-link" href="/privacy">Privacy Policy</a>
  <a class="legal-link" href="/terms">Terms of Service</a>
</footer>
```
## Assistant
Declare a base link class, then a thin subclass that adds `scope: "document";` so any `child` that extends the subclass automatically inherits document-wide scoping:

```vnr
class BaseLink {
    bind label: "self | text";
    bind url: "self | attr:href";
}

class DocumentScopedLink extends BaseLink {
    scope: "document";
}

reconstruct "#policy-hub" -> UiSplitLayout {
    sidebarWidth: "280px";
    sidebarSide: "right";
    bind mainHtml: "h1.hub-title | html";
    
    child buttons extends DocumentScopedLink {
        selector: "#site-footer a.legal-link";
    }
}
```

---

# Sibling classes with a consistent shape but no inheritance
## User
I have two different podcast-participant blocks with almost identical fields, but slightly different selectors. Should I use inheritance, or just declare them separately?
## Assistant
When the field shapes only coincidentally overlap rather than representing a true "is-a" relationship, it's usually clearer to declare independent sibling classes rather than forcing an `extends` relationship between them:

```vnr
class EpisodeHost {
    bind name: ".host-name | text";
    bind avatarUrl: ".host-avatar img | attr:src";
    bind bio: ".host-bio | text";
}

class EpisodeGuest {
    bind name: ".guest-name | text";
    bind avatarUrl: ".guest-avatar img | attr:src";
    bind bio: ".guest-bio | text";
    bind episodeCount: ".guest-stats .episodes | text | number";
}
```

---

# Circular inheritance compile error
## User
Why does this fail to compile?

```vnr
class A extends B {
    bind x: "self | text";
}

class B extends A {
    bind y: "self | text";
}
```
## Assistant
The resolver detects this as circular inheritance (`A -> B -> A`) while building the ancestry graph and fails at compile time. Break the cycle by having both extend a shared, non-circular base instead:

```vnr
class Base {
    bind x: "self | text";
    bind y: "self | text";
}

class A extends Base {
    bind extraA: "self | attr:data-a";
}

class B extends Base {
    bind extraB: "self | attr:data-b";
}
```

---

# Referencing an undeclared class error
## User
Why does this fail?

```vnr
class Derived extends MissingBase {
    bind extra: "self | attr:data-extra";
}
```
## Assistant
The problem: `MissingBase` is never declared. Declare the missing base class in your workspace files:

```vnr
class MissingBase {
    bind z: "self | text";
}

class Derived extends MissingBase {
    bind extra: "self | attr:data-extra";
}
```

---

# Forgetting the required action key on a selector block
## User
Why does this fail to compile?

```vnr
selector "#promo-ribbon" -> UiTagBadge {
    label: "Limited Time";
}
```
## Assistant
Every `selector` block requires an `action` key (`hide` or `replace`) so the compiler knows whether to just hide the legacy element or mount a component in its place:

```vnr
selector "#promo-ribbon" -> UiTagBadge {
    action: replace;
    bind label: "self | text";
}
```

---

# Using child outside of a selector or reconstruct block
## User
Why does this fail to compile?

```vnr
child orphanList {
    selector: ".x";
}
```
## Assistant
The `child` block is only valid when nested inside a `selector` or `reconstruct` block:

```vnr
reconstruct "#page" -> UiModernGridPage {
    child items -> UiImageCard {
        selector: ".x";
        bind imageUrl: "img | attr:src";
        bind linkUrl: "a | attr:href";
        bind title: "a | text";
        bind id: "self | attr:id";
    }
}
```

---

# Typo'd base extractor name
## User
Why does this fail to compile?

```vnr
bind title: "h2 | txt";
```
## Assistant
Veneer Spec only recognizes the seven documented base extractors (`text`, `html`, `attr:<name>`, `hrefOrOnclick`, `nextSiblingText`, `hiddenInputs`, `selector`), so any other name fails to compile:

```vnr
bind title: "h2 | text";
```

---

# Duplicate child name at the same nesting level
## User
Why does this fail?

```vnr
reconstruct "#page" -> UiNavHeader {
    siteName: "Site";
    
    child primaryLinks {
        selector: ".a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
    child primaryLinks {
        selector: ".b";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```
## Assistant
Two `child` blocks share the same name `primaryLinks` under the same parent. Give each child block a distinct prop name:

```vnr
reconstruct "#page" -> UiNavHeader {
    siteName: "Site";
    
    child primaryLinks {
        selector: ".a";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
    child secondaryLinks {
        selector: ".b";
        bind label: "self | text";
        bind url: "self | attr:href";
    }
}
```

---

# Raw string delimiter collision in a urlPattern regex
## User
Why does this `urlPattern` fail to compile correctly?

```vnr
urlPattern: R"(\)")";
```
## Assistant
The regex content contains the default raw-string terminator sequence `)"`, closing the literal early. Use a custom tag delimiter:

```vnr
urlPattern: R"tag(\)")tag";
```

---

# Silent runtime failure from a mismatched preserve slot name
## User
My `preserve` block compiled without any errors, but the legacy chat widget just disappeared. What went wrong?

```vnr
reconstruct "#support-center" -> UiSplitLayout {
    sidebarWidth: "280px";
    sidebarSide: "right";
    
    preserve {
        liveChatSlot: "#zendesk-chat-widget";
    }
}
```
## Assistant
This is a runtime layout matching issue. At runtime, the layout looks for a slot element with a matching name inside `UiSplitLayout` to reparent the preserved node into. If that container doesn't exist in the React component code, the legacy node is removed from its original spot but is never reattached.

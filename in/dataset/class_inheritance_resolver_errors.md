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
When classes extend each other across multiple levels, the resolver walks the whole chain and merges every ancestor's bindings into the final class — `TrackedClickable` here ends up with `isDisabled`, `url`, and `trackingId` all merged together:

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
    
    child tableRows extends TrackedClickable {
        selector: "tr.audit-row a.audit-link";
    }
}
```

# Overriding a parent class binding for lazy-loaded images
## User
Write VNR classes for this deal card, where the real image lives in `data-src` instead of `src` because it's lazy-loaded:

```html
<div class="deal-card">
  <span class="title">Weekend Flash Sale</span>
  <img data-src="/img/deals/flash-sale.jpg" src="/img/placeholder.png" />
</div>
```
## Assistant
Declare a generic base class first, then extend it with a specialized class that overrides just the `image` binding — the child class's declaration wins over the parent's when both define the same property:

```vnr
class GenericCard {
    bind title: ".title | text";
    bind image: "img | attr:src";
}

class LazyLoadedCard extends GenericCard {
    bind image: "img | attr:data-src";
}

reconstruct "#deals-feed" -> UiModernGridPage {
    pageTitle: "Flash Deals";
    
    child items extends LazyLoadedCard {
        selector: ".deal-card";
    }
}
```

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
Declare a base link class, then a thin subclass that only adds `scope: "document";` — any `child` that extends the subclass automatically inherits document-wide scoping without repeating it:

```vnr
class BaseLink {
    bind label: "self | text";
    bind url: "self | attr:href";
}

class DocumentScopedLink extends BaseLink {
    scope: "document";
}

reconstruct "#policy-hub" -> UiSplitLayout {
    pageTitle: "Legal Center";
    bind headline: "h1.hub-title | text";
    
    child legalLinks extends DocumentScopedLink {
        selector: "#site-footer a.legal-link";
    }
}
```

# Sibling classes with a consistent shape but no inheritance
## User
I have two different podcast-participant blocks with almost identical fields, but slightly different selectors and one extra field on the guest. Should I use inheritance, or just declare them separately?
## Assistant
When the field shapes only coincidentally overlap rather than representing a true "is-a" relationship, it's usually clearer to declare independent sibling classes rather than forcing an `extends` relationship between them — inheritance is for genuine specialization, not just for avoiding a bit of duplication:

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
The problem: `A` extends `B`, and `B` extends `A` — the resolver detects this as circular inheritance (`A -> B -> A`) while building the ancestry graph, which it can never fully resolve, so it fails at compile time. Break the cycle by having both extend a shared, non-circular base instead:

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

# Referencing an undeclared class error
## User
Why does this fail?

```vnr
class Derived extends MissingBase {
    bind extra: "self | attr:data-extra";
}
```
## Assistant
The problem: `MissingBase` is never declared anywhere the compiler can find it — in single-file linter mode it must live in the same file or a sibling file in the same directory; in a full workspace compile it must be declared somewhere in the compiled tree. Declare the missing base class before (or after — order doesn't matter in a full compile) the class that extends it:

```vnr
class MissingBase {
    bind z: "self | text";
}

class Derived extends MissingBase {
    bind extra: "self | attr:data-extra";
}
```

# Forgetting the required action key on a selector block
## User
Why does this fail to compile?

```vnr
selector "#promo-ribbon" -> UiTagBadge {
    label: "Limited Time";
}
```
## Assistant
The problem: every `selector` block requires an `action` key (`hide` or `replace`) — without it, the compiler doesn't know whether to just hide the legacy element or mount a component in its place. Add the missing key:

```vnr
selector "#promo-ribbon" -> UiTagBadge {
    action: replace;
    label: "Limited Time";
}
```

# Using child outside of a selector or reconstruct block
## User
Why does this fail to compile?

```vnr
child orphanList {
    selector: ".x";
}
```
## Assistant
The problem: `child` is only valid when nested inside a `selector` or `reconstruct` block — it has no meaning at the top level of a file, since it needs a parent component to attach its resulting array prop to. Nest it inside a block that mounts a component:

```vnr
reconstruct "#page" -> UiGridPage {
    child orphanList {
        selector: ".x";
    }
}
```

# Typo'd base extractor name
## User
Why does this fail to compile?

```vnr
bind title: "h2 | txt";
```
## Assistant
The problem: `txt` is not a recognized base extractor — the correct name is `text`. Veneer Spec only recognizes the seven documented base extractors (`text`, `html`, `attr:<name>`, `hrefOrOnclick`, `nextSiblingText`, `hiddenInputs`, `selector`), so any other name fails to compile:

```vnr
bind title: "h2 | text";
```

# Duplicate child name at the same nesting level
## User
Why does this fail?

```vnr
reconstruct "#page" -> UiDashboardPage {
    child items {
        selector: ".a";
    }
    child items {
        selector: ".b";
    }
}
```
## Assistant
The problem: two `child` blocks share the name `items` at the same nesting level under the same parent, which creates a naming conflict — each child list needs a distinct prop name so the resolver knows which array each one maps to. Give each list its own name:

```vnr
reconstruct "#page" -> UiDashboardPage {
    child primaryItems {
        selector: ".a";
    }
    child secondaryItems {
        selector: ".b";
    }
}
```

# Raw string delimiter collision in a urlPattern regex
## User
Why does this `urlPattern` fail to compile correctly?

```vnr
urlPattern: R"(\)")";
```
## Assistant
The problem: the regex content itself contains the default raw-string terminator sequence `)"`, which closes the literal early and leaves trailing garbage the parser can't make sense of. Use a custom delimiter so the closing sequence becomes unambiguous:

```vnr
urlPattern: R"tag(\)")tag";
```

# Silent runtime failure from a mismatched preserve slot name
## User
My `preserve` block compiled without any errors, but the legacy chat widget just disappeared — it never reappeared anywhere on the page. What went wrong?

```vnr
reconstruct "#support-center" -> UiItemDetailsPage {
    preserve {
        liveChatSlot: "#zendesk-chat-widget";
    }
}
```
## Assistant
This is a runtime issue, not a compile error — the compiler has no way to check `preserve` slot names against the target component's actual internals. At runtime, the layout looks for a host element with `id="liveChatSlot-container"` inside `UiItemDetailsPage` to reparent the preserved node into; if that container doesn't exist in the component, the legacy node is still removed from its original spot but is never reattached anywhere visible. Always confirm the slot name matches a container the target component actually renders before relying on `preserve` for that widget.

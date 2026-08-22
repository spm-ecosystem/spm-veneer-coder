# Veneer Spec FAQ and Concepts

# What are the base extractors available in a Veneer Spec binding expression?
## User
What are the base extractors available in a Veneer Spec binding expression?
## Assistant
Veneer Spec supports seven base extractors: `text` (textContent of the matched element), `html` (innerHTML), `attr:<name>` (a named attribute value, e.g. `attr:src`), `hrefOrOnclick` (resolves a link destination from `href` or a fallback inline `onclick`), `nextSiblingText` (text content of the immediate next sibling element), `hiddenInputs` (collects all `<input type="hidden">` descendants as a JSON array string), and `selector` (generates a unique selector string for the matched element itself).

# What pipe operations can follow a base extractor in a Veneer Spec bind expression?
## User
What pipe operations can follow a base extractor in a Veneer Spec bind expression?
## Assistant
Four pipe operations are supported, chained with `|`: `split` (splits a space-separated string into a JSON array of tokens), `split:<delimiter>` (splits by a custom delimiter and trims each token), `number` (parses a valid number string into a native JSON number), and `cleanNumber` (strips currency symbols like `$`, `R$`, `€`), commas, and spacing, then parses the value into a JSON float number (e.g. `"$ 1,200.50"` -> `1200.5`).

# What is the difference between `number` and `cleanNumber` pipes, and when should each be used?
## User
What is the difference between `number` and `cleanNumber` pipes, and when should each be used?
## Assistant
`number` expects an already-clean numeric string (e.g. quantities, IDs, ratings) and converts it directly to a JSON number. `cleanNumber` is meant for currency-adjacent values: it first strips symbols such as `$`, `R$`, `€`, thousands-separator commas, and surrounding whitespace, then parses the result as a float. Use `number` for plain digits, `cleanNumber` whenever a price or formatted amount might be present.

# What does `self` mean inside a Veneer Spec bind expression?
## User
What does `self` mean inside a Veneer Spec bind expression?
## Assistant
`self` refers to the element already matched by the enclosing `selector`, `reconstruct`, or `child` block — it does not run a new DOM query. Use it to read a property (text, attribute) of the matched element itself, as opposed to a relative CSS selector which queries inside/among its descendants or siblings.

# How does Veneer Spec's raw string literal syntax work, and why would you use it?
## User
How does Veneer Spec's raw string literal syntax work, and why would you use it?
## Assistant
Raw string literals use C++-style syntax `R"(content)"`, or `R"delim(content)delim"` with a custom delimiter when the content itself contains the closing sequence `)"`. Everything between the delimiters is treated as a literal, unescaped string — no backslash-escaping needed. This is primarily used for regular expressions (like `urlPattern`) and inline JSON blocks (like `columns` or `tagGroups`), which would otherwise require painful escaping of backslashes and quotes.

# How does implicit JSON type deserialization work when Veneer Spec emits property values?
## User
How does implicit JSON type deserialization work when Veneer Spec emits property values?
## Assistant
When emitting a property to the manifest JSON, the compiler checks whether the written value parses as a valid JSON type — a number, boolean, array, or object. If it does, that native JSON type is emitted (e.g. `mobileColumns: 2;` becomes the number `2`, `showSearch: true;` becomes the boolean `true`, and a raw-string JSON array becomes a native array). If parsing fails (e.g. `"280px"` or a zip code with a leading zero like `"02139"`), the value is emitted as a plain JSON string instead.

# What is the compile-time cost of `class` declarations in Veneer Spec?
## User
What is the compile-time cost of `class` declarations in Veneer Spec?
## Assistant
Zero. Classes are resolved entirely at compile time — the resolver builds an inheritance graph, propagates bound properties and scoping rules from parent to child classes, and checks for circular dependencies — but classes themselves never appear in the final emitted manifest.json. Only the resolved bindings on the concrete `selector`, `reconstruct`, or `child` blocks that use `extends` show up in the output.

# What happens if two Veneer Spec classes in an inheritance chain both declare a binding with the same name?
## User
What happens if two Veneer Spec classes in an inheritance chain both declare a binding with the same name?
## Assistant
The child class's binding wins. If a property or `bind` is declared in both a class and the class it extends (at any depth in the chain), the child's declaration overrides the parent's when the classes are resolved.

# What is the difference between `selector` and `reconstruct` in Veneer Spec?
## User
What is the difference between `selector` and `reconstruct` in Veneer Spec?
## Assistant
`selector` targets an individual legacy element to hide or replace it in place (e.g. a header, sidebar, or search box) without touching the rest of the page. `reconstruct` is for full-viewport or full-section overrides — it targets a large container (a catalog feed, comment board, or whole page), hides its legacy children, and mounts a React layout component inside an isolated Shadow DOM host, optionally gated by `urlPattern` or `mediaQuery` constraints.

# What two actions can a `selector` block specify, and what does each do?
## User
What two actions can a `selector` block specify, and what does each do?
## Assistant
`hide` sets `display: none !important` on the matched selector, removing it visually without mounting any component. `replace` hides the legacy element and mounts a React component (specified via the `->` arrow syntax) in its place, populated with the block's static props and any `bind` extractions.

# What is the purpose of the `child` keyword in Veneer Spec, and what does it compile to?
## User
What is the purpose of the `child` keyword in Veneer Spec, and what does it compile to?
## Assistant
`child` defines a nested list of scraped legacy elements that becomes an array-valued prop on the parent layout component. It declares a name (which becomes the prop key, e.g. `child items` -> the `items` prop), a `selector` for the list items, and optional bindings (or an extended class) describing each item's fields. In the manifest, it becomes an entry in the `children` array with `name`, `selector`, optional `scope`, and a `propsMap`.

# What does the `preserve` block do inside a `reconstruct`, and what's the risk if the slot name doesn't match anything?
## User
What does the `preserve` block do inside a `reconstruct`, and what's the risk if the slot name doesn't match anything?
## Assistant
`preserve` keeps specific interactive legacy elements (like a comment form, payment iframe, or chat widget) alive instead of hiding them, reparenting them into a named slot inside the new React Shadow DOM layout. It maps a slot name to a legacy CSS selector. The target layout component must contain a host element with `id="{slotName}-container"` for the reparenting to work — the compiler cannot validate this against the component's internals, so a mismatched slot name compiles successfully but fails silently at runtime (the legacy node is removed from the page but never reappears anywhere).

# What is the default value of `scope` for a `child` block in Veneer Spec, and when is it omitted from the compiled output?
## User
What is the default value of `scope` for a `child` block in Veneer Spec, and when is it omitted from the compiled output?
## Assistant
The default scope is `"container"`, meaning selectors inside a `child` block query only descendants of the enclosing `selector`/`reconstruct` container. Because `"container"` is the default, the compiler omits the `scope` key entirely from the emitted manifest when it's either unset or explicitly set to `"container"` — only `scope: "document";` (used for elements physically outside the container, like global pagination) is emitted.

# How does spm-cli handle a directory full of .vnr files during compilation?
## User
How does spm-cli handle a directory full of .vnr files during compilation?
## Assistant
Running `spm compile <directory> -o manifest.json` recursively scans all `.vnr` files under the target path, regardless of file name or nesting depth (Java-style nested packages like `core/models/`, `layout/headers/`, `pages/gallery/` are fully supported). It concatenates their source contents and resolves class blueprints globally across the whole tree in a single compilation pass.

# What is Sibling Class Autoloading in spm-cli, and when does it trigger?
## User
What is Sibling Class Autoloading in spm-cli, and when does it trigger?
## Assistant
When compiling a single `.vnr` file in isolation (linter mode, e.g. from an editor), if the compiler encounters a class reference (`extends SomeClass`) that isn't declared in the current file, it automatically inspects the file's directory and loads sibling `.vnr` files in the background solely to resolve that class blueprint. This enables accurate background validation without requiring a full workspace compile, but it only searches the same directory — classes in unrelated top-level directories won't be found this way.

# What does spm-cli's metadata merge behavior do when recompiling over an existing manifest.json?
## User
What does spm-cli's metadata merge behavior do when recompiling over an existing manifest.json?
## Assistant
During `spm compile`, the CLI parses any preexisting target `manifest.json` and performs a deep merge on the `theme` block: global metadata fields like `author`, `description`, `targetUrl`, and `minEngineVersion` already present in the destination file are preserved and merged back into the newly compiled output, so GitOps-style metadata survives repeated compilations without manual restoration.

# Why would a Veneer Spec author choose `attr:src` combined with `nextSiblingText` versus a single selector?
## User
Why would a Veneer Spec author choose `attr:src` combined with `nextSiblingText` versus a single selector?
## Assistant
`attr:<name>` reads an attribute off the *matched* element (e.g. an `<img>`'s `src`), while `nextSiblingText` reads the text content of whatever element immediately follows the matched node in the DOM — useful when a label and its value are adjacent siblings rather than nested (e.g. `<span class="label">Price</span><span>$19.99</span>`, where matching `.label` and piping through `nextSiblingText` grabs the price text from the sibling).

# Give an example of a value that should NOT rely on Veneer Spec's implicit JSON number coercion, and explain why.
## User
Give an example of a value that should NOT rely on Veneer Spec's implicit JSON number coercion, and explain why.
## Assistant
An all-digit identifier with no leading zero and no other characters — e.g. a 10-digit phone number or account number like `"10023491"` — will be silently coerced into a JSON number during emission, which can lose formatting significance or exceed safe-integer precision for very large values. Values like postal codes with a leading zero (`"02139"`) are safe because the leading zero makes them invalid as a JSON number, so they stay strings; but plain numeric IDs are not protected this way and should be reviewed if string-preservation matters.


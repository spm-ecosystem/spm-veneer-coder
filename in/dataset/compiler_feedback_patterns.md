# Compiler Error Feedback — Unexpected token in global scope
## User
The following Veneer Spec code failed compilation with spm-cli:

```vnr
bind title: "h3 | text";
bind price: ".price | text";
```

Compiler Error Diagnostic:
[Error] Veneer compilation failed: [Parser Error] Line 1: Unexpected token in global scope

Please fix the Veneer Spec code and return only the valid ```vnr block.
## Assistant
Property bindings using the `bind` keyword cannot exist in global scope. They must be enclosed inside a `class` definition.

```vnr
class ProductCard {
    bind title: "h3 | text";
    bind price: ".price | text";
}
```

# Compiler Error Feedback — Expected ':' after property key in reconstruct
## User
The following Veneer Spec code failed compilation with spm-cli:

```vnr
reconstruct "#search-form" -> UiSearchBar {
    bind submitUrl: "form | attr:action";
    bind hiddenFields: "form | hiddenInputs";
}
```

Compiler Error Diagnostic:
[Error] Veneer compilation failed: [Parser Error] Line 2: Expected ':' after property key

Please fix the Veneer Spec code and return only the valid ```vnr block.
## Assistant
Inside `reconstruct` blocks, direct property assignments do not use the `bind` keyword. The `bind` keyword is reserved for `class` definitions.

```vnr
reconstruct "#search-form" -> UiSearchBar {
    submitUrl: "form | attr:action";
    hiddenFields: "form | hiddenInputs";
}
```

# Compiler Error Feedback — Unknown base class
## User
The following Veneer Spec code failed compilation with spm-cli:

```vnr
class ProductCard extends NonExistentBaseCard {
    bind price: ".price | text";
}
```

Compiler Error Diagnostic:
[Error] Veneer compilation failed: [Resolver Error] Unknown base class: NonExistentBaseCard

Please fix the Veneer Spec code and return only the valid ```vnr block.
## Assistant
The base class `NonExistentBaseCard` is not declared. Either declare `BaseCard` or remove the `extends` clause.

```vnr
class BaseCard {
    bind title: "h3 | text";
}

class ProductCard extends BaseCard {
    bind price: ".price | text";
}
```

# Compiler Error Feedback — Expected '->' after selector in reconstruct
## User
The following Veneer Spec code failed compilation with spm-cli:

```vnr
reconstruct "#nav-bar" UiNavHeader {
    pageTitle: "Home";
}
```

Compiler Error Diagnostic:
[Error] Veneer compilation failed: [Parser Error] Line 1: Expected '->' after selector in reconstruct

Please fix the Veneer Spec code and return only the valid ```vnr block.
## Assistant
A `reconstruct` statement requires the `->` arrow operator between the target CSS selector and the target component name.

```vnr
reconstruct "#nav-bar" -> UiNavHeader {
    pageTitle: "Home";
}
```

# Compiler Error Feedback — Expected '{' after reconstruct definition
## User
The following Veneer Spec code failed compilation with spm-cli:

```vnr
reconstruct ".header" -> UiNavHeader
action: replace;
```

Compiler Error Diagnostic:
[Error] Veneer compilation failed: [Parser Error] Line 2: Expected '{' after reconstruct definition

Please fix the Veneer Spec code and return only the valid ```vnr block.
## Assistant
The body of a `reconstruct` statement must be enclosed inside opening `{` and closing `}` braces.

```vnr
reconstruct ".header" -> UiNavHeader {
    action: replace;
}
```

# Compiler Error Feedback — Expected ':' after bind key
## User
The following Veneer Spec code failed compilation with spm-cli:

```vnr
class ItemCard {
    bind title "h3 | text";
}
```

Compiler Error Diagnostic:
[Error] Veneer compilation failed: [Parser Error] Line 2: Expected ':' after bind key

Please fix the Veneer Spec code and return only the valid ```vnr block.
## Assistant
A `bind` statement requires a colon `:` separating the property key and the selector pipe expression.

```vnr
class ItemCard {
    bind title: "h3 | text";
}
```

# Compiler Error Feedback — Expected ';' after bind expression
## User
The following Veneer Spec code failed compilation with spm-cli:

```vnr
class ItemCard {
    bind title: "h3 | text"
    bind price: ".price | text"
}
```

Compiler Error Diagnostic:
[Error] Veneer compilation failed: [Parser Error] Line 3: Expected ';' after bind expression

Please fix the Veneer Spec code and return only the valid ```vnr block.
## Assistant
Every property binding statement inside a `class` or `reconstruct` block must terminate with a semicolon `;`.

```vnr
class ItemCard {
    bind title: "h3 | text";
    bind price: ".price | text";
}
```

# Compiler Error Feedback — Invalid Child Declaration Syntax
## User
The following Veneer Spec code failed compilation with spm-cli:

```vnr
reconstruct "#feed" -> UiTableListPage {
    child items -> UiImageCard {
        selector: ".card";
    }
}
```

Compiler Error Diagnostic:
[Error] Veneer compilation failed: [Parser Error] Line 2: Expected ':' after property key

Please fix the Veneer Spec code and return only the valid ```vnr block.
## Assistant
Inside `reconstruct` blocks, child declarations do not use `->` arrow syntax. Use `child items extends ClassName` or `child items { selector: "..."; }`.

```vnr
class CardItem {
    bind title: "h3 | text";
}

reconstruct "#feed" -> UiTableListPage {
    child items extends CardItem {
        selector: ".card";
    }
}
```

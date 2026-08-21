# Custom styles block syntax instruction
## User
How should I declare global CSS styles in a theme?
## Assistant
Global CSS stylesheet rules must be defined inside a `customStyles` block with braces (curly brackets) containing one or more string literals, rather than as a scalar key-value pair.

Here is an example:
```vnr
theme "ModernDark" {
    variables {
        --spm-accent: "#7c6af5";
    }
    customStyles {
        "body { background-color: #121212 !important; }"
        "#ad-banner { display: none !important; }"
    }
}
```

---

# Scoped class directive mapping
## User
How do I map a list of items using a scoped class inside a table list page?
## Assistant
To map a list of items (like a row in a table) to relative child properties, define a `class` block, and then extend that class in a `child` block inside your `reconstruct` or `selector` declaration, and configure the table column mappings:

```vnr
class GithubIssueItem {
    bind issueNumber: "span.opened-by | text | cleanNumber";
    bind title: "a.markdown-title | text";
    bind commentsCount: "a.Link--muted | text | number";
}

reconstruct "#issues-container" -> UiTableListPage {
    pageTitle: "Repository Issues";
    columns: R"([
      { "key": "issueNumber", "header": "Issue #", "type": "number" },
      { "key": "title", "header": "Title", "type": "text" },
      { "key": "commentsCount", "header": "Comments", "type": "number" }
    ])";
    
    child tableRows extends GithubIssueItem {
        selector: ".js-issue-row";
    }
}
```

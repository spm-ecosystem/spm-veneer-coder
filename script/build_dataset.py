#!/usr/bin/env python3
"""
Builds dataset.jsonl (chat/messages format) for fine-tuning LLMs on the
Veneer Spec (.vnr) DSL, using /home/claude/veneer-spec-reference.md as the
source of truth.

Each source ```vnr code block (with its preceding heading + descriptive
text as context) is turned into several distinct training examples:

  1. "explain"      -> given the code, explain what it does
  2. "generate"      -> given a natural-language task description, write the code
  3. "complete"      -> given a partial snippet, complete it
  4. "fix" (errors only) -> given broken code + error, produce the fix
  5. "qa"            -> conceptual question about the rule demonstrated

Plus a set of hand-written "reference" Q&A pairs distilled from the prose
(non-code) parts of the doc (extractor tables, pipe tables, JSON typing
rules, cheat sheet, etc.) to make sure the dataset also covers declarative
knowledge, not just code examples.
"""

import json
import random
import re
import sys

random.seed(7)

SRC = "../in/veneer-spec-reference.md"
OUT = "../out/dataset.jsonl"

SYSTEM_PROMPT = (
    "You are an expert assistant for Veneer Spec (.vnr), the declarative "
    "layout-override DSL compiled by spm-cli for the Site Package Manager "
    "(SPM) ecosystem. You write correct, idiomatic .vnr source, explain "
    "what existing .vnr code does, and help debug compiler errors."
)

with open(SRC, encoding="utf-8") as f:
    text = f.read()

lines = text.split("\n")

# ------------------------------------------------------------------
# 1) Walk the document, tracking the current heading path, and collect
#    (heading, preceding_context_text, code) tuples for every ```vnr block.
# ------------------------------------------------------------------

heading_stack = {1: "", 2: "", 3: ""}
blocks = []  # list of dicts: heading, subheading, context, code

i = 0
pending_context = []
current_h2 = ""
current_h3 = ""

while i < len(lines):
    line = lines[i]
    h2 = re.match(r"^##\s+(.*)", line)
    h3 = re.match(r"^###\s+(.*)", line)
    if h2 and not line.startswith("###"):
        current_h2 = h2.group(1).strip()
        current_h3 = ""
        pending_context = []
        i += 1
        continue
    if h3:
        current_h3 = h3.group(1).strip()
        pending_context = []
        i += 1
        continue
    if line.strip() == "```vnr":
        i += 1
        code_lines = []
        while i < len(lines) and lines[i].strip() != "```":
            code_lines.append(lines[i])
            i += 1
        code = "\n".join(code_lines).strip("\n")
        ctx_text = " ".join(pending_context).strip()
        blocks.append({
            "h2": current_h2,
            "h3": current_h3,
            "context": ctx_text,
            "code": code,
        })
        pending_context = []
        i += 1
        continue
    # accumulate plain prose lines (skip other code fences, tables, blockquotes noise a bit)
    stripped = line.strip()
    if stripped and not stripped.startswith("```") and not stripped.startswith("|"):
        pending_context.append(stripped)
        # keep the context window short/recent
        pending_context = pending_context[-6:]
    i += 1

print(f"Extracted {len(blocks)} vnr code blocks", file=sys.stderr)

# ------------------------------------------------------------------
# 2) Generate diverse training examples from each block
# ------------------------------------------------------------------

examples = []


def add(messages):
    examples.append({"messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages})


EXPLAIN_TEMPLATES = [
    "Explain what the following Veneer Spec (.vnr) code does:\n\n```vnr\n{code}\n```",
    "What does this .vnr snippet compile to / achieve? \n\n```vnr\n{code}\n```",
    "Walk me through this Veneer Spec block line by line:\n\n```vnr\n{code}\n```",
    "I found this in a spm-cli theme project. What is it doing?\n\n```vnr\n{code}\n```",
]

GENERATE_TEMPLATES = [
    "Write a Veneer Spec (.vnr) snippet that does the following: {ctx}",
    "In .vnr syntax, {ctx_lower}",
    "Show me how to accomplish this in Veneer Spec: {ctx}",
    "I'm building an spm-cli theme. {ctx} Give me the .vnr code.",
]

QA_TEMPLATES_BY_SECTION = {
    "`theme` — Exhaustive Examples": "How many `theme` blocks are allowed in a single compiled Veneer Spec project, and what happens if you declare more than one?",
    "`scope` — Exhaustive Examples": "What is the default `scope` for a `child` selector query in Veneer Spec, and when should you override it with `scope: \"document\"`?",
    "`class` / `extends` — Exhaustive Examples": "How does property overriding work when a Veneer Spec class extends another class and both declare the same `bind`?",
    "`preserve` — Exhaustive Examples": "What does the `preserve` block do in a `reconstruct`, and what naming convention must the target React layout follow for the slot to work at runtime?",
}


def clean_ctx(ctx):
    # trim trailing punctuation artifacts, keep it a clean sentence-ish string
    ctx = ctx.strip()
    ctx = re.sub(r"\s+", " ", ctx)
    return ctx


for b in blocks:
    code = b["code"]
    if not code.strip():
        continue
    # Skip the "Common Errors" section here entirely — those ❌/✅ snippets are
    # handled separately below as dedicated bad-code/fix pairs, and including
    # them in the generic explain/generate/complete loop would train the model
    # on broken code as if it were valid.
    if b["h2"].strip().startswith("17."):
        continue
    ctx = clean_ctx(b["context"])
    raw_heading = b["h3"] or b["h2"]
    # strip a leading numeric subsection label like "8.8 " so the heading reads naturally
    heading = re.sub(r"^\d+(\.\d+)*\s+", "", raw_heading).strip()

    # ---- 1) explain (two independent phrasings per block for paraphrase coverage) ----
    explanation = (
        f"This snippet is an example of **{heading}** in Veneer Spec.\n\n"
        + (f"Context: {ctx}\n\n" if ctx else "")
        + "```vnr\n" + code + "\n```\n\n"
        + "When compiled with `spm-cli`, this is lexed, parsed into an AST, "
        "resolved (class inheritance and scoping applied), and emitted into the "
        "target `manifest.json`, following the rules for this construct described "
        "in the Veneer Spec language reference."
    )
    explain_tpls = random.sample(EXPLAIN_TEMPLATES, k=2)
    for tpl in explain_tpls:
        user_msg = tpl.format(code=code)
        add([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": explanation},
        ])

    # ---- 2) generate from description (only if we have decent context) ----
    if ctx and len(ctx) > 25:
        ctx_lower = ctx[0].lower() + ctx[1:] if ctx else ctx
        gen_tpls = random.sample(GENERATE_TEMPLATES, k=2)
        assistant_msg = f"```vnr\n{code}\n```"
        for tpl in gen_tpls:
            user_msg = tpl.format(ctx=ctx, ctx_lower=ctx_lower)
            add([
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_msg},
            ])

    # ---- 3) complete a partial snippet (for multi-line blocks only) ----
    code_lines = code.split("\n")
    if len(code_lines) >= 6:
        cut = max(2, len(code_lines) // 2)
        partial = "\n".join(code_lines[:cut])
        user_msg = (
            "Complete this Veneer Spec snippet in a way that is consistent with "
            f"the `{heading}` construct:\n\n```vnr\n{partial}\n...\n```"
        )
        assistant_msg = f"```vnr\n{code}\n```"
        add([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg},
        ])

# ------------------------------------------------------------------
# 3) Errors / anti-patterns section -> dedicated "fix the bug" examples
#    (parsed specially since each has a ❌ bad example and a ✅ good one)
# ------------------------------------------------------------------

err_section = text.split("## 17. Common Errors, Anti-Patterns & Fixes")[1].split("## 18.")[0]
# split into individual "### 17.N ..." subsections so bad/good pairs never cross
subsections = re.split(r"(?=^### 17\.\d)", err_section, flags=re.M)

for sub in subsections:
    sub_blocks = re.findall(r"```vnr\n(.*?)\n```", sub, re.S)
    bad = next((c for c in sub_blocks if "❌" in c), None)
    good = next((c for c in sub_blocks if "✅" in c), None)
    if not bad or not good:
        continue  # only keep subsections that have a clear broken/fixed pair
    bad_comment_match = re.search(r"//\s*❌\s*(.*)", bad)
    err_desc = bad_comment_match.group(1).strip() if bad_comment_match else "a compile-time error"
    user_msg = (
        "The following Veneer Spec code fails to compile "
        f"({err_desc}). What's wrong, and how do I fix it?\n\n```vnr\n{bad}\n```"
    )
    assistant_msg = (
        f"The problem: {err_desc}.\n\nHere is the corrected version:\n\n```vnr\n{good}\n```"
    )
    add([
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": assistant_msg},
    ])

# ------------------------------------------------------------------
# 4) Hand-written declarative Q&A pairs (extractors, pipes, JSON typing,
#    keyword rules) distilled from the prose/tables in the doc.
# ------------------------------------------------------------------

qa_pairs = [
    ("What are the base extractors available in a Veneer Spec binding expression?",
     "Veneer Spec supports seven base extractors: `text` (textContent of the matched element), "
     "`html` (innerHTML), `attr:<name>` (a named attribute value, e.g. `attr:src`), "
     "`hrefOrOnclick` (resolves a link destination from `href` or a fallback inline `onclick`), "
     "`nextSiblingText` (text content of the immediate next sibling element), `hiddenInputs` "
     "(collects all `<input type=\"hidden\">` descendants as a JSON array string), and `selector` "
     "(generates a unique selector string for the matched element itself)."),
    ("What pipe operations can follow a base extractor in a Veneer Spec bind expression?",
     "Four pipe operations are supported, chained with `|`: `split` (splits a space-separated "
     "string into a JSON array of tokens), `split:<delimiter>` (splits by a custom delimiter and "
     "trims each token), `number` (parses a clean numeric string into a native JSON number), and "
     "`cleanNumber` (strips currency symbols like `$`, `R$`, `€`, commas, and whitespace before "
     "parsing into a JSON float — e.g. `\"$ 1,200.50\"` becomes `1200.5`)."),
    ("What is the difference between `number` and `cleanNumber` pipes, and when should each be used?",
     "`number` expects an already-clean numeric string (e.g. quantities, IDs, ratings) and converts "
     "it directly to a JSON number. `cleanNumber` is meant for currency-adjacent values: it first "
     "strips symbols such as `$`, `R$`, `€`, thousands-separator commas, and surrounding whitespace, "
     "then parses the result as a float. Use `number` for plain digits, `cleanNumber` whenever a "
     "price or formatted amount might be present."),
    ("What does `self` mean inside a Veneer Spec bind expression?",
     "`self` refers to the element already matched by the enclosing `selector`, `reconstruct`, or "
     "`child` block — it does not run a new DOM query. Use it to read a property (text, attribute) "
     "of the matched element itself, as opposed to a relative CSS selector which queries inside/among "
     "its descendants or siblings."),
    ("How does Veneer Spec's raw string literal syntax work, and why would you use it?",
     "Raw string literals use C++-style syntax `R\"(content)\"`, or `R\"delim(content)delim\"` with a "
     "custom delimiter when the content itself contains the closing sequence `)\"`. Everything between "
     "the delimiters is treated as a literal, unescaped string — no backslash-escaping needed. This is "
     "primarily used for regular expressions (like `urlPattern`) and inline JSON blocks (like `columns` "
     "or `tagGroups`), which would otherwise require painful escaping of backslashes and quotes."),
    ("How does implicit JSON type deserialization work when Veneer Spec emits property values?",
     "When emitting a property to the manifest JSON, the compiler checks whether the written value "
     "parses as a valid JSON type — a number, boolean, array, or object. If it does, that native JSON "
     "type is emitted (e.g. `mobileColumns: 2;` becomes the number `2`, `showSearch: true;` becomes "
     "the boolean `true`, and a raw-string JSON array becomes a native array). If parsing fails (e.g. "
     "`\"280px\"` or a zip code with a leading zero like `\"02139\"`), the value is emitted as a plain "
     "JSON string instead."),
    ("What is the compile-time cost of `class` declarations in Veneer Spec?",
     "Zero. Classes are resolved entirely at compile time — the resolver builds an inheritance graph, "
     "propagates bound properties and scoping rules from parent to child classes, and checks for "
     "circular dependencies — but classes themselves never appear in the final emitted manifest.json. "
     "Only the resolved bindings on the concrete `selector`, `reconstruct`, or `child` blocks that use "
     "`extends` show up in the output."),
    ("What happens if two Veneer Spec classes in an inheritance chain both declare a binding with the same name?",
     "The child class's binding wins. If a property or `bind` is declared in both a class and the "
     "class it extends (at any depth in the chain), the child's declaration overrides the parent's "
     "when the classes are resolved."),
    ("What is the difference between `selector` and `reconstruct` in Veneer Spec?",
     "`selector` targets an individual legacy element to hide or replace it in place (e.g. a header, "
     "sidebar, or search box) without touching the rest of the page. `reconstruct` is for full-viewport "
     "or full-section overrides — it targets a large container (a catalog feed, comment board, or "
     "whole page), hides its legacy children, and mounts a React layout component inside an isolated "
     "Shadow DOM host, optionally gated by `urlPattern` or `mediaQuery` constraints."),
    ("What two actions can a `selector` block specify, and what does each do?",
     "`hide` sets `display: none !important` on the matched selector, removing it visually without "
     "mounting any component. `replace` hides the legacy element and mounts a React component "
     "(specified via the `->` arrow syntax) in its place, populated with the block's static props "
     "and any `bind` extractions."),
    ("What is the purpose of the `child` keyword in Veneer Spec, and what does it compile to?",
     "`child` defines a nested list of scraped legacy elements that becomes an array-valued prop on "
     "the parent layout component. It declares a name (which becomes the prop key, e.g. `child items` "
     "-> the `items` prop), a `selector` for the list items, and optional bindings (or an extended "
     "class) describing each item's fields. In the manifest, it becomes an entry in the `children` "
     "array with `name`, `selector`, optional `scope`, and a `propsMap`."),
    ("What does the `preserve` block do inside a `reconstruct`, and what's the risk if the slot name doesn't match anything?",
     "`preserve` keeps specific interactive legacy elements (like a comment form, payment iframe, or "
     "chat widget) alive instead of hiding them, reparenting them into a named slot inside the new "
     "React Shadow DOM layout. It maps a slot name to a legacy CSS selector. The target layout "
     "component must contain a host element with `id=\"{slotName}-container\"` for the reparenting to "
     "work — the compiler cannot validate this against the component's internals, so a mismatched slot "
     "name compiles successfully but fails silently at runtime (the legacy node is removed from the "
     "page but never reappears anywhere)."),
    ("What is the default value of `scope` for a `child` block in Veneer Spec, and when is it omitted from the compiled output?",
     "The default scope is `\"container\"`, meaning selectors inside a `child` block query only "
     "descendants of the enclosing `selector`/`reconstruct` container. Because `\"container\"` is the "
     "default, the compiler omits the `scope` key entirely from the emitted manifest when it's either "
     "unset or explicitly set to `\"container\"` — only `scope: \"document\";` (used for elements "
     "physically outside the container, like global pagination) is emitted."),
    ("How does spm-cli handle a directory full of .vnr files during compilation?",
     "Running `spm compile <directory> -o manifest.json` recursively scans all `.vnr` files under the "
     "target path, regardless of file name or nesting depth (Java-style nested packages like "
     "`core/models/`, `layout/headers/`, `pages/gallery/` are fully supported). It concatenates their "
     "source contents and resolves class blueprints globally across the whole tree in a single "
     "compilation pass."),
    ("What is Sibling Class Autoloading in spm-cli, and when does it trigger?",
     "When compiling a single `.vnr` file in isolation (linter mode, e.g. from an editor), if the "
     "compiler encounters a class reference (`extends SomeClass`) that isn't declared in the current "
     "file, it automatically inspects the file's directory and loads sibling `.vnr` files in the "
     "background solely to resolve that class blueprint. This enables accurate background validation "
     "without requiring a full workspace compile, but it only searches the same directory — classes "
     "in unrelated top-level directories won't be found this way."),
    ("What does spm-cli's metadata merge behavior do when recompiling over an existing manifest.json?",
     "During `spm compile`, the CLI parses any preexisting target `manifest.json` and performs a deep "
     "merge on the `theme` block: global metadata fields like `author`, `description`, `targetUrl`, "
     "and `minEngineVersion` already present in the destination file are preserved and merged back "
     "into the newly compiled output, so GitOps-style metadata survives repeated compilations without "
     "manual restoration."),
    ("Why would a Veneer Spec author choose `attr:src` combined with `nextSiblingText` versus a single selector?",
     "`attr:<name>` reads an attribute off the *matched* element (e.g. an `<img>`'s `src`), while "
     "`nextSiblingText` reads the text content of whatever element immediately follows the matched "
     "node in the DOM — useful when a label and its value are adjacent siblings rather than nested "
     "(e.g. `<span class=\"label\">Price</span><span>$19.99</span>`, where matching `.label` and "
     "piping through `nextSiblingText` grabs the price text from the sibling)."),
    ("Give an example of a value that should NOT rely on Veneer Spec's implicit JSON number coercion, and explain why.",
     "An all-digit identifier with no leading zero and no other characters — e.g. a 10-digit phone "
     "number or account number like `\"10023491\"` — will be silently coerced into a JSON number "
     "during emission, which can lose formatting significance or exceed safe-integer precision for "
     "very large values. Values like postal codes with a leading zero (`\"02139\"`) are safe because "
     "the leading zero makes them invalid as a JSON number, so they stay strings; but plain numeric "
     "IDs are not protected this way and should be reviewed if string-preservation matters."),
]

for q, a in qa_pairs:
    add([
        {"role": "user", "content": q},
        {"role": "assistant", "content": a},
    ])

# ------------------------------------------------------------------
# 5) Shuffle and write out
# ------------------------------------------------------------------

random.shuffle(examples)

with open(OUT, "w", encoding="utf-8") as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print(f"Wrote {len(examples)} examples to {OUT}", file=sys.stderr)

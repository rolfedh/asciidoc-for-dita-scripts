Optimize the following github copilot prompt:

Look at the https://github.com/jhradilek/asciidoctor-dita-vale rule for ContentType:
```
ContentType:	Without an explicit content type definition, the Vale style cannot reliably report problems related to procedure modules such as TaskSection or TaskExample. Add the correct `:_mod-docs-content-type:` definition at the top of the file.
```

Look at the following ideal placement of the `:_mod-docs-content-type: ` attribute, at the top of the file, above the ID and title. For example:

```
:_mod-docs-content-type: CONCEPT

[id="my-concept-module-a_{context}"]
= My concept module A

```

More examples for other content types are available here:  https://github.com/redhat-documentation/modular-docs/tree/main/modular-docs-manual/files

**GOAL: Based on your expertise in of user interface design, suggest a user interface that does the following**

As an end user, I want you to help me design interactive software that gives users a range of choices in how they want to interact: from "just fix errors for me", to "just flag issues in the file but don't make any changes; I'll review the flags and update them manually"; to "guide me interactively file-by-file to apply changes that fix errors and apply suggestions."   

There are going to be three levels of issues:
- SUGGESTION
- WARNING 
- ERROR

Here is a review of the expected files in the ContentType directory:

---

### ignore_content_type.expected
```plaintext
// A topic with a deprecated content type definition:
:_content-type: PROCEDURE

= Topic title

A paragraph.
```
- Deprecated `:_content-type:` is present. The plugin should ignore this and make no changes.

PLUGIN, generate an interactive a suggestion for this: 
```
A deprecated `:_content-type:` attribute is present. 
SUGGESTION: Replace it with a `:_mod-docs-content-type:`? Y/n
```
If yes, ask:
```
SUGGESTION: Do you want me to automatically replace all `:_content-type:` attributes with a `:_mod-docs-content-type:`? Y/n
```

---

### ignore_defined_type.expected
```plaintext
// A topic with a valid content type definition:
:_mod-docs-content-type: PROCEDURE

= Topic title

A paragraph.
```
- The correct content type is already defined. The plugin should not change anything.

---

PLUGIN, don't do anything for this one.

### ignore_module_type.expected
```plaintext
// A topic with a deprecated content type definition:
:_module-type: PROCEDURE

= Topic title

A paragraph.
```
- Deprecated `:_module-type:` is present. The plugin should ignore this and make no changes.


PLUGIN, generate an interactive a suggestion for this: 
```
A deprecated `:_module-type:` attribute is present. 
SUGGESTION: Replace it with a `:_mod-docs-content-type:`? Y/n
```

If yes, ask:
```
SUGGESTION: Do you want me to automatically replace all `:_module-type:` attributes with a `:_mod-docs-content-type:`? Y/n
```

---

### ignore_preceding_content.expected
```plaintext
// A topic with a valid content type definition:
= Topic title
:_mod-docs-content-type: PROCEDURE

A paragraph.
```
- The content type is present after the title. The plugin should not change anything.

PLUGIN, generate an interactive a suggestion for this: 
```
The expected `:_mod-docs-content-type:` attribute is below the ID and Title lines. 
SUGGESTION: Move it above them? Y/n
```

If yes, ask:
```
SUGGESTION: Move all similar instances above the ID and title lines? Y/n
```

---

### report_comments.expected
```plaintext
// A topic with the content type definition commented out:
//:_mod-docs-content-type: PROCEDURE

= Topic title

A paragraph.
```
- The content type is commented out. The plugin should report or fix this as needed.

PLUGIN, generate an interactive a suggestion for this: 
```
The expected `:_mod-docs-content-type:` attribute is present but commented out. 
SUGGESTION: Uncomment it? Y/n
```

If yes, ask:
```
SUGGESTION: Uncomment all similar instances? Y/n
```

---

### report_missing_type.expected
```plaintext
// A topic without the content type definition:
= Topic title

A paragraph.
```
- No content type is present. The plugin should add or report the missing type.

PLUGIN, generate an interactive a suggestion for this: 
```
The expected `:_mod-docs-content-type:` attribute is missing. 
SUGGESTION: Create it? Y/n
```

If yes, ask:
```
SUGGESTION: Use up/down arrow to select the content type: 
ASSEMBLY
CONCEPT
PROCEDURE
REFERENCE
SNIPPET
```

---

### report_missing_value.expected
```plaintext
// A topic with an invalid content type definition:
:_mod-docs-content-type:

= Topic title

A paragraph.
```
- The content type key is present but the value is missing. The plugin should report or fix this.

```
The value of the `:_mod-docs-content-type:` attribute is missing. 
Use up/down arrow to select the content type: 

ASSEMBLY
CONCEPT
PROCEDURE
REFERENCE
SNIPPET
```

---

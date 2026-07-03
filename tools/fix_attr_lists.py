"""Move trailing attr_list annotations onto their own line after mdformat runs.

Python-Markdown's attr_list extension applies block-level attributes (e.g. table
caption styling like `{: style="..." }`) only when the attribute list is alone on
the last line of the block. mdformat's line wrapping joins that line into the
preceding text whenever the combined length fits the wrap width, which makes the
annotation render literally. This tool re-splits such lines and runs as the final
step of the `format-md` task.

Same-line attribute lists on headings are valid syntax and are left untouched.
"""

import re
from os.path import abspath, dirname, join
from pathlib import Path

HERE = dirname(abspath(__file__))
DOCS = join(HERE, "../ieps")

TRAILING_ATTR = re.compile(
    r"^(?P<indent>[ ]*)(?P<text>\S.*\S)[ ]+(?P<attr>\{:[^{}]*\})[ ]*$"
)
FENCE = re.compile(r"^[ ]*(?P<marker>`{3,}|~{3,})(?P<rest>.*)$")


def split_trailing_attr_lists(text):
    """Return text with non-heading trailing attr_lists moved to their own line."""
    lines = []
    fence = None  # marker of the currently open code fence, if any
    for line in text.split("\n"):
        fence_match = FENCE.match(line)
        if fence_match:
            marker = fence_match["marker"]
            if fence is None:
                fence = marker
            elif marker.startswith(fence) and not fence_match["rest"].strip():
                # A closing fence uses the same marker character, is at least as
                # long as the opening fence, and carries no info string.
                fence = None
            lines.append(line)
            continue
        match = TRAILING_ATTR.match(line)
        if match and fence is None and not match["text"].startswith("#"):
            lines.append(match["indent"] + match["text"])
            lines.append(match["indent"] + match["attr"])
        else:
            lines.append(line)
    return "\n".join(lines)


def main():
    """Fix trailing attr_lists in all markdown files of the documentation tree."""
    for path in sorted(Path(DOCS).rglob("*.md")):
        original = path.read_text(encoding="utf-8")
        fixed = split_trailing_attr_lists(original)
        if fixed != original:
            path.write_text(fixed, encoding="utf-8", newline="\n")
            print(f"fixed attr_lists in {path}")


if __name__ == "__main__":
    main()

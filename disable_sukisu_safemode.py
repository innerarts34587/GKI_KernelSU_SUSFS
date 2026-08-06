#!/usr/bin/env python3

from pathlib import Path
import re
import shutil
import sys


ROOT = Path("drivers/kernelsu")
MARKER = "SUKISU_SAFE_MODE_TEMP_DISABLED"



# bool ksu_is_safe_mode()
# bool ksu_is_safe_mode(void)
pattern = re.compile(
    r"\bbool\s+ksu_is_safe_mode\s*\(\s*(?:void\s*)?\)\s*\{",
    re.MULTILINE
)


if not ROOT.exists():
    print("ERROR: drivers/kernelsu not found")
    sys.exit(1)


patched = False


for file in ROOT.rglob("*.c"):

    text = file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    
    if MARKER in text:
        print(f"Already patched: {file}")
        continue


    match = pattern.search(text)

    if not match:
        continue


    print(f"Found safe mode function: {file}")


    start = match.start()

    brace_start = text.find("{", match.start())

    if brace_start < 0:
        print("ERROR: function brace not found")
        sys.exit(1)


    depth = 0
    end = None


    for i in range(brace_start, len(text)):

        if text[i] == "{":
            depth += 1

        elif text[i] == "}":
            depth -= 1

            if depth == 0:
                end = i
                break


    if end is None:
        print("ERROR: function end not found")
        sys.exit(1)


   
    backup = file.with_suffix(
        file.suffix + ".sukisu-safemode.bak"
    )

    if not backup.exists():
        shutil.copy2(file, backup)
        print(f"Backup: {backup}")


    old_function = text[start:end+1]


   
    signature = old_function.split("{")[0].rstrip()


    new_function = f"""{signature}
{{
    /* {MARKER}: disable early boot VOLUME_DOWN safe mode detection */
    return false;
}}"""


    new_text = (
        text[:start]
        + new_function
        + text[end+1:]
    )


    file.write_text(
        new_text,
        encoding="utf-8"
    )


    print(f"Patched: {file}")

    patched = True
    break



if not patched:
    print(
        "ERROR: Cannot find ksu_is_safe_mode()"
    )
    sys.exit(1)



print(
    "SukiSU kernel safe mode disabled successfully."
)
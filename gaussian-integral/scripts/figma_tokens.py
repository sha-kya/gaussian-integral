"""Write tokens.json from a Figma file's local variables.

    FIGMA_TOKEN=<token with file_variables:read> FIGMA_FILE_KEY=<key> python scripts/figma_tokens.py

Name each variable after the token it sets, inside a collection named for its
group: collection "color" with variable "integrand", collection "font" with
"title-size", and so on (see tokens.json). Aliased variables are skipped and
only each collection's default mode is read. The variables endpoint is only
available on Figma Enterprise plans.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "tokens.json"


def fetch_variables(file_key, token):
    url = f"https://api.figma.com/v1/files/{file_key}/variables/local"
    request = urllib.request.Request(url, headers={"X-Figma-Token": token})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["meta"]


def variables_to_tokens(meta):
    tokens = {}
    for variable in meta["variables"].values():
        collection = meta["variableCollections"][variable["variableCollectionId"]]
        value = variable["valuesByMode"][collection["defaultModeId"]]
        if isinstance(value, dict) and value.get("type") == "VARIABLE_ALIAS":
            continue
        if isinstance(value, dict):  # colours arrive as 0-1 floats
            value = "#{:02X}{:02X}{:02X}".format(*(round(value[c] * 255) for c in "rgb"))
        group = collection["name"].strip().lower()
        tokens.setdefault(group, {})[variable["name"].split("/")[-1].strip().lower()] = value
    return tokens


if __name__ == "__main__":
    token = os.environ["FIGMA_TOKEN"]
    file_key = os.environ["FIGMA_FILE_KEY"]
    tokens = variables_to_tokens(fetch_variables(file_key, token))
    OUTPUT.write_text(json.dumps(tokens, indent=2) + "\n")
    print(f"wrote {sum(map(len, tokens.values()))} tokens to {OUTPUT.name}", file=sys.stderr)

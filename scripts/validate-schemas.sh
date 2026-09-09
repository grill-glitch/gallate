#!/usr/bin/env bash
#
# validate-schemas.sh
#
# Validate every YAML file under schema/ as JSON Schema draft-07.
#
# The schemas are stored in YAML (human-readable, GCWP-consistent),
# but the semantic definitions follow JSON Schema. We convert each
# schema to JSON with `yq` and pass it to a JSON Schema validator.
#
# Requirements:
#   yq        https://github.com/mikefarah/yq  (v4+)
#   check-jsonschema  (or any other Draft-07 validator)
#
# Install on Arch:
#   pacman -S yq python-check-jsonschema
#
# Usage:
#   ./scripts/validate-schemas.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SCHEMA_DIR="${REPO_ROOT}/schema"

if ! command -v yq >/dev/null 2>&1; then
    echo "ERROR: 'yq' not found. Install with: pacman -S yq" >&2
    exit 1
fi

if ! command -v check-jsonschema >/dev/null 2>&1; then
    echo "ERROR: 'check-jsonschema' not found." >&2
    echo "  pip install check-jsonschema" >&2
    exit 1
fi

fail=0
count=0

for schema_file in "${SCHEMA_DIR}"/*.schema.yaml; do
    [ -f "${schema_file}" ] || continue
    count=$((count + 1))
    base="$(basename "${schema_file}" .yaml)"

    json_tmp="$(mktemp --suffix=.json)"
    trap "rm -f '${json_tmp}'" EXIT

    echo "Validating ${base}..."
    yq -o=json '.' "${schema_file}" > "${json_tmp}"

    # check-jsonschema --schemafile validates the schema itself.
    if ! check-jsonschema --schemafile "${json_tmp}"; then
        echo "  ✗ ${base} is not a valid JSON Schema" >&2
        fail=1
    else
        echo "  ✓ ${base}"
    fi
done

echo
echo "Checked ${count} schemas."

exit ${fail}
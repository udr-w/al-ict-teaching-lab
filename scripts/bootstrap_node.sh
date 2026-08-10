#!/usr/bin/env sh
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TOOLS_DIR="$REPO_ROOT/.tools"
TARGET_DIR="$TOOLS_DIR/node-v22.23.2-linux-x64"
ARCHIVE_URL="https://nodejs.org/dist/v22.23.2/node-v22.23.2-linux-x64.tar.xz"
EXPECTED_SHA256="d60acfe00a2932254bb0ad20e01b0d74397a0875595de719654b214f4b03f307"

if [ -x "$TARGET_DIR/bin/node" ]; then
  "$TARGET_DIR/bin/node" --version
  exit 0
fi

mkdir -p "$TOOLS_DIR"
STAGING_DIR=$(mktemp -d "$TOOLS_DIR/node-staging.XXXXXX")
ARCHIVE_PATH="$STAGING_DIR/node.tar.xz"
trap 'test ! -d "$STAGING_DIR" || mv "$STAGING_DIR" "$STAGING_DIR.incomplete"' EXIT

curl --fail --location --retry 3 "$ARCHIVE_URL" --output "$ARCHIVE_PATH"
printf '%s  %s\n' "$EXPECTED_SHA256" "$ARCHIVE_PATH" | sha256sum --check --status
tar -xJf "$ARCHIVE_PATH" -C "$TOOLS_DIR"
mv "$ARCHIVE_PATH" "$TOOLS_DIR/node-v22.23.2-linux-x64.tar.xz.verified"
rmdir "$STAGING_DIR"
trap - EXIT
printf '%s\n' "Installed verified Node at $TARGET_DIR"
"$TARGET_DIR/bin/node" --version

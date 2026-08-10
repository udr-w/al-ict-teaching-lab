#!/usr/bin/env sh
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TOOLS_DIR="$REPO_ROOT/.tools"
TARGET_DIR="$TOOLS_DIR/quarto-1.10.18"
ARCHIVE_URL="https://github.com/quarto-dev/quarto-cli/releases/download/v1.10.18/quarto-1.10.18-linux-amd64.tar.gz"
EXPECTED_SHA256="afad071b5bd22c02f2d300695743189d3650e0537a53073e654b630cff2b0c73"

if [ -x "$TARGET_DIR/bin/quarto" ]; then
  "$TARGET_DIR/bin/quarto" --version
  exit 0
fi

mkdir -p "$TOOLS_DIR"
STAGING_DIR=$(mktemp -d "$TOOLS_DIR/quarto-staging.XXXXXX")
ARCHIVE_PATH="$STAGING_DIR/quarto.tar.gz"
trap 'test ! -d "$STAGING_DIR" || mv "$STAGING_DIR" "$STAGING_DIR.incomplete"' EXIT

curl --fail --location --retry 3 "$ARCHIVE_URL" --output "$ARCHIVE_PATH"
printf '%s  %s\n' "$EXPECTED_SHA256" "$ARCHIVE_PATH" | sha256sum --check --status
mkdir -p "$STAGING_DIR/extracted"
tar -xzf "$ARCHIVE_PATH" -C "$STAGING_DIR/extracted" --strip-components=1
mv "$STAGING_DIR/extracted" "$TARGET_DIR"
mv "$ARCHIVE_PATH" "$TOOLS_DIR/quarto-1.10.18-linux-amd64.tar.gz.verified"
rmdir "$STAGING_DIR"
trap - EXIT
printf '%s\n' "Installed verified Quarto at $TARGET_DIR"
"$TARGET_DIR/bin/quarto" --version

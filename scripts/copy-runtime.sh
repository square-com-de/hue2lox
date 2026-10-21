#!/bin/sh
# Shared by the historical, explicitly targeted prototype update scripts.
# src/dst/backup are supplied by the caller; never copy live secrets or .env.
copy_runtime() {
    for directory in src docker config web catalog trust; do
        [ -d "$src/$directory" ] || { echo "Missing source directory: $src/$directory"; return 1; }
    done
    umask 077
    mkdir -p "$backup"
    for item in src docker config web catalog trust compose.yaml .dockerignore LICENSE NOTICE THIRD-PARTY-NOTICES.md; do
        if [ -e "$dst/$item" ]; then cp -a "$dst/$item" "$backup/"; fi
    done
    printf 'Rollback files: %s\n' "$backup"
    for directory in src docker web catalog trust; do
        install -d -m 755 "$dst/$directory"
        cp -R "$src/$directory/." "$dst/$directory/"
        find "$dst/$directory" -type d -exec chmod 755 {} \;
        find "$dst/$directory" -type f -exec chmod 644 {} \;
    done
    install -d -m 755 "$dst/config"
    if [ ! -f "$dst/config/registry.json" ]; then
        if [ -f "$dst/registry.json" ]; then
            install -m 644 "$dst/registry.json" "$dst/config/registry.json"
        else
            install -m 644 "$src/config/registry.json" "$dst/config/registry.json"
        fi
    fi
    for file in compose.yaml .dockerignore LICENSE NOTICE THIRD-PARTY-NOTICES.md; do
        install -m 644 "$src/$file" "$dst/$file"
    done
}

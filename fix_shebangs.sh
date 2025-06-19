find ~/LGitHub/Python-Utilities -type f -name "*.py" | while read -r file; do
    first_line=$(head -n 1 "$file")
    if [[ "$first_line" != "#!/usr/bin/env python3" ]]; then
        echo "Adding shebang to $file"
        tmpfile=$(mktemp)
        echo '#!/usr/bin/env python3' > "$tmpfile"
        cat "$file" >> "$tmpfile"
        mv "$tmpfile" "$file"
        chmod +x "$file"
    fi
done


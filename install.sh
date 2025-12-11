#!/bin/bash
# Installation script for uv-disk-clean CLI tool

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"
BIN_DIR="$HOME/.local/bin"
SYMLINK="$BIN_DIR/uv-disk-clean"

echo "Installing uv-disk-clean..."

# Create bin directory if it doesn't exist
mkdir -p "$BIN_DIR"

# Make main script executable
chmod +x "$MAIN_SCRIPT"

# Create symlink
if [ -L "$SYMLINK" ] || [ -e "$SYMLINK" ]; then
    echo "Removing existing symlink..."
    rm "$SYMLINK"
fi

ln -s "$MAIN_SCRIPT" "$SYMLINK"
echo "Created symlink: $SYMLINK -> $MAIN_SCRIPT"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "Warning: $BIN_DIR is not in your PATH."
    echo "Add this line to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then run: source ~/.bashrc  (or source ~/.zshrc)"
else
    echo ""
    echo "Installation complete!"
    echo "You can now run 'uv-disk-clean' from anywhere."
fi

# Verify installation
if [ -x "$SYMLINK" ]; then
    echo ""
    echo "Verifying installation..."
    "$SYMLINK" --version
    echo ""
    echo "Installation successful!"
else
    echo "Error: Installation verification failed."
    exit 1
fi


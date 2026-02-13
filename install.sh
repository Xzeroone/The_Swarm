#!/bin/bash
# The Swarm v2.0 - One-Command Installer
# Usage: curl -sSL https://raw.githubusercontent.com/Xzeroone/The_Swarm/main/install.sh | bash
# License: MIT

set -e

INSTALL_DIR="${INSTALL_DIR:-$HOME/.swarm}"
CONFIG_DIR="${CONFIG_DIR:-$HOME/.swarm-config}"
REPO_URL="https://github.com/Xzeroone/The_Swarm"
BIN_DIR="$HOME/.local/bin"

echo ""
echo "🐝 The Swarm v2.0 Installer"
echo "============================"
echo ""
echo "Install directory: $INSTALL_DIR"
echo "Config directory: $CONFIG_DIR"
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Install with: apt install python3 python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PYTHON_VERSION detected"

# 2. Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
fi
echo "✓ Ollama detected"

# 3. Clone or update repository
if [[ -d "$INSTALL_DIR" ]]; then
    echo ""
    echo "📦 Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull 2>/dev/null || echo "   (Not a git repo, skipping pull)"
else
    echo ""
    echo "📦 Cloning repository..."
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 4. Create Python venv
echo ""
echo "🐍 Setting up Python environment..."
python3 -m venv venv

# 5. Install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# 6. Create config directory
echo ""
echo "📁 Setting up directories..."
mkdir -p "$CONFIG_DIR"
mkdir -p "$CONFIG_DIR/workspace/skills"
mkdir -p "$BIN_DIR"

# 7. Detect hardware and create config
echo ""
echo "🔍 Detecting hardware..."
RAM_GB=$(free -g | awk '/^Mem:/{print $2}')

if [ "$RAM_GB" -ge 16 ]; then
    DEFAULT_MODEL="qwen2.5-coder:3b"
    PROFILE="powerful"
elif [ "$RAM_GB" -ge 8 ]; then
    DEFAULT_MODEL="qwen2.5-coder:1.5b"
    PROFILE="moderate"
elif [ "$RAM_GB" -ge 4 ]; then
    DEFAULT_MODEL="qwen2.5-coder:1.5b"
    PROFILE="limited"
else
    DEFAULT_MODEL="qwen2.5:0.5b"
    PROFILE="minimal"
fi

echo "   RAM: ${RAM_GB}GB → Profile: $PROFILE"
echo "   Default model: $DEFAULT_MODEL"

# 8. Create config file if not exists
CONFIG_FILE="$CONFIG_DIR/config.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
    cat > "$CONFIG_FILE" << EOF
{
  "version": "2.0.0",
  "default_model": "$DEFAULT_MODEL",
  "router_model": "qwen2.5:0.5b",
  "voter_models": ["qwen2.5:0.5b", "tinyllama"],
  "offline_mode": false,
  "max_iterations": 12,
  "workspace": "$CONFIG_DIR/workspace",
  "auto_cleanup": true,
  "auto_download": true,
  "hardware_profile": "$PROFILE",
  "ram_gb": $RAM_GB
}
EOF
    echo "   Created: $CONFIG_FILE"
else
    echo "   Exists: $CONFIG_FILE (keeping existing config)"
fi

# 9. Create CLI wrapper symlink
echo ""
echo "🔗 Setting up CLI..."
chmod +x "$INSTALL_DIR/bin/swarm"
ln -sf "$INSTALL_DIR/bin/swarm" "$BIN_DIR/swarm"
echo "   Created: $BIN_DIR/swarm"

# 10. Add to PATH if needed
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "⚠️  $BIN_DIR is not in PATH"
    echo "   Add this to your ~/.bashrc:"
    echo "     export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "   Or run: source ~/.bashrc"
fi

# 11. Pull tiny model for routing
echo ""
echo "🤖 Pulling tiny model for routing (397MB)..."
if ! ollama list | grep -q "qwen2.5:0.5b"; then
    ollama pull qwen2.5:0.5b
    echo "   ✓ Downloaded qwen2.5:0.5b"
else
    echo "   ✓ qwen2.5:0.5b already installed"
fi

# 12. Success message
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "✅ Installation Complete!"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "Quick start:"
echo ""
echo "  swarm \"Create a hello_world function\""
echo ""
echo "  swarm --offline \"Create fibonacci\""
echo ""
echo "  swarm                    # Interactive mode"
echo ""
echo "Commands:"
echo "  swarm config             # View/edit config"
echo "  swarm models             # Manage models"
echo "  swarm hardware           # Hardware info"
echo "  swarm --help             # Full help"
echo ""
echo "Config: $CONFIG_FILE"
echo "Workspace: $CONFIG_DIR/workspace/"
echo ""

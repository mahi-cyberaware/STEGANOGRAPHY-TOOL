#!/bin/bash
# install.sh – Cross‑platform dependency installer for Stegano tool
# Supports: Kali/Debian/Ubuntu, Termux (Android), iSH (iOS), macOS, Windows (Git Bash/WSL)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔍 Detecting your platform...${NC}"

# Detect platform
PLATFORM="unknown"
if [[ -n "$PREFIX" && "$PREFIX" == *"/com.termux"* ]]; then
    PLATFORM="termux"
elif [[ -f "/etc/alpine-release" ]]; then
    PLATFORM="ios_ish"   # iSH runs Alpine
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [[ -f /etc/debian_version ]]; then
        PLATFORM="debian"
    else
        PLATFORM="linux_other"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    PLATFORM="windows_gitbash"
elif [[ -n "$WSL_DISTRO_NAME" ]]; then
    PLATFORM="wsl"
else
    PLATFORM="unknown"
fi

echo -e "${GREEN}✅ Detected: $PLATFORM${NC}"
echo ""

# Function to install Python packages via pip
install_pip_packages() {
    echo -e "${YELLOW}📦 Installing Python packages: pillow, numpy, cryptography...${NC}"
    if command -v pip3 &> /dev/null; then
        pip3 install --upgrade pillow numpy cryptography
    elif command -v pip &> /dev/null; then
        pip install --upgrade pillow numpy cryptography
    else
        echo -e "${RED}❌ pip not found. Please install pip first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Python packages installed.${NC}"
}

# ---------- Platform‑specific installations ----------
case $PLATFORM in
    termux)
        echo -e "${YELLOW}📱 Termux detected. Updating packages...${NC}"
        pkg update -y && pkg upgrade -y
        echo -e "${YELLOW}🔧 Installing Python, clang, and required libraries...${NC}"
        pkg install python clang libjpeg-turbo -y
        install_pip_packages
        ;;

    ios_ish)
        echo -e "${YELLOW}🍏 iSH (Alpine) detected. Updating repositories...${NC}"
        apk update
        echo -e "${YELLOW}🔧 Installing Python 3, pip, build tools, and libraries...${NC}"
        apk add python3 py3-pip gcc musl-dev python3-dev libffi-dev openssl-dev
        install_pip_packages
        ;;

    debian)
        echo -e "${YELLOW}🐧 Debian/Ubuntu/Kali detected. Updating package list...${NC}"
        sudo apt update -y
        echo -e "${YELLOW}🔧 Installing Python3, pip, Tkinter, and build tools...${NC}"
        sudo apt install -y python3 python3-pip python3-tk python3-dev libjpeg-dev zlib1g-dev
        install_pip_packages
        ;;

    linux_other)
        echo -e "${YELLOW}🐧 Generic Linux detected. Attempting to use apt (if available)...${NC}"
        if command -v apt &> /dev/null; then
            sudo apt update -y
            sudo apt install -y python3 python3-pip python3-tk python3-dev
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip python3-tkinter python3-devel
        elif command -v pacman &> /dev/null; then
            sudo pacman -Syu --noconfirm python python-pip tk
        else
            echo -e "${RED}⚠️ No known package manager found. Please install Python 3, pip, and Tkinter manually.${NC}"
        fi
        install_pip_packages
        ;;

    macos)
        echo -e "${YELLOW}🍎 macOS detected. Checking Homebrew...${NC}"
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}Homebrew not found. Install it first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
            exit 1
        fi
        echo -e "${YELLOW}🔧 Installing Python and Tkinter via Homebrew...${NC}"
        brew install python python-tk
        install_pip_packages
        ;;

    windows_gitbash|wsl)
        echo -e "${YELLOW}🪟 Windows environment (Git Bash / WSL) detected.${NC}"
        if [[ "$PLATFORM" == "wsl" ]]; then
            echo -e "${YELLOW}Using WSL – following Debian/Ubuntu steps...${NC}"
            sudo apt update -y
            sudo apt install -y python3 python3-pip python3-tk python3-dev
            install_pip_packages
        else
            echo -e "${YELLOW}⚠️ Native Windows (Git Bash) – manual installation recommended.${NC}"
            echo -e "${YELLOW}Please install Python from https://python.org and then run:${NC}"
            echo "  pip install pillow numpy cryptography"
            echo -e "${GREEN}After that, run: python stego_crossplatform.py${NC}"
            exit 0
        fi
        ;;

    unknown)
        echo -e "${RED}❌ Could not detect your platform automatically.${NC}"
        echo -e "${YELLOW}Please install Python 3.8+, pip, and then run:${NC}"
        echo "  pip install pillow numpy cryptography"
        echo -e "${YELLOW}If you want GUI, also install Tkinter for your system.${NC}"
        exit 1
        ;;
esac

# Final verification
echo ""
echo -e "${GREEN}🔍 Verifying installation...${NC}"
python3 -c "import PIL, numpy, cryptography; print('✅ All modules loaded successfully.')" 2>/dev/null || {
    echo -e "${RED}❌ Verification failed. Some modules are missing.${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}✅ Installation completed successfully!${NC}"
echo -e "${GREEN}🚀 Now run: python3 stego_crossplatform.py${NC}"
echo -e "${GREEN}================================================================${NC}"

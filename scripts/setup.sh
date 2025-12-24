set -euo pipefail

# Args: UTORID and PASSWORD
if [[ $# -lt 2 ]]; then
  echo "Usage: sh scripts/setup.sh <your_utorid> <your_password>" >&2
  exit 1
fi
UTORID="$1"
PASSWORD="$2"

# Fallback defaults if not set in .env
LOGIN_CREDENTIALS_PATH="${LOGIN_CREDENTIALS_PATH:-./secrets/login_credentials.txt}"
BYPASS_CODES_PATH="${BYPASS_CODES_PATH:-./secrets/bypass_codes.txt}"

SECRETS_DIR="$(dirname "$LOGIN_CREDENTIALS_PATH")"
CREDENTIALS_FILE="$LOGIN_CREDENTIALS_PATH"
BYPASS_FILE="$BYPASS_CODES_PATH"

# Ensure secrets directory
mkdir -p "$SECRETS_DIR"

# Seed secrets files
printf "%s\n%s\n" "$UTORID" "$PASSWORD" > "$CREDENTIALS_FILE"
touch "$BYPASS_FILE"
echo "[ok] Wrote credentials to $CREDENTIALS_FILE"

# Create python venv and install requirements 
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
  echo "[ok] Created .venv"
fi

# Activate venv and install
VENV_PY=".venv/bin/python"
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -r requirements.txt
"$VENV_PY" -m playwright install
echo "[ok] Installed python dependencies into .venv and activated"

echo "[done] Environment setup complete."
# Secrets Management

## Preferred Method: macOS Keychain

Store cross-project secrets in macOS Keychain using the `security` command. Encrypted at rest, survives reboots, works offline.

### Helper Script

Create `~/bin/secret`:

```bash
#!/bin/bash
# Minimal secrets manager using macOS Keychain
case "$1" in
  set)  security add-generic-password -a "$USER" -s "$2" -w "$3" -U ;;
  get)  security find-generic-password -a "$USER" -s "$2" -w 2>/dev/null ;;
  list) security dump-keychain | grep -A4 "class: \"genp\"" | grep svce | sed 's/.*="//;s/"//' | sort -u ;;
  *)    echo "Usage: secret [set|get|list] KEY [VALUE]" ;;
esac
```

### Usage

```bash
# Store a secret
secret set OPENAI_API_KEY "sk-..."

# Retrieve in scripts
export OPENAI_API_KEY=$(secret get OPENAI_API_KEY)

# List all stored secrets
secret list
```

### Usage in Python

```python
import subprocess
def get_secret(name):
    result = subprocess.run(['secret', 'get', name], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None
```

### What NOT to Store in Keychain

* Vercel OIDC tokens (auto-generated, project-specific)
* Short-lived tokens that refresh automatically
* Secrets that must be in .env.local for framework detection (Next.js, etc.)

<!--
Alternative: use the ~/.config/secrets/ directory pattern (see STORAGE-OPTIONS.md)
Both approaches work; Keychain is more secure, flat files are simpler to sync
-->

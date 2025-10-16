# Deployment Guide

## Development Deployment to Home Assistant

Quick deployment script for syncing the integration to your Home Assistant instance during development.

### Prerequisites

1. **Home Assistant with SSH add-on installed and running**
2. **SSH access configured** (password or SSH keys)
3. **Home Assistant OS or Supervised** (uses `/config` directory)

### Quick Start

#### Option 1: Use defaults (homeassistant.local)

```bash
./deploy-dev.sh
```

#### Option 2: Specify your HA host

```bash
HA_HOST=192.168.1.100 ./deploy-dev.sh
```

#### Option 3: Create a configuration file

```bash
# Copy example config
cp .env.example .env

# Edit with your details
nano .env

# Deploy
source .env && ./deploy-dev.sh
```

### Configuration Options

Set these as environment variables or in your `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `HA_HOST` | `homeassistant.local` | Hostname or IP of HA |
| `HA_USER` | `root` | SSH username |
| `HA_PORT` | `22` | SSH port |
| `HA_CONFIG_DIR` | `/config` | HA config directory |

### Example Configurations

#### Home Assistant with default mDNS

```bash
HA_HOST=homeassistant.local HA_USER=root HA_PORT=22 ./deploy-dev.sh
```

#### Home Assistant on specific IP

```bash
HA_HOST=192.168.1.100 HA_USER=root HA_PORT=22 ./deploy-dev.sh
```

#### Home Assistant with custom SSH port

```bash
HA_HOST=192.168.1.100 HA_PORT=22222 ./deploy-dev.sh
```

### What the Script Does

1. ✅ Tests SSH connection to your Home Assistant
2. 📦 Syncs `custom_components/bosch_ebike/` to HA (via rsync if available, falls back to scp)
3. 🔄 Optionally restarts Home Assistant to load changes
4. 📊 Shows status and next steps

### After Deployment

1. **Wait for HA to restart** (~30 seconds)
2. **Add the integration:**
   - Settings → Devices & Services
   - Add Integration → Search "Bosch eBike"
   - Follow OAuth flow

### Development Workflow

```bash
# 1. Make changes to integration files
nano custom_components/bosch_ebike/api.py

# 2. Deploy to Home Assistant
./deploy-dev.sh

# 3. Test in Home Assistant UI

# 4. Repeat!
```

### Troubleshooting

#### Cannot connect via SSH

**Check SSH add-on is running:**

1. Home Assistant → Settings → Add-ons
2. SSH add-on should be "Started"
3. Check the port in add-on configuration

**Test SSH manually:**

```bash
ssh root@homeassistant.local
# or
ssh root@192.168.1.100
```

**Configure SSH keys (optional but recommended):**

```bash
# Generate key if you don't have one
ssh-keygen -t ed25519

# Copy to Home Assistant
ssh-copy-id root@homeassistant.local
```

#### Wrong directory structure

If you're using Home Assistant Container (Docker), you might need:

```bash
HA_CONFIG_DIR=/config ./deploy-dev.sh
```

For Home Assistant Core (Python venv):

```bash
HA_CONFIG_DIR=/home/homeassistant/.homeassistant ./deploy-dev.sh
```

#### Integration doesn't appear after deployment

1. **Verify files were copied:**

   ```bash
   ssh root@homeassistant.local "ls -la /config/custom_components/bosch_ebike/"
   ```

2. **Check for errors in logs:**

   ```bash
   ssh root@homeassistant.local "ha core logs"
   ```

3. **Restart Home Assistant:**
   - Settings → System → Restart
   - Or: `ssh root@homeassistant.local "ha core restart"`

4. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (Linux/Windows) or Cmd+Shift+R (Mac)

#### Permission denied

Make sure deploy script is executable:

```bash
chmod +x deploy-dev.sh
```

### Alternative: Manual Deployment

If the script doesn't work for your setup, you can deploy manually:

#### Via SSH/SCP

```bash
# Copy files
scp -r custom_components/bosch_ebike root@homeassistant.local:/config/custom_components/

# Restart Home Assistant
ssh root@homeassistant.local "ha core restart"
```

#### Via FTP

1. Install "Samba share" add-on in Home Assistant
2. Connect via file browser or FTP client
3. Copy `custom_components/bosch_ebike` to `/config/custom_components/`
4. Restart Home Assistant

#### Via Home Assistant File Editor

1. Install "File editor" add-on
2. Manually create directory structure
3. Copy-paste file contents
4. Restart Home Assistant

(Not recommended for development - too slow!)

### Production Deployment

For production use, users should install via:

- **HACS** (Home Assistant Community Store) - recommended
- **Manual installation** - copy to custom_components and restart

The `deploy-dev.sh` script is for development iteration only.

---

**Next:** After successful deployment, see [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) for testing Phase 1.

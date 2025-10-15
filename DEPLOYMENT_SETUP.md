# 🚀 Deployment Setup Complete!

## What We Created

### 1. `deploy-dev.sh` - Automated Deployment Script

A smart deployment script that:
- ✅ Tests SSH connection to your Home Assistant
- ✅ Syncs integration files via rsync (fast and efficient)
- ✅ Excludes unnecessary files (`__pycache__`, `.pyc`, etc.)
- ✅ Optionally restarts Home Assistant
- ✅ Shows clear status and next steps
- ✅ Color-coded output for easy reading

### 2. `deploy.conf.example` - Configuration Template

Template for your Home Assistant connection details.

### 3. `DEPLOYMENT.md` - Complete Deployment Guide

Comprehensive documentation covering:
- Quick start examples
- Configuration options
- Troubleshooting
- Alternative deployment methods
- Development workflow

### 4. Updated `README.md`

Added deployment section with quick reference.

---

## 🎯 How to Use (Your First Deployment)

### Step 1: Configure (Choose One Option)

#### Option A: Use Defaults (if using homeassistant.local)

Just run the script - it will use `homeassistant.local` as the host:

```bash
./deploy-dev.sh
```

#### Option B: Specify Your HA IP/Hostname

```bash
HA_HOST=192.168.1.100 ./deploy-dev.sh
```

#### Option C: Create Configuration File (Recommended for repeated use)

```bash
# Copy the example config
cp .env.example .env

# Edit with your Home Assistant details
nano .env
# Change HA_HOST to your IP or hostname
# Adjust port if needed

# Deploy using your config
source .env && ./deploy-dev.sh
```

### Step 2: What to Expect

The script will:

1. **Test connection:**
   ```
   ℹ Testing SSH connection...
   ✓ SSH connection successful
   ```

2. **Sync files:**
   ```
   ℹ Syncing integration files...
   ✓ Files synced successfully
   ```

3. **Ask about restart:**
   ```
   ⚠ Restart Home Assistant to load changes? (y/N):
   ```
   
   - Say **Yes** to restart automatically
   - Say **No** to restart manually later

4. **Show completion:**
   ```
   ✓ Deployment complete!
   
   ℹ Next steps:
     1. Wait for Home Assistant to restart
     2. Go to: Settings → Devices & Services
     3. Add Integration → Search for 'Bosch eBike'
   ```

### Step 3: Add Integration in Home Assistant

1. **Wait for restart** (~30 seconds)
2. **Open Home Assistant** in your browser
3. **Go to:** Settings → Devices & Services
4. **Click:** Add Integration
5. **Search:** "Bosch eBike"
6. **Follow:** OAuth flow (will open Bosch login in browser)

---

## 🔧 Common Configurations

### Home Assistant on Unraid VM (Your Setup)

If your HA is on `homeassistant.local`:
```bash
./deploy-dev.sh
```

If you know the IP:
```bash
HA_HOST=192.168.1.50 ./deploy-dev.sh
```

### Home Assistant with Custom SSH Port

If you changed the SSH port:
```bash
HA_HOST=192.168.1.50 HA_PORT=22222 ./deploy-dev.sh
```

### Home Assistant Supervised on Different Path

If your config is not at `/config`:
```bash
HA_CONFIG_DIR=/usr/share/hassio/homeassistant ./deploy-dev.sh
```

---

## 📋 Prerequisites Checklist

Before running the deployment:

- [ ] **SSH add-on installed** in Home Assistant
  - Settings → Add-ons → SSH Server
  - Make sure it's "Started"
  
- [ ] **Know your HA hostname or IP**
  - Check in Unraid or your router
  - Usually `homeassistant.local` or an IP like `192.168.1.x`
  
- [ ] **SSH access working**
  - Test: `ssh root@homeassistant.local`
  - Enter password when prompted
  - (Optional: Set up SSH keys for password-less access)

---

## 🐛 Troubleshooting

### "Cannot connect to Home Assistant via SSH"

**Check these:**

1. **Is SSH add-on running?**
   - Home Assistant → Settings → Add-ons → SSH Server
   - Should show "Started"

2. **Can you SSH manually?**
   ```bash
   ssh root@homeassistant.local
   # or
   ssh root@192.168.1.100
   ```

3. **Is the hostname correct?**
   - Try IP address instead: `HA_HOST=192.168.1.100 ./deploy-dev.sh`
   - Check Unraid dashboard for the VM's IP

4. **Is the port correct?**
   - Check SSH add-on configuration for the port
   - Try: `HA_PORT=22 ./deploy-dev.sh`

### "Permission denied"

Make the script executable:
```bash
chmod +x deploy-dev.sh
```

### Files synced but integration not showing

1. **Check files arrived:**
   ```bash
   ssh root@homeassistant.local "ls -la /config/custom_components/bosch_ebike/"
   ```

2. **Restart Home Assistant:**
   - Settings → System → Restart
   - Or: `ssh root@homeassistant.local "ha core restart"`

3. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

4. **Check logs:**
   ```bash
   ssh root@homeassistant.local "ha core logs"
   ```

---

## 💡 Development Workflow

Once set up, your workflow is super simple:

```bash
# 1. Make changes to any integration files
nano custom_components/bosch_ebike/api.py

# 2. Deploy (takes ~5 seconds)
./deploy-dev.sh

# 3. Restart Home Assistant when prompted

# 4. Test changes immediately

# 5. Repeat!
```

The rsync will only transfer changed files, making iterations fast!

---

## 🎯 What's Next

1. **Test deployment** - Run `./deploy-dev.sh` now!
2. **Add integration** - Follow OAuth flow in HA
3. **Check logs** - See if Phase 1 works
4. **Report back** - Let me know how it goes
5. **Continue to Phase 2** - Data coordinator when ready

---

## 📝 Files in This Setup

```
.
├── deploy-dev.sh          # ← Deployment script (executable)
├── deploy.conf.example    # ← Configuration template
├── DEPLOYMENT.md          # ← Full deployment guide
├── DEPLOYMENT_SETUP.md    # ← This file (quick start)
└── .env                   # ← Your config (create from example)
    └── (gitignored)
```

---

**Ready?** Run your first deployment:

```bash
./deploy-dev.sh
```

Let me know how it goes! 🚀


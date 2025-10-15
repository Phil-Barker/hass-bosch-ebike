# SSH Connection Troubleshooting

## Current Issue

Getting "Permission denied (publickey)" when trying to connect to Home Assistant.

## Your Public Key

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKtX3Y7+5qx6ZDhDZkrMcZDmmcvjXgZ/ZklDUVkqwNDZ mail@phil-barker.com
```

## Solution Steps

### Option 1: Enable Password Authentication (Recommended for Testing)

1. **Open Home Assistant SSH Add-on Configuration**
   - Settings → Add-ons → Terminal & SSH
   - Click "Configuration" tab

2. **Add this configuration:**

   ```yaml
   authorized_keys:
     - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKtX3Y7+5qx6ZDhDZkrMcZDmmcvjXgZ/ZklDUVkqwNDZ mail@phil-barker.com
   password: ""  # Leave empty to keep password auth enabled
   ```

3. **Make sure these settings are configured:**
   - Port: 22
   - Allow Agent Forwarding: true (optional)
   - Allow Remote Port Forwarding: false
   - Allow TCP Forwarding: false

4. **Save and restart the SSH add-on**

5. **Try connecting with password:**

   ```bash
   ssh root@192.168.1.220
   # Enter your Home Assistant password when prompted
   ```

### Option 2: Fix SSH Key Configuration

If you want key-only authentication:

1. **Check the SSH add-on configuration format:**

   ```yaml
   authorized_keys:
     - >-
       ssh-ed25519
       AAAAC3NzaC1lZDI1NTE5AAAAIKtX3Y7+5qx6ZDhDZkrMcZDmmcvjXgZ/ZklDUVkqwNDZ
       mail@phil-barker.com
   password: ""
   ```

   **Important:** The key might need to be on multiple lines with proper YAML formatting!

2. **Or try without line breaks:**

   ```yaml
   authorized_keys:
     - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKtX3Y7+5qx6ZDhDZkrMcZDmmcvjXgZ/ZklDUVkqwNDZ mail@phil-barker.com"
   ```

3. **Save and restart SSH add-on**

4. **Test connection:**

   ```bash
   ssh -v root@192.168.1.220
   ```

   The `-v` flag shows verbose output to help debug.

### Option 3: Use Different SSH Add-on

If the official SSH add-on is giving trouble, try:

**"SSH & Web Terminal" add-on** (more user-friendly):

1. Settings → Add-ons → Add-on Store
2. Search for "SSH & Web Terminal"
3. Install
4. Configure similarly but with easier UI

### Checking Your Current SSH Config

**Try verbose SSH to see what's happening:**

```bash
ssh -vvv root@192.168.1.220
```

Look for lines like:

- "Offering public key:" - Shows if your key is being tried
- "Server refused our key" - Key is wrong format or not in authorized_keys
- "No more authentication methods to try" - No password auth enabled

### Common Issues

#### 1. YAML Formatting in HA Config

The SSH add-on is picky about YAML format. Make sure:

- No extra spaces
- Proper indentation
- Key is all on one line OR properly multiline with `>-`

#### 2. Wrong Username

Home Assistant SSH is accessed as `root`, not `homeassistant` or your HA username.

#### 3. SSH Add-on Not Using Port 22

Check the add-on config - it might be using a different port like 22222.

#### 4. Firewall/Network Issue

Test if you can reach the port:

```bash
telnet 192.168.1.220 22
# or
nc -zv 192.168.1.220 22
```

### Quick Fix: Use Password Auth for Now

**Simplest solution for development:**

1. In SSH add-on config, set:

   ```yaml
   password: ""
   ```

   Leave it empty or blank - this ENABLES password authentication!

2. Remove or comment out `authorized_keys` for now:

   ```yaml
   # authorized_keys:
   #   - your key here
   password: ""
   ```

3. Connect with your HA password:

   ```bash
   ssh root@192.168.1.220
   # Enter password when prompted
   ```

4. **This is fine for development on your local network!**

### After Getting SSH Working

Once you can SSH in, you can:

1. **Test deployment:**

   ```bash
   HA_HOST=192.168.1.220 ./deploy-dev.sh
   ```

2. **Set up SSH keys properly later** (optional for dev)

3. **Continue with integration testing!**

## Recommended Next Steps

1. **Enable password auth** (quickest)
2. **Test SSH manually:** `ssh root@192.168.1.220`
3. **Test deployment:** `HA_HOST=192.168.1.220 ./deploy-dev.sh`
4. **Add integration in HA UI**

## Alternative: Use Different Deployment Method

If SSH continues to be problematic, you can temporarily use:

### Samba Share Method

1. Install "Samba share" add-on in HA
2. Mount the share on your machine
3. Copy files manually or with rsync over SMB

### FTP Method  

1. Install FTP add-on
2. Connect with FTP client
3. Upload files

But SSH is definitely the best once working! Let's get it sorted.

---

**Try this now:**

1. Set `password: ""` in SSH add-on config (enables password auth)
2. Restart SSH add-on
3. Run: `ssh root@192.168.1.220`
4. Enter your HA password

Let me know what happens!

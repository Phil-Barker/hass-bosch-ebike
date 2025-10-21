# Authentication Guide for Bosch eBike Flow Integration

This guide will help you through the authentication process step-by-step.

## ⚠️ **CRITICAL: Use a Desktop/Laptop Browser**

**DO NOT use your phone or tablet!** The authentication flow requires browser developer tools, which are not available on mobile devices. Additionally, mobile devices will automatically open the Bosch Flow app when redirected, preventing you from seeing the authorization code.

**Supported browsers:**

- ✅ Chrome (Windows, Mac, Linux)
- ✅ Firefox (Windows, Mac, Linux)
- ✅ Edge (Windows, Mac)
- ✅ Safari (Mac)
- ❌ Mobile browsers (iPhone, iPad, Android) - **WILL NOT WORK**

## Step-by-Step Instructions

### Step 1: Start the Integration Setup

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **"+ ADD INTEGRATION"**
3. Search for **"Bosch eBike Flow"**
4. Click on it to start the setup

### Step 2: Copy the Authorization URL

You'll see a long URL starting with `https://identity.bosch.com/...`

**DO NOT click on it directly!**

1. **Highlight the entire URL** by triple-clicking on it
2. **Copy it** (Ctrl+C on Windows/Linux, Cmd+C on Mac)
3. **Open a new browser tab**
4. **Paste the URL** into the address bar
5. **Press Enter**

### Step 3: Log In to Bosch

1. You'll be taken to the Bosch login page
2. Enter your **Bosch eBike Flow** account email and password
   - This is the same account you use in the Flow mobile app
3. Click **"Sign In"** or **"Log In"**

### Step 4: The Redirect "Failure" (This is Normal!)

After logging in, one of two things will happen:

#### Option A: Blank page or error message

- This is **perfect!** Continue to Step 5.

#### Option B: Page with "Cannot open page" or similar

- This is also **perfect!** Continue to Step 5.

#### Option C: Nothing happens

- The page might just sit there. That's okay, continue to Step 5.

Don't worry - this "failure" is expected because your browser doesn't know how to handle the `onebikeapp-ios://` redirect.

### Step 5: Open Developer Tools

Now we need to find the authorization code hidden in the failed redirect:

**Windows/Linux:**

- Press **F12**, or
- Right-click anywhere on the page → **"Inspect"**, or
- Press **Ctrl+Shift+I**

**Mac:**

- Press **Cmd+Option+I**, or
- Right-click anywhere on the page → **"Inspect Element"**

A panel will appear at the bottom or side of your browser window.

### Step 6: Find the Network Tab

1. Look at the top of the developer tools panel
2. Click on the **"Network"** tab
   - It might be between other tabs like "Elements", "Console", "Sources"

### Step 7: Find the Authorization Code

Look for a request in the list that starts with **"onebikeapp-ios"** or **"oauth2redirect"**

**Chrome/Edge:**

1. Look in the "Name" column for `onebikeapp-ios`
2. Click on it
3. Look at the **"Headers"** tab on the right
4. Find **"Request URL"** at the top
5. You'll see: `onebikeapp-ios://com.bosch.ebike.onebikeapp/oauth2redirect?code=XXXXX`

**Firefox:**

1. Look for `onebikeapp-ios` in the left column
2. Click on it
3. Look at the **"URL"** field on the right
4. You'll see: `onebikeapp-ios://com.bosch.ebike.onebikeapp/oauth2redirect?code=XXXXX`

**Safari:**

1. Look for `onebikeapp-ios` in the list
2. Click on it
3. The URL will be shown at the top
4. You'll see: `onebikeapp-ios://com.bosch.ebike.onebikeapp/oauth2redirect?code=XXXXX`

### Step 8: Copy the Code

The code is the long string of characters after `code=` in the URL.

**Example URL:**

```text
onebikeapp-ios://com.bosch.ebike.onebikeapp/oauth2redirect?code=eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1...
```

**What to copy:** Only copy everything after `code=`, which would be:

```text
eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1...
```

**The code will be LONG** - usually 500-1000+ characters. That's normal!

### Step 9: Paste the Code into Home Assistant

1. Go back to your Home Assistant tab
2. **Paste the code** into the **"Authorization Code"** field
3. Click **"Submit"**

### Step 10: Select Your Bike

If you have multiple eBikes registered in your Flow account:

1. Select which bike you want to add
2. Click **"Submit"**

Done! Your eBike should now appear in Home Assistant.

## Common Issues

### "I don't see onebikeapp-ios in the Network tab"

**Try this:**

1. Make sure you're on the **Network** tab (not Console or Elements)
2. Scroll through the list - it might be near the bottom
3. Try refreshing the page (F5) and look for new requests
4. The request might be marked in red (that's normal - it's a "failed" redirect)
5. Look for anything that says "oauth2redirect" or starts with "onebikeapp"

### "I used my phone and it opened the Flow app"

This is why we say **you must use a desktop browser!** Mobile devices intercept the redirect and open the app automatically, so you never see the code.

**Solution:** Start over on your desktop/laptop computer.

### "My code doesn't work / Authentication failed"

This is the most common issue. Here's how to diagnose:

#### 1. Check Home Assistant Logs

- Go to **Settings** → **System** → **Logs**
- Search for `bosch_ebike` or `authentication`
- Look for error messages like:
  - `Token exchange failed (400): invalid_grant` - **Code expired or already used** (most common!)
  - `Token exchange failed (401)` - Authentication issue
  - Other specific errors

#### 2. Common causes

##### Code expired (most common)

- OAuth codes typically expire in **60-90 seconds**
- From the moment you see the failed redirect, you have ~1 minute
- **Solution:** Start over and paste the code immediately

##### Code already used

- You can only use each code once
- If you tried before and it failed, you need a new code
- **Solution:** Start over from Step 1 to get a fresh code

##### Missing characters

- The code is **VERY long** (500-1000+ characters)
- It contains dots/periods (.) and hyphens (-) - these are important!
- **Solution:** Triple-click the URL to select all, or carefully drag-select the entire code

##### Extra characters

- Make sure when you paste, there are no:
  - Spaces at the beginning or end
  - Line breaks or newlines
  - The text `code=` itself (just the value after it)
  - URL encoding like `%3D` or `%2F`

#### 3. How to succeed

1. Have Home Assistant config flow open and ready
2. Open browser with Developer Tools already open on Network tab
3. Paste the auth URL and log in quickly
4. As soon as you see the failed redirect, copy the code immediately
5. Paste it in Home Assistant within 30 seconds
6. Click Submit

#### 4. Still not working?

- Share the error from Home Assistant logs
- Report on [GitHub Issue #2](https://github.com/Phil-Barker/hass-bosch-ebike/issues/2)

### "I don't have a desktop/laptop computer"

Unfortunately, this authentication method requires desktop browser developer tools. Alternatives:

1. **Borrow a friend's computer** - you only need to do this once during setup
2. **Use a work computer** - the setup only takes 5 minutes
3. **Remote desktop** - If you have a remote desktop server, you can use it from your phone/tablet
4. **Wait for a mobile-friendly solution** - We're exploring options for future versions

## Video Tutorial

A video tutorial showing this process will be available soon.

## Still Need Help?

- 🐛 [Report an issue on GitHub](https://github.com/Phil-Barker/hass-bosch-ebike/issues)
- 💬 [Ask in GitHub Discussions](https://github.com/Phil-Barker/hass-bosch-ebike/discussions)
- 📧 Include screenshots if possible!

## Technical Details (For Developers)

The integration uses OAuth 2.0 with PKCE (Proof Key for Code Exchange) to authenticate with Bosch's identity service.

**Why this manual process?**

Bosch's OAuth implementation uses a mobile app deep link (`onebikeapp-ios://`) as the redirect URI. Since Home Assistant can't register as a handler for this URL scheme, the redirect "fails" in the browser, but the authorization code is still visible in the network request. This is a common workaround for reverse-engineered APIs that weren't designed for third-party integrations.

**Future improvements:**

Potential solutions being explored:

- Custom redirect URI (requires finding/registering one with Bosch)
- Proxy server to intercept redirects (adds complexity/hosting)
- Direct API token generation (if Bosch provides a developer program)

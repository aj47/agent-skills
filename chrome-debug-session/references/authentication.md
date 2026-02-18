# Authentication Patterns

Login flows, session persistence, and auth handling for `agent-browser --cdp 9222`.

**Related**: [../SKILL.md](../SKILL.md) for core workflow, [common-patterns.md](common-patterns.md) for general patterns.

## Your Chrome Profile Advantage

Since you connect to a Chrome instance with `--user-data-dir="$HOME/chrome-debug-profile"`, you're typically **already logged in** to most sites. Just navigate directly:

```bash
agent-browser --cdp 9222 open https://app.example.com/dashboard
agent-browser --cdp 9222 snapshot -i  # Already authenticated
```

If you get redirected to a login page, see the flows below.

## Basic Login Flow

```bash
agent-browser --cdp 9222 open https://app.example.com/login
agent-browser --cdp 9222 wait --load networkidle
agent-browser --cdp 9222 snapshot -i
# @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Sign In"

agent-browser --cdp 9222 fill @e1 "user@example.com"
agent-browser --cdp 9222 fill @e2 "password123"
agent-browser --cdp 9222 click @e3
agent-browser --cdp 9222 wait --load networkidle

# Verify — should be dashboard, not login
agent-browser --cdp 9222 get url
```

Once logged in via the debug Chrome profile, the session persists across browser restarts.

## Saving and Restoring State

For sites where the Chrome profile doesn't preserve auth (or for sharing state):

```bash
# After logging in, save state
agent-browser --cdp 9222 state save ./auth-state.json

# Later, restore it
agent-browser --cdp 9222 state load ./auth-state.json
agent-browser --cdp 9222 open https://app.example.com/dashboard
```

**Security note**: State files contain session tokens — don't commit them.

## OAuth / SSO Flows

```bash
# Start OAuth flow
agent-browser --cdp 9222 open https://app.example.com/auth/google

# Wait for redirect to Google
agent-browser --cdp 9222 wait --url "**/accounts.google.com**"
agent-browser --cdp 9222 snapshot -i

# Fill Google credentials
agent-browser --cdp 9222 fill @e1 "user@gmail.com"
agent-browser --cdp 9222 click @e2  # Next
agent-browser --cdp 9222 wait 2000
agent-browser --cdp 9222 snapshot -i
agent-browser --cdp 9222 fill @e3 "password"
agent-browser --cdp 9222 click @e4  # Sign in

# Wait for redirect back
agent-browser --cdp 9222 wait --url "**/app.example.com**"
```

**Tip**: If you're already logged into Google in the debug Chrome profile, the OAuth flow may complete automatically with just a consent click.

## Two-Factor Authentication (2FA)

2FA requires manual intervention — use the visible Chrome window:

```bash
# Fill credentials
agent-browser --cdp 9222 open https://app.example.com/login
agent-browser --cdp 9222 snapshot -i
agent-browser --cdp 9222 fill @e1 "user@example.com"
agent-browser --cdp 9222 fill @e2 "password123"
agent-browser --cdp 9222 click @e3

# Wait for user to complete 2FA in the Chrome window
echo "Complete 2FA in the Chrome debug window..."
agent-browser --cdp 9222 wait --url "**/dashboard" --timeout 120000
```

## Cookie-Based Auth

```bash
# Set an auth cookie directly
agent-browser --cdp 9222 cookies set session_token "abc123xyz"
agent-browser --cdp 9222 open https://app.example.com/dashboard

# View all cookies
agent-browser --cdp 9222 cookies

# Clear cookies (force re-login)
agent-browser --cdp 9222 cookies clear
```

## HTTP Basic Auth

```bash
agent-browser --cdp 9222 set credentials username password
agent-browser --cdp 9222 open https://protected.example.com
```

## Checking Auth Status

Quick way to verify you're authenticated:

```bash
agent-browser --cdp 9222 open https://app.example.com/dashboard
agent-browser --cdp 9222 get url
# If URL is still /dashboard → authenticated
# If URL redirected to /login → need to log in
```


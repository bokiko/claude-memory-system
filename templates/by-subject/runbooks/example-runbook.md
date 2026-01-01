---
title: Example Runbook
category: runbooks
tags: [howto, operations]
updated: 2024-01-01
---

# Example Runbook

Step-by-step guide for common operations.

## Prerequisites

- Access to server
- Required permissions

## Steps

### Step 1: Prepare

```bash
# Check current state
systemctl status service-name
```

### Step 2: Execute

```bash
# Perform the operation
sudo systemctl restart service-name
```

### Step 3: Verify

```bash
# Confirm success
curl http://localhost:8080/health
```

## Troubleshooting

### Issue: Service won't start

Check logs:
```bash
journalctl -u service-name -n 50
```

### Issue: Connection refused

Verify firewall:
```bash
sudo ufw status
```

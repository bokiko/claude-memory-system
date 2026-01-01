---
title: Deployment Guide Template
category: deployment
tags: [deployment, production, devops, template]
---

# Project Deployment

## Environments

| Environment | URL | Branch |
|-------------|-----|--------|
| Development | dev.example.com | develop |
| Staging | staging.example.com | staging |
| Production | example.com | main |

## Prerequisites

- [ ] SSH access to servers
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Tests passing

## Deploy Steps

### 1. Pre-deploy Checks

```bash
# Run tests
npm test

# Build
npm run build

# Check for security issues
npm audit
```

### 2. Deploy to Staging

```bash
git checkout staging
git merge develop
git push origin staging
```

### 3. Verify Staging

- [ ] Check main features work
- [ ] Review error logs
- [ ] Test critical user flows

### 4. Deploy to Production

```bash
git checkout main
git merge staging
git push origin main
```

### 5. Post-deploy

- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify critical endpoints

## Rollback

If something goes wrong:

```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or deploy specific version
git checkout v1.2.3
git push origin main --force
```

## Contacts

- On-call: #oncall-channel
- DevOps: devops@example.com

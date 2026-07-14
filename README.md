# InsightSwarm

Welcome to the central repository for **InsightSwarm**.

## Project Plan

The implementation tracker lives in [plan.md](plan.md). Section 1 lists the work that is already completed, and Section 2 lists the remaining work that still needs to be implemented.

This project uses a collaborative Git workflow to keep the `main` branch stable and production-ready.

## 🚀 Team Git Workflow

To maintain a clean and reliable history, please follow these rules:

1. **Do not push directly to `main`.**
2. Create and work on a **feature branch**.
3. Open a Pull Request (PR) for review before merging.

## 🛠 Initial Repository Setup

Run these commands once when setting up the project locally:

```bash
git init
git branch -M main
git remote add origin https://github.com/ArshilTech/insightswarm-sipher-capstone.git
git fetch origin
git pull origin main
```

## 📦 Install Dependencies

This project uses `uv` for fast, reliable Python dependency management:

```bash
pip install uv
uv sync
```

This will install all required dependencies specified in the project configuration.

## 🌿 Create a Feature Branch

Use a consistent branch naming convention:

```bash
git checkout -b <your-name>/feature-<short-description>
```

Example:

```bash
git checkout -b arshil/feature-auth-flow
```

## 📤 Push Your Branch

Push your feature branch to GitHub:

```bash
git push -u origin <your-name>/feature-<short-description>
```

## ✅ Pull Request Process

Before opening a PR:

- Pull latest changes from `main`
- Resolve any merge conflicts locally
- Ensure your code is tested and linted
- Add a clear PR title and description

After approval, your PR can be merged by a maintainer.

---

If you are unsure about the workflow, ask the team before pushing changes.

## 🔄 Keep Your Branch Up-to-Date

Before you start working on your branch, pull the latest changes from `main` so you can merge any upstream updates into your branch.

Make sure you are on your branch before executing these commands:

```bash
# verify current branch
git branch --show-current

# fetch latest refs
git fetch

# check status (if error, consult the team lead)
git status

# switch to main and pull latest
git switch main
git pull origin main

# switch back to your branch and merge main
git switch <yourBranchName>
git merge main
```

## 💾 Commit and Push Your Changes

Once you've finished adding your features and resolved any merge conflicts, commit and push your changes:

```bash
git add .
git commit -m "Your message"
git push origin <yourBranchName>
```

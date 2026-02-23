# GitHub Repository Setup Guide

This guide walks you through setting up your Black-Litterman portfolio optimization project on GitHub.

## Prerequisites

- Git installed on your computer ([Download Git](https://git-scm.com/downloads))
- GitHub account ([Create account](https://github.com/join))
- Command line / Terminal access

## Step 1: Create GitHub Repository

### Option A: Via GitHub Website

1. Go to [GitHub](https://github.com) and log in
2. Click the "+" icon in the top right → "New repository"
3. Fill in the details:
   - **Repository name**: `BL-Portfolio-optimization`
   - **Description**: "Black-Litterman portfolio optimization with factor models"
   - **Visibility**: Choose "Public" (recommended) or "Private"
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click "Create repository"

### Option B: Via GitHub CLI (if installed)

```bash
gh repo create BL-Portfolio-optimization --public --description "Black-Litterman portfolio optimization with factor models"
```

## Step 2: Initialize Local Repository

Navigate to your project directory and initialize Git:

```bash
cd BL-Portfolio-optimization
git init
```

## Step 3: Configure Git (First Time Only)

If you haven't configured Git before:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 4: Add Files to Git

Add all files to the repository:

```bash
git add .
```

Check what will be committed:

```bash
git status
```

## Step 5: Create Initial Commit

Commit the files with a descriptive message:

```bash
git commit -m "Initial commit: Complete Black-Litterman portfolio optimization framework"
```

## Step 6: Link to GitHub Repository

Replace `yourusername` with your actual GitHub username:

```bash
git remote add origin https://github.com/yourusername/BL-Portfolio-optimization.git
```

Verify the remote:

```bash
git remote -v
```

## Step 7: Push to GitHub

### For Main Branch

```bash
git branch -M main
git push -u origin main
```

If prompted for credentials:
- **Username**: Your GitHub username
- **Password**: Use a [Personal Access Token](https://github.com/settings/tokens), not your account password

### Setting Up Personal Access Token (if needed)

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: "black-litterman-repo"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. **SAVE THE TOKEN** - you won't see it again!
7. Use this token as your password when pushing

## Step 8: Verify Upload

1. Go to your GitHub repository URL:
   ```
   https://github.com/yourusername/BL-Portfolio-optimization
   ```
2. Verify all files and folders are present
3. Check that README.md displays correctly

## Step 9: Configure Repository Settings

### Add Topics (Tags)

1. On your repository page, click the gear icon next to "About"
2. Add topics/tags:
   - `portfolio-optimization`
   - `black-litterman`
   - `quantitative-finance`
   - `python`
   - `factor-models`
   - `machine-learning`
   - `finance`
3. Save changes

### Enable GitHub Pages (Optional)

To host documentation:

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` → `/docs` folder
4. Click Save
5. Your documentation will be available at:
   ```
   https://yourusername.github.io/BL-Portfolio-optimization/
   ```

### Add Repository Description

1. Click the gear icon next to "About"
2. Add description: "Black-Litterman portfolio optimization with factor models"
3. Add website URL (if you have one)
4. Check "Releases" and "Packages"
5. Save changes

## Step 10: Create Release (Optional)

Create your first release:

1. Go to "Releases" → "Create a new release"
2. Tag: `v1.0.0`
3. Title: "Initial Release - v1.0.0"
4. Description: Copy from CHANGELOG.md
5. Click "Publish release"

## Step 11: Protect Main Branch (Recommended)

For collaborative projects:

1. Go to Settings → Branches
2. Add branch protection rule
3. Branch name pattern: `main`
4. Enable:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
5. Save changes

## Step 12: Update README with Your Info

Replace placeholder information in README.md:

```bash
# Edit README.md
# Replace:
# - yourusername → your actual GitHub username
# - your.email@example.com → your actual email
# - [Your LinkedIn] → your LinkedIn profile

git add README.md
git commit -m "Update README with author information"
git push
```

## Daily Workflow

### Making Changes

```bash
# 1. Make your changes to files

# 2. Stage changes
git add .

# 3. Commit with descriptive message
git commit -m "Add feature: Description of what you changed"

# 4. Push to GitHub
git push
```

### Creating a New Feature

```bash
# 1. Create new branch
git checkout -b feature/new-optimization-method

# 2. Make changes and commit
git add .
git commit -m "Implement new optimization method"

# 3. Push branch to GitHub
git push -u origin feature/new-optimization-method

# 4. Create Pull Request on GitHub
# Then merge when ready
```

### Syncing with Remote

```bash
# Pull latest changes
git pull origin main
```

## Troubleshooting

### Problem: Push Rejected

```bash
# Solution: Pull first, then push
git pull origin main
git push origin main
```

### Problem: Merge Conflicts

```bash
# 1. Open conflicted files
# 2. Resolve conflicts (remove <<<, ===, >>> markers)
# 3. Stage resolved files
git add .
git commit -m "Resolve merge conflicts"
git push
```

### Problem: Large Files

If you have files >100MB:

```bash
# Option 1: Use Git LFS
git lfs install
git lfs track "*.xlsx"
git add .gitattributes
git commit -m "Add Git LFS tracking"

# Option 2: Remove from Git
git rm --cached large_file.xlsx
# Add to .gitignore
echo "large_file.xlsx" >> .gitignore
git add .gitignore
git commit -m "Remove large file"
```

### Problem: Forgot to Add .gitignore

```bash
# Remove all files from Git (but keep locally)
git rm -r --cached .

# Re-add with .gitignore in place
git add .
git commit -m "Apply .gitignore rules"
git push
```

## Best Practices

1. **Commit Often**: Small, focused commits are better than large ones
2. **Descriptive Messages**: Explain *what* and *why*, not *how*
3. **Branch for Features**: Use feature branches for new work
4. **Pull Before Push**: Always pull before pushing to avoid conflicts
5. **Review Changes**: Use `git diff` before committing
6. **Keep Secrets Out**: Never commit API keys, passwords, or tokens

## Additional Resources

- [GitHub Docs](https://docs.github.com)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Pro Git Book](https://git-scm.com/book/en/v2) (free)
- [GitHub Learning Lab](https://lab.github.com/)

## Getting Help

If you encounter issues:

1. Check the error message carefully
2. Search GitHub Issues for similar problems
3. Ask on [Stack Overflow](https://stackoverflow.com/questions/tagged/git)
4. Consult [Git documentation](https://git-scm.com/doc)

## Next Steps

After setting up GitHub:

1. ✅ Repository is public and accessible
2. ✅ README displays correctly
3. ✅ All files are tracked by Git
4. ✅ Topics/tags are added
5. ⬜ Share repository link
6. ⬜ Add to your resume/portfolio
7. ⬜ Write blog post about the project
8. ⬜ Submit to quantitative finance communities

## Sharing Your Work

Share your repository:
- LinkedIn: Add project to your profile
- Twitter: Tweet about your work
- Reddit: r/algotrading, r/quantfinance
- QuantConnect: Share in forums
- Personal blog: Write about methodology
- Academic: Include in publications

---

**Congratulations!** 🎉 Your Black-Litterman portfolio optimization project is now live on GitHub!

**Repository URL**: `https://github.com/yourusername/BL-Portfolio-optimization`

Don't forget to ⭐ star your own repository and encourage others to star it too!

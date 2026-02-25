#!/bin/bash
cd /home/kapil/Desktop/pytest

# Remove old git directory
rm -rf .git

# Initialize fresh git repository
git init

# Set git user config
git config user.name "Kapil"
git config user.email "your-email@example.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Complete test suite with documentation"

# Add remote
git remote add origin https://github.com/Kapilraj007/Pytest_test_case.git

# Push to master
git branch -M master
git push -u origin master --force

echo "Git push complete!"

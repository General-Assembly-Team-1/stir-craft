#!/bin/bash

# Navigate to your cloned repo
# Replace the path below with your local repository path
cd /path/to/your/local/stir-craft || { echo "Repo not found"; exit 1; }

# Fetch latest changes from origin
echo "Fetching latest changes from origin..."
git fetch --all

# Get list of remote branches
remote_branches=$(git branch -r | grep 'origin/' | grep -v 'HEAD' | sed 's|origin/||')

# Loop through each remote branch
for branch in $remote_branches; do
  echo "Updating branch: $branch"

  # Check if local branch exists
  if git rev-parse --verify "$branch" >/dev/null 2>&1; then
    # Checkout and pull latest changes
    git checkout "$branch" || { echo "Failed to checkout $branch"; exit 1; }
    git pull origin "$branch" || { echo "Failed to pull $branch"; exit 1; }
  else
    # Create tracking branch
    git checkout -b "$branch" origin/"$branch" || { echo "Failed to create tracking branch $branch"; exit 1; }
  fi
done

echo "All branches updated."

# Searching for dependent pairs in the GitHub repository

This Python script provides a set of metrics for analyzing the similarity of contributors and files in the GitHub repository. It extracts the history of commits and changes to files from the GitHub API and calculates various indicators related to how often the commits of some contributors are similar or how often some files are updated at the same time.

## Features

- Fetches commit history and file changes from a GitHub repository.
- Calculates the number of shared commits between pairs of developers.
- Calculates the percentage of shared commits between pairs of developers.
- Calculates the cosine similarity between pairs of developers based on their file changes.
- Identifies pairs of files that have a high percentage of shared commits.

## Requirements

- Python 3
- `requests` library
- `collections` library

## Usage

1. Clone this repository and navigate to the directory in a terminal.
2. Run `python main.py`.
3. When prompted, enter the owner and name of the GitHub repository you want to analyze.
4. When prompted, enter your GitHub personal access token. This is required to access the GitHub API.
5. Follow the prompts to calculate various metrics.

## Metrics

- **Shared Commits**: The number of times when same files appear in commits of two developers.
- **Percentage of Shared Commits**: The percentage of changes to the same files, relative to the total number of file changes by each developer.
- **Cosine Similarity**: A measure of similarity between two developers' file changes, calculated as the cosine of the angle between their vectors of file changes.
- **File Similarity**: The percentage of commits where two files have been changed together, relative to the total number of commits where each file has been changed.

## Note

This script uses the GitHub REST API, which has a rate limit. If you encounter rate limit issues, you may need to wait for the rate limit to reset or use a different GitHub account.

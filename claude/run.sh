#!/bin/bash
# Convenience script to run the MP3 player interface

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project root (parent of claude directory)
cd "$DIR/.."

# Run the application
python3 -m claude.main "$@"

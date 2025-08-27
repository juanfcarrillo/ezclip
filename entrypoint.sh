#!/bin/bash
set -e

echo "Starting EZClip service..."

# Run initialization script
./init_env_files.sh

# Execute the command passed as arguments
exec "$@"

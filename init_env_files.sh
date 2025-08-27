#!/bin/bash
set -e

echo "🚀 Initializing environment files..."

# Function to create credentials.json from CREDENTIALS env var
create_credentials_file() {
    if [ -z "$CREDENTIALS" ]; then
        echo "Warning: CREDENTIALS environment variable not set. Skipping credentials.json creation."
        return 1
    fi
    
    # Try to decode base64, if it fails assume it's already decoded
    if echo "$CREDENTIALS" | base64 -d > /tmp/test_decode 2>/dev/null; then
        echo "$CREDENTIALS" | base64 -d > /app/credentials.json
    else
        echo "$CREDENTIALS" > /app/credentials.json
    fi
    
    # Validate JSON
    if python3 -m json.tool /app/credentials.json > /dev/null 2>&1; then
        echo "✓ Successfully created /app/credentials.json"
        return 0
    else
        echo "Error: Invalid JSON in CREDENTIALS environment variable"
        rm -f /app/credentials.json
        return 1
    fi
}

# Function to create cookies.txt from COOKIES env var
create_cookies_file() {
    if [ -z "$COOKIES" ]; then
        echo "Warning: COOKIES environment variable not set. Skipping cookies.txt creation."
        return 1
    fi
    
    # Try to decode base64, if it fails assume it's already decoded
    if echo "$COOKIES" | base64 -d > /tmp/test_decode 2>/dev/null; then
        echo "$COOKIES" | base64 -d > /app/cookies.txt
    else
        echo "$COOKIES" > /app/cookies.txt
    fi
    
    echo "✓ Successfully created /app/cookies.txt"
    return 0
}

# Clean up test file
cleanup() {
    rm -f /tmp/test_decode
}
trap cleanup EXIT

# Create files
success_count=0
total_files=2

if create_credentials_file; then
    ((success_count++))
fi

if create_cookies_file; then
    ((success_count++))
fi

# Report results
if [ $success_count -eq 0 ]; then
    echo "❌ No files were created. Please check your environment variables."
    exit 1
elif [ $success_count -lt $total_files ]; then
    echo "⚠️  Only $success_count/$total_files files were created successfully."
    echo "Some environment variables may be missing."
else
    echo "✅ All $success_count files created successfully!"
fi

echo "🎉 Environment initialization complete!"

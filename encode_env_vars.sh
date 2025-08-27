#!/bin/bash

# Helper script to encode credentials and cookies to base64 for environment variables

set -e

echo "🔧 EZClip Environment Variable Helper"
echo "This script helps you encode your credentials and cookies files to base64"
echo "for use as environment variables in deployment."
echo

# Function to encode a file to base64
encode_file() {
    local file_path="$1"
    local var_name="$2"
    
    if [ ! -f "$file_path" ]; then
        echo "❌ File not found: $file_path"
        return 1
    fi
    
    echo "📁 Encoding $file_path..."
    local encoded=$(base64 -i "$file_path")
    
    echo "✅ Encoded $file_path"
    echo "   Add this to your .env file or export it:"
    echo "   $var_name='$encoded'"
    echo
}

# Check if files exist and encode them
if [ -f "credentials.json" ]; then
    encode_file "credentials.json" "CREDENTIALS"
else
    echo "⚠️  credentials.json not found in current directory"
    echo "   You can create it with your Firebase service account key"
    echo
fi

if [ -f "cookies.txt" ]; then
    encode_file "cookies.txt" "COOKIES"
else
    echo "⚠️  cookies.txt not found in current directory"
    echo "   You can export cookies from your browser for YouTube access"
    echo
fi

echo "💡 Usage Tips:"
echo "   1. Copy the generated environment variables to your .env file"
echo "   2. Or export them directly: export CREDENTIALS='encoded_value'"
echo "   3. The init scripts will automatically decode these during container startup"
echo
echo "🚀 Ready for deployment!"

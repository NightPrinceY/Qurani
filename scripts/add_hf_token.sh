#!/bin/bash
# Add Hugging Face token to venv activation script

VENV_ACTIVATE="venv/bin/activate"
HF_TOKEN="your_huggingface_token_here"

if [ -f "$VENV_ACTIVATE" ]; then
    # Remove old token entries if they exist
    sed -i '/^export HF_TOKEN=/d' "$VENV_ACTIVATE"
    sed -i '/^export HUGGINGFACE_HUB_TOKEN=/d' "$VENV_ACTIVATE"
    
    # Add new token exports before the last line (hash -r)
    # Find the line with "hash -r" and add before it
    if grep -q "hash -r" "$VENV_ACTIVATE"; then
        # Add token exports before hash -r line
        sed -i '/hash -r/i export HF_TOKEN="'"$HF_TOKEN"'"' "$VENV_ACTIVATE"
        sed -i '/hash -r/i export HUGGINGFACE_HUB_TOKEN="'"$HF_TOKEN"'"' "$VENV_ACTIVATE"
    else
        # Append at the end
        echo "export HF_TOKEN=\"$HF_TOKEN\"" >> "$VENV_ACTIVATE"
        echo "export HUGGINGFACE_HUB_TOKEN=\"$HF_TOKEN\"" >> "$VENV_ACTIVATE"
    fi
    
    echo "✅ Hugging Face token added to venv activation script"
    echo "Token will be set automatically when you activate venv"
else
    echo "❌ venv/bin/activate not found"
    exit 1
fi


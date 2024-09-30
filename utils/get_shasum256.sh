#!/bin/bash

# Ensure 'uds zarf tools yq' is available
if ! uds zarf tools yq --version &>/dev/null; then
  echo "'uds zarf tools yq' not found. Please ensure it is installed and accessible."
  exit 1
fi

# Check if manifest path is provided
if [ -z "$1" ]; then
  echo "Usage: $0 path/to/hardening_manifest.yaml"
  exit 1
fi

MANIFEST="$1" # The manifest file path provided as an argument

# Get the number of resources
num_resources=$(uds zarf tools yq eval '.resources | length' "$MANIFEST")

# Iterate over each resource
for ((i = 0; i < num_resources; i++)); do
  filename=$(uds zarf tools yq eval ".resources[$i].filename" "$MANIFEST")
  url=$(uds zarf tools yq eval ".resources[$i].url" "$MANIFEST")

  echo "Processing resource: $filename"

  # Download the file using wget
  wget -O "$filename" "$url"

  # Compute the SHA256 checksum
  sha256=$(sha256sum "$filename" | awk '{print $1}')
  echo "Computed SHA256: $sha256"

  # Update the manifest with the computed SHA256 checksum
  uds zarf tools yq eval ".resources[$i].validation.value = \"$sha256\"" -i "$MANIFEST"
  echo "Updated manifest with SHA256 for $filename"

  echo "Removing file: $filename"
  rm -rf $filename

  echo "----------------------------------------"
done

echo "All resources have been processed."

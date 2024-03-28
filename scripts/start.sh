#!/bin/bash -xe

echo "Start-up Script..."

get_metadata() {
  curl -s http://metadata.google.internal/computeMetadata/v1/instance/attributes/$1 -H "Metadata-Flavor: Google"
}

BAR=$(get_metadata FOO)

#!/bin/bash
# Update SearXNG settings to enable custom plugins

echo "📦 Updating SearXNG plugin configuration..."

# Create a temporary file with updated settings
cat > /tmp/plugin_update.txt << 'EOF'
# Enabled plugins
enabled_plugins:
  - 'oa_doi_rewrite'
  - 'ahmia_filter'
  - 'custom.discovery_feed'
  - 'custom.morning_coffee'
  - 'custom.search_moods'
  - 'custom.friend_activity'
  - 'custom.collection_builder'
  - 'custom.gift_drops'
EOF

# Use docker to update the file with proper permissions
docker exec -i searxng-convivial sh -c 'cat > /tmp/plugin_update.txt' < /tmp/plugin_update.txt

# Update the settings file
docker exec searxng-convivial sh -c "
sed -i '/# Enabled plugins/,/ahmia_filter/c\\
# Enabled plugins\\
enabled_plugins:\\
  - '\''oa_doi_rewrite'\''\\
  - '\''ahmia_filter'\''\\
  - '\''custom.discovery_feed'\''\\
  - '\''custom.morning_coffee'\''\\
  - '\''custom.search_moods'\''\\
  - '\''custom.friend_activity'\''\\
  - '\''custom.collection_builder'\''\\
  - '\''custom.gift_drops'\''' /etc/searxng/settings.yml
"

echo "✅ Plugin configuration updated"
echo ""
echo "🔄 Restarting SearXNG to apply changes..."
docker restart searxng-convivial

echo "✅ Done! Custom plugins are now enabled."
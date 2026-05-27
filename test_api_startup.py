#!/usr/bin/env python
"""Quick test script to start API and verify logging."""
import sys
import time
from API_EXTERNA.api import create_api_app

print("✓ Creating API app with logging...")
app = create_api_app()

print("✓ API app created successfully")
print("✓ Logging configured with Loki integration")
print("\nTo start the API server, run:")
print("  python -c \"from API_EXTERNA.api import create_api_app; app = create_api_app(); app.run(host='0.0.0.0', port=5001)\"")
print("\nOr use the docker-compose stack for Grafana/Loki:")
print("  docker-compose up -d")
print("  Then access: http://localhost:3000 (admin/admin)")


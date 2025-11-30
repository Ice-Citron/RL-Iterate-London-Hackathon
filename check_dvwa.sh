#!/bin/bash
# Script to check and initialize DVWA

echo "=== Checking DVWA Containers ==="
docker ps --filter name=dvwa

echo ""
echo "=== Checking DVWA Logs ==="
docker logs dvwa --tail 50

echo ""
echo "=== Checking MySQL Logs ==="
docker logs dvwa-mysql --tail 30

echo ""
echo "=== Testing DVWA Access ==="
curl -I http://localhost/ 2>&1 | head -10

echo ""
echo "=== Checking if DVWA files exist in container ==="
docker exec dvwa ls -la /var/www/html/ 2>&1 | head -20

echo ""
echo "=== Attempting to initialize DVWA database ==="
echo "Visit: http://localhost/setup.php"
echo "If that fails, try: http://localhost/"

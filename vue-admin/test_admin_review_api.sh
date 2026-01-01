#!/bin/bash

# 管理员登录获取token
LOGIN_RESPONSE=$(curl -s -X POST 'http://localhost:8001/api/admin/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}')

echo "登录响应:"
echo $LOGIN_RESPONSE | python3 -m json.tool

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo -e "\nToken: ${TOKEN:0:50}..."

# 测试获取评价列表
echo -e "\n=== 测试评价列表API ==="
curl -s -X GET 'http://localhost:8001/api/admin/reviews?page=1&page_size=10' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' | python3 -m json.tool


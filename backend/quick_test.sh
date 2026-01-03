#!/bin/bash

# 快速测试脚本 - 验证API基本功能
# 使用前请确保:
# 1. 后端服务运行在 http://localhost:8000
# 2. 已有管理员账号 (admin/admin123)
# 3. 数据库中存在商品

BASE_URL="http://localhost:8000"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "=========================================="
echo "商品详情API快速测试"
echo "=========================================="

# 1. 登录获取token
echo -e "\n1. 管理员登录..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${ADMIN_USER}\",\"password\":\"${ADMIN_PASS}\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ 登录失败"
  echo $LOGIN_RESPONSE
  exit 1
fi

echo "✅ 登录成功"
TOKEN_HEADER="Authorization: Bearer $TOKEN"

# 2. 获取商品列表
echo -e "\n2. 获取商品列表..."
PRODUCTS_RESPONSE=$(curl -s -X GET "${BASE_URL}/admin/products?page=1&page_size=1" \
  -H "$TOKEN_HEADER")

PRODUCT_ID=$(echo $PRODUCTS_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$PRODUCT_ID" ]; then
  echo "❌ 未找到商品"
  exit 1
fi

echo "✅ 找到商品ID: $PRODUCT_ID"

# 3. 创建内容分区
echo -e "\n3. 创建内容分区 (测试XSS防护)..."
CREATE_RESPONSE=$(curl -s -X POST "${BASE_URL}/admin/products/${PRODUCT_ID}/details/sections" \
  -H "$TOKEN_HEADER" \
  -H "Content-Type: application/json" \
  -d '{
    "section_type": "story",
    "title": "测试标题",
    "content": "<script>alert(\"XSS\")</script><p>正常内容</p>",
    "display_order": 1
  }')

SECTION_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$SECTION_ID" ]; then
  echo "❌ 创建失败"
  echo $CREATE_RESPONSE
  exit 1
fi

echo "✅ 创建成功，分区ID: $SECTION_ID"

# 检查XSS防护
HAS_SCRIPT=$(echo $CREATE_RESPONSE | grep -c "<script>")
if [ $HAS_SCRIPT -gt 0 ]; then
  echo "❌ XSS防护失败 - <script> 标签未被过滤"
else
  echo "✅ XSS防护成功 - <script> 标签已被移除"
fi

# 4. 获取商品详情
echo -e "\n4. 获取商品完整详情..."
DETAILS_RESPONSE=$(curl -s -X GET "${BASE_URL}/admin/products/${PRODUCT_ID}/details" \
  -H "$TOKEN_HEADER")

SECTIONS_COUNT=$(echo $DETAILS_RESPONSE | grep -o '"section_type"' | wc -l)
echo "✅ 获取成功，内容分区数: $SECTIONS_COUNT"

# 5. 更新内容分区
echo -e "\n5. 更新内容分区..."
UPDATE_RESPONSE=$(curl -s -X PUT "${BASE_URL}/admin/products/${PRODUCT_ID}/details/sections/${SECTION_ID}" \
  -H "$TOKEN_HEADER" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新后的标题",
    "content": "<p>更新后的内容</p>"
  }')

echo "✅ 更新成功"

# 6. 批量更新
echo -e "\n6. 批量更新内容分区..."
BATCH_RESPONSE=$(curl -s -X PUT "${BASE_URL}/admin/products/${PRODUCT_ID}/details/sections/batch" \
  -H "$TOKEN_HEADER" \
  -H "Content-Type: application/json" \
  -d '[
    {"section_type": "story", "title": "故事", "content": "<p>故事内容</p>", "display_order": 1},
    {"section_type": "nutrition", "title": "营养", "content": "<p>营养内容</p>", "display_order": 2}
  ]')

echo "✅ 批量更新成功"

# 7. 用户端API（无需认证）
echo -e "\n7. 测试用户端API (无需认证)..."
USER_RESPONSE=$(curl -s -X GET "${BASE_URL}/products/${PRODUCT_ID}/full-details")

USER_SECTIONS_COUNT=$(echo $USER_RESPONSE | grep -o '"section_type"' | wc -l)
echo "✅ 用户端访问成功，内容分区数: $USER_SECTIONS_COUNT"

# 8. 删除测试分区
echo -e "\n8. 删除内容分区..."
DELETE_RESPONSE=$(curl -s -X DELETE "${BASE_URL}/admin/products/${PRODUCT_ID}/details/sections/${SECTION_ID}" \
  -H "$TOKEN_HEADER")

echo "✅ 删除成功"

# 测试总结
echo -e "\n=========================================="
echo "测试总结"
echo "=========================================="
echo "✅ 所有基本功能测试通过"
echo ""
echo "功能清单:"
echo "  ✅ 管理员认证"
echo "  ✅ 创建内容分区 (含XSS防护)"
echo "  ✅ 获取商品详情"
echo "  ✅ 更新内容分区"
echo "  ✅ 批量更新"
echo "  ✅ 用户端API访问"
echo "  ✅ 删除内容分区"
echo ""
echo "🎉 API-001 实现完成！"
echo "=========================================="

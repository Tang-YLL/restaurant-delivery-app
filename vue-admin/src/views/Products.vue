<template>
  <div class="products">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加商品
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="商品名称">
          <el-input v-model="queryForm.keyword" placeholder="请输入商品名称" clearable />
        </el-form-item>

        <el-form-item label="分类">
          <el-select v-model="queryForm.category" placeholder="请选择分类" clearable>
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="请选择状态" clearable>
            <el-option label="上架" value="active" />
            <el-option label="下架" value="inactive" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadProducts">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 商品列表 -->
      <el-table :data="productList" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="商品图片" width="100">
          <template #default="{ row }">
            <el-image
              :src="row.image"
              fit="cover"
              style="width: 60px; height: 60px"
              :preview-src-list="row.images"
            />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="150" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column prop="sales" label="销量" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleUpdateStock(row)">
              库存
            </el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryForm.page"
          v-model:page-size="queryForm.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadProducts"
          @current-change="loadProducts"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="productForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入商品名称" />
        </el-form-item>

        <el-form-item label="商品分类" prop="category">
          <el-select v-model="productForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>

        <el-form-item label="价格" prop="price">
          <el-input-number v-model="productForm.price" :min="0" :precision="2" />
        </el-form-item>

        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="productForm.stock" :min="0" :precision="0" />
        </el-form-item>

        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="productForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入商品描述"
          />
        </el-form-item>

        <el-form-item label="商品主图" prop="image">
          <div class="image-upload-container">
            <el-upload
              class="image-uploader"
              :action="uploadAction"
              :show-file-list="false"
              :on-success="handleImageSuccess"
              :on-error="handleImageError"
              :before-upload="beforeImageUpload"
              :headers="uploadHeaders"
              accept="image/*"
            >
              <img v-if="productForm.image" :src="getImageUrl(productForm.image)" class="uploaded-image" />
              <div v-else class="uploader-placeholder">
                <el-icon class="uploader-icon"><Plus /></el-icon>
                <div class="uploader-text">点击上传</div>
              </div>
            </el-upload>
            <div class="upload-tip">
              <p>支持jpg、png、gif、webp格式，文件大小不超过5MB</p>
              <el-input
                v-model="productForm.image"
                placeholder="或直接输入图片URL"
                style="margin-top: 10px"
              />
            </div>
          </div>
        </el-form-item>

        <el-form-item label="商品图片">
          <div class="multiple-images-upload">
            <div class="image-list">
              <div v-for="(img, index) in productForm.images" :key="index" class="image-item">
                <el-image :src="getImageUrl(img)" fit="cover" style="width: 100px; height: 100px" />
                <div class="image-actions">
                  <el-button type="danger" size="small" circle @click="removeImagePath(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <el-upload
                class="image-uploader-inline"
                :action="uploadAction"
                :show-file-list="false"
                :on-success="handleImagesSuccess"
                :on-error="handleImageError"
                :before-upload="beforeImageUpload"
                :headers="uploadHeaders"
                accept="image/*"
              >
                <div class="add-image-btn">
                  <el-icon><Plus /></el-icon>
                  <span>添加</span>
                </div>
              </el-upload>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="productForm.status">
            <el-radio label="active">上架</el-radio>
            <el-radio label="inactive">下架</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 库存更新对话框 -->
    <el-dialog v-model="stockDialogVisible" title="更新库存" width="400px">
      <el-form :model="stockForm" label-width="80px">
        <el-form-item label="库存数量">
          <el-input-number v-model="stockForm.stock" :min="0" :precision="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleStockSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, RefreshLeft, Delete } from '@element-plus/icons-vue'
import { getProductList, createProduct, updateProduct, deleteProduct, getCategories, updateStock } from '../api/product'
import type { Product, ProductForm, ProductQuery } from '../types'
import type { FormInstance, FormRules, UploadProps } from 'element-plus'

const loading = ref(false)
const productList = ref<Product[]>([])
const categories = ref<string[]>([])
const total = ref(0)
const dialogVisible = ref(false)
const stockDialogVisible = ref(false)
const isEdit = ref(false)
const currentProductId = ref(0)
const formRef = ref<FormInstance>()
const imagePathInput = ref('')

// 图片上传配置
const uploadAction = computed(() => {
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api'}/admin/uploads/image`
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return {
    Authorization: `Bearer ${token}`
  }
})

const queryForm = reactive<ProductQuery>({
  page: 1,
  pageSize: 10,
  keyword: '',
  category: '',
  status: undefined as any
})

const productForm = reactive<ProductForm>({
  name: '',
  description: '',
  price: 0,
  stock: 0,
  category: '',
  image: '',
  images: [],
  status: 'active'
})

const stockForm = reactive({
  stock: 0
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入库存', trigger: 'blur' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }],
  image: [{ required: true, message: '请输入主图路径', trigger: 'blur' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑商品' : '添加商品')

const loadProducts = async () => {
  loading.value = true
  try {
    const data = await getProductList(queryForm)
    productList.value = data.list
    total.value = data.total
  } catch (error) {
    console.error('Failed to load products:', error)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const data = await getCategories()
    // 从分类对象数组中提取name字段
    categories.value = data.map((cat: any) => cat.name)
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const handleReset = () => {
  queryForm.keyword = ''
  queryForm.category = ''
  queryForm.status = undefined
  queryForm.page = 1
  loadProducts()
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: Product) => {
  isEdit.value = true
  currentProductId.value = row.id
  Object.assign(productForm, {
    name: row.name,
    description: row.description,
    price: row.price,
    stock: row.stock,
    category: row.category,
    image: row.image,
    images: [...row.images],
    status: row.status
  })
  dialogVisible.value = true
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个商品吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteProduct(id)
    ElMessage.success('删除成功')
    loadProducts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleUpdateStock = (row: Product) => {
  currentProductId.value = row.id
  stockForm.stock = row.stock
  stockDialogVisible.value = true
}

const handleStockSubmit = async () => {
  try {
    await updateStock(currentProductId.value, stockForm.stock)
    ElMessage.success('库存更新成功')
    stockDialogVisible.value = false
    loadProducts()
  } catch (error) {
    ElMessage.error('库存更新失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await updateProduct(currentProductId.value, productForm)
          ElMessage.success('更新成功')
        } else {
          await createProduct(productForm)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        loadProducts()
      } catch (error: any) {
        ElMessage.error(error.message || '操作失败')
      }
    }
  })
}

const addImagePath = () => {
  if (imagePathInput.value) {
    productForm.images.push(imagePathInput.value)
    imagePathInput.value = ''
  }
}

const removeImagePath = (index: number) => {
  productForm.images.splice(index, 1)
}

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  Object.assign(productForm, {
    name: '',
    description: '',
    price: 0,
    stock: 0,
    category: '',
    image: '',
    images: [],
    status: 'active'
  })
  formRef.value?.resetFields()
}

// 图片上传处理
const beforeImageUpload: UploadProps['beforeUpload'] = (rawFile) => {
  const isImage = rawFile.type.startsWith('image/')
  const isLt5M = rawFile.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过5MB!')
    return false
  }
  return true
}

const handleImageSuccess: UploadProps['onSuccess'] = (response) => {
  console.log('上传成功响应:', response)
  if (response && response.url) {
    productForm.image = response.url
    ElMessage.success('图片上传成功')
  } else {
    ElMessage.error('图片上传失败：响应格式错误')
  }
}

const handleImageError: UploadProps['onError'] = (error) => {
  console.error('上传错误:', error)
  ElMessage.error('图片上传失败，请检查网络连接或使用手动输入')
}

const handleImagesSuccess: UploadProps['onSuccess'] = (response) => {
  console.log('批量上传成功响应:', response)
  if (response && response.url) {
    productForm.images.push(response.url)
    ElMessage.success('图片上传成功')
  } else {
    ElMessage.error('图片上传失败：响应格式错误')
  }
}

const getImageUrl = (path: string) => {
  if (!path) return ''
  if (path.startsWith('http')) {
    return path
  }
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'}${path}`
}

onMounted(() => {
  loadProducts()
  loadCategories()
})
</script>

<style scoped>
.products {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.image-paths-list {
  max-height: 100px;
  overflow-y: auto;
}

/* 图片上传样式 */
.image-upload-container {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.image-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  width: 148px;
  height: 148px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-uploader:hover {
  border-color: #409eff;
}

.uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.uploader-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.uploader-text {
  margin-top: 8px;
  font-size: 12px;
  color: #8c939d;
}

.uploaded-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-tip {
  flex: 1;
}

.add-image-btn {
  width: 100px;
  height: 100px;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.add-image-btn:hover {
  border-color: #409eff;
  color: #409eff;
}

.add-image-btn span {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.upload-tip p {
  margin: 0 0 10px 0;
  color: #909399;
  font-size: 12px;
}

/* 多图片上传样式 */
.multiple-images-upload {
  width: 100%;
}

.image-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.image-item {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
}

.image-actions {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: none;
}

.image-item:hover .image-actions {
  display: block;
}

.image-uploader-inline {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
}

.image-uploader-inline:hover {
  border-color: #409eff;
}
</style>

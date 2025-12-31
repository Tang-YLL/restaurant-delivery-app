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

        <el-form-item label="主图路径" prop="image">
          <el-input v-model="productForm.image" placeholder="请输入图片路径，如: /images/product.jpg" />
        </el-form-item>

        <el-form-item label="图片路径">
          <el-input
            v-model="imagePathInput"
            placeholder="输入图片路径后点击添加"
            style="margin-bottom: 10px"
          >
            <template #append>
              <el-button @click="addImagePath">添加</el-button>
            </template>
          </el-input>
          <div class="image-paths-list" v-if="productForm.images.length > 0">
            <el-tag
              v-for="(img, index) in productForm.images"
              :key="index"
              closable
              @close="removeImagePath(index)"
              style="margin-right: 10px; margin-bottom: 10px"
            >
              {{ img }}
            </el-tag>
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
import { Plus, Search, RefreshLeft } from '@element-plus/icons-vue'
import { getProductList, createProduct, updateProduct, deleteProduct, getCategories, updateStock } from '../api/product'
import type { Product, ProductForm, ProductQuery } from '../types'
import type { FormInstance, FormRules } from 'element-plus'

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
    categories.value = data
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
</style>

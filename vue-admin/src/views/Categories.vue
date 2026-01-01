<template>
  <div class="categories">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加分类
          </el-button>
        </div>
      </template>

      <!-- 分类列表 -->
      <el-table :data="categoryList" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分类名称" min-width="150" />
        <el-table-column prop="code" label="分类代码" width="120" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button
              type="primary"
              link
              @click="handleToggleStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form :model="categoryForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>

        <el-form-item label="分类代码" prop="code">
          <el-input
            v-model="categoryForm.code"
            placeholder="请输入分类代码（英文）"
            :disabled="isEdit"
          />
          <div class="form-tip">分类代码创建后不可修改</div>
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="categoryForm.sort_order" :min="0" :max="9999" />
          <div class="form-tip">数字越小越靠前</div>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="categoryForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          />
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="categoryForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getCategoryList, createCategory, updateCategory, deleteCategory } from '../api/category'
import type { Category, CategoryForm } from '../types'
import type { FormInstance, FormRules } from 'element-plus'

const loading = ref(false)
const categoryList = ref<Category[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentCategoryId = ref(0)
const formRef = ref<FormInstance>()

const categoryForm = reactive<CategoryForm>({
  name: '',
  code: '',
  description: '',
  sort_order: 0,
  is_active: true
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入分类代码', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '分类代码只能包含字母、数字、下划线和横线', trigger: 'blur' }
  ],
  sort_order: [{ required: true, message: '请输入排序', trigger: 'blur' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑分类' : '添加分类')

const loadCategories = async () => {
  loading.value = true
  try {
    const data = await getCategoryList()
    categoryList.value = data
  } catch (error: any) {
    ElMessage.error(error.message || '加载分类失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  loadCategories()
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: Category) => {
  isEdit.value = true
  currentCategoryId.value = row.id
  Object.assign(categoryForm, {
    name: row.name,
    code: row.code,
    description: row.description || '',
    sort_order: row.sort_order,
    is_active: row.is_active
  })
  dialogVisible.value = true
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个分类吗？删除分类可能会影响相关商品。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteCategory(id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleToggleStatus = async (row: Category) => {
  const action = row.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}这个分类吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await updateCategory(row.id, {
      ...row,
      is_active: !row.is_active
    })
    ElMessage.success(`${action}成功`)
    loadCategories()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await updateCategory(currentCategoryId.value, categoryForm)
          ElMessage.success('更新成功')
        } else {
          await createCategory(categoryForm)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        loadCategories()
      } catch (error: any) {
        ElMessage.error(error.message || '操作失败')
      }
    }
  })
}

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  Object.assign(categoryForm, {
    name: '',
    code: '',
    description: '',
    sort_order: 0,
    is_active: true
  })
  formRef.value?.resetFields()
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.categories {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>

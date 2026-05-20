<template>
  <div class="publish-wanted-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" width="20" height="20" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        返回
      </button>
      <h1 class="page-title">{{ isEdit ? '编辑求购' : '发布求购' }}</h1>
    </div>

    <div class="form-card">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="简洁描述您的需求" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="详细描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="4" 
            placeholder="详细说明您想要的物品,例如型号、配置、颜色等"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="预算范围" required>
          <div class="budget-inputs">
            <el-form-item prop="budget_min" style="flex: 1; margin-bottom: 0;">
              <el-input-number 
                v-model="form.budget_min" 
                :min="0" 
                :precision="0"
                placeholder="最低"
                style="width: 100%;"
              />
            </el-form-item>
            <span class="budget-separator">—</span>
            <el-form-item prop="budget_max" style="flex: 1; margin-bottom: 0;">
              <el-input-number 
                v-model="form.budget_max" 
                :min="form.budget_min || 0" 
                :precision="0"
                placeholder="最高"
                style="width: 100%;"
              />
            </el-form-item>
          </div>
        </el-form-item>

        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="选择分类" style="width: 100%;">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>

        <el-form-item label="期望成色">
          <el-select v-model="form.desired_condition" placeholder="可选" clearable style="width: 100%;">
            <el-option label="全新/未拆封" value="全新/未拆封" />
            <el-option label="几乎全新" value="几乎全新" />
            <el-option label="轻微使用痕迹" value="轻微使用痕迹" />
            <el-option label="正常使用" value="正常使用" />
            <el-option label="明显使用痕迹" value="明显使用痕迹" />
            <el-option label="不限" value="不限" />
          </el-select>
        </el-form-item>

        <div class="submit-section">
          <el-button size="large" @click="$router.back()">取消</el-button>
          <el-button 
            type="primary" 
            size="large" 
            @click="submitForm"
            :loading="submitting"
          >
            {{ submitting ? '发布中...' : (isEdit ? '保存修改' : '发布求购') }}
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createWanted, updateWanted, getWantedById } from '../api/wanted'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  title: '',
  description: '',
  budget_min: 0,
  budget_max: 100,
  category: '',
  desired_condition: '',
})

const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 5, message: '标题至少5个字符', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入详细描述', trigger: 'blur' },
    { min: 10, message: '描述至少10个字符', trigger: 'blur' },
  ],
  budget_min: [
    { required: true, message: '请输入最低预算', trigger: 'blur' },
  ],
  budget_max: [
    { required: true, message: '请输入最高预算', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value < form.budget_min) {
          callback(new Error('最高预算不能低于最低预算'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    },
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' },
  ],
}

const categories = [
  '数码电子', '图书教材', '生活用品', '服装配饰', 
  '运动户外', '美妆护肤', '食品零食', '其他'
]

async function loadWanted() {
  if (!isEdit.value) return
  try {
    const res = await getWantedById(route.params.id)
    const wanted = res.data.wanted
    form.title = wanted.title
    form.description = wanted.description
    form.budget_min = wanted.budget_min
    form.budget_max = wanted.budget_max
    form.category = wanted.category
    form.desired_condition = wanted.desired_condition
  } catch (error) {
    console.error('Failed to load wanted:', error)
  }
}

async function submitForm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await updateWanted(route.params.id, form)
      ElMessage.success('修改成功')
    } else {
      await createWanted(form)
      ElMessage.success('发布成功')
    }
    router.push('/wanteds')
  } catch (error) {
    console.error('Failed to submit:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadWanted()
})
</script>

<style scoped>
.publish-wanted-page {
  max-width: 600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  background: var(--c-surface);
  color: var(--c-text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--c-shadow-sm);
}

.back-btn:hover {
  background: var(--c-surface-alt);
  color: var(--c-text);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-text);
}

.form-card {
  background: var(--c-surface);
  border-radius: 20px;
  padding: 32px;
  box-shadow: var(--c-shadow-lg);
}

.budget-inputs {
  display: flex;
  align-items: center;
  gap: 12px;
}

.budget-separator {
  font-size: 18px;
  color: var(--c-text-muted);
  font-weight: 300;
}

.submit-section {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--c-border);
}
</style>

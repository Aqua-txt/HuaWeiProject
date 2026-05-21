<template>
  <div class="publish-page">
    <div class="publish-card">
      <div class="publish-header">
        <router-link to="/home" class="home-link">
          <el-button type="primary" round size="small">返回主页</el-button>
        </router-link>
        <h2>{{ isEdit ? '编辑商品' : '发布商品' }}</h2>
        <p class="publish-sub">{{ isEdit ? '修改商品信息' : '填写信息，让更多人看到你的闲置' }}</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large">
        <el-form-item label="商品标题" prop="title">
          <el-input v-model="form.title" placeholder="例：95新大学英语教材第四册" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="商品图片" prop="images">
          <el-upload v-model:file-list="fileList" list-type="picture-card" :auto-upload="false"
            :limit="6" :on-exceed="onExceed" :before-upload="beforeUpload"
            :on-change="onChange" accept="image/*">
            <div class="upload-placeholder">
              <svg viewBox="0 0 24 24" fill="none" width="24" height="24" stroke="currentColor" stroke-width="1.8">
                <rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              <span>上传图片</span>
            </div>
          </el-upload>
          <template #extra>
            <div class="form-tip">最多 6 张，单张 ≤ 5MB，支持 PNG/JPG/WebP</div>
          </template>
        </el-form-item>

        <el-form-item label="商品描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4"
            placeholder="说说商品的使用情况、购买时间、出手原因..." maxlength="500" show-word-limit />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="价格 (&yen;)" prop="price">
              <el-input v-model="form.price" placeholder="0.00" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="form.category" style="width:100%">
                <el-option label="📚 教材" value="教材" />
                <el-option label="💻 数码" value="数码" />
                <el-option label="🏠 生活" value="生活" />
                <el-option label="📦 其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="成色" prop="condition">
          <div class="condition-cards">
            <label v-for="c in conditions" :key="c.value"
              class="condition-card" :class="{ active: form.condition === c.value }">
              <input type="radio" :value="c.value" v-model="form.condition" style="display:none" />
              <span class="cond-emoji">{{ c.emoji }}</span>
              <span class="cond-label">{{ c.label }}</span>
            </label>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit"
            style="width:100%;height:48px;font-size:16px;border-radius:14px">
            {{ isEdit ? '保存修改' : '✨ 立即发布' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createProduct, updateProduct, getProduct } from '../api/products'
import { useUserStore } from '../store'
import { getUploadUrl } from '../utils/url'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const submitting = ref(false)
const fileList = ref([])

const isEdit = computed(() => !!route.params.id)

const conditions = [
  { value: '全新', label: '全新', emoji: '✨' },
  { value: '几乎全新', label: '几乎全新', emoji: '👍' },
  { value: '轻微使用痕迹', label: '轻微痕迹', emoji: '📝' },
  { value: '明显使用痕迹', label: '明显痕迹', emoji: '📦' },
]

const form = reactive({
  title: '',
  description: '',
  price: '',
  category: '教材',
  condition: '轻微使用痕迹',
})

const rules = {
  title: [
    { required: true, message: '请输入商品标题', trigger: 'blur' },
    { max: 100, message: '标题不能超过100个字符', trigger: 'blur' },
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    {
      validator: (rule, value, cb) => {
        const v = parseFloat(value)
        if (isNaN(v) || v < 0.01 || v > 99999.99) {
          cb(new Error('价格需在 0.01 - 99999.99 之间'))
        } else { cb() }
      },
      trigger: 'blur',
    },
  ],
}

function onExceed() { ElMessage.warning('最多上传6张图片') }

function beforeUpload(file) {
  if (file.size > 5 * 1024 * 1024) { ElMessage.error('图片大小不能超过5MB'); return false }
  const valid = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']
  if (!valid.includes(file.type)) { ElMessage.error('仅支持 png/jpg/jpeg/gif/webp'); return false }
  return false
}

function onChange(file, files) { fileList.value = files }

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  if (!isEdit.value && fileList.value.length === 0) {
    ElMessage.error('请至少上传一张图片'); return
  }
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('title', form.title)
    fd.append('description', form.description)
    fd.append('price', form.price)
    fd.append('category', form.category)
    fd.append('condition', form.condition)
    fileList.value.forEach(f => { fd.append('images', f.raw) })
    if (isEdit.value) await updateProduct(route.params.id, fd)
    else await createProduct(fd)
    router.push(isEdit.value ? `/product/${route.params.id}` : '/home')
  } catch {} finally { submitting.value = false }
}

async function loadProduct() {
  if (!isEdit.value) return
  try {
    const res = await getProduct(route.params.id)
    const p = res.data
    if (p.seller_id !== userStore.user?.id) {
      ElMessage.error('只能编辑自己的商品'); router.replace('/home'); return
    }
    form.title = p.title
    form.description = p.description
    form.price = String(p.price)
    form.category = p.category
    form.condition = p.condition
    if (p.images) {
      fileList.value = p.images.map((img, i) => ({
        name: `image_${i}`,
        url: getUploadUrl(img),
        raw: null,
      }))
    }
  } catch {}
}

onMounted(() => { loadProduct() })
</script>

<style scoped>
.publish-page {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  box-sizing: border-box;
  animation: fadeInUp 0.4s ease;
}

.publish-card {
  background: white;
  width: min(100%, 680px);
  padding: 36px;
  border-radius: 20px;
  box-shadow: 0 2px 20px rgba(26,35,50,0.04);
  border: 1px solid rgba(0,0,0,0.03);
}

.publish-header {
  position: relative;
  margin-bottom: 32px;
  padding-right: 108px;
}

.home-link {
  position: absolute;
  top: 0;
  right: 0;
  text-decoration: none;
}

.publish-header h2 {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.publish-sub {
  font-size: 14px;
  color: var(--c-text-muted);
}

.form-tip {
  font-size: 12px;
  color: var(--c-text-muted);
  margin-top: 6px;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--c-text-muted);
  font-size: 12px;
}

/* Condition cards */
.condition-cards {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.condition-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 20px;
  border-radius: 14px;
  border: 2px solid var(--c-border);
  background: white;
  cursor: pointer;
  transition: all 0.25s;
  min-width: 90px;
}

.condition-card:hover {
  border-color: rgba(91,141,239,0.3);
  background: var(--c-primary-light);
}

.condition-card.active {
  border-color: var(--c-primary);
  background: var(--c-primary-light);
  box-shadow: 0 0 0 3px rgba(91,141,239,0.12);
}

.cond-emoji { font-size: 22px; }
.cond-label { font-size: 12px; font-weight: 600; color: var(--c-text-secondary); }
.condition-card.active .cond-label { color: var(--c-primary); }
</style>

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/Home.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'messages',
        name: 'Messages',
        component: () => import('../views/Messages.vue'),
        meta: { title: '消息', requiresAuth: true },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { title: '我的', requiresAuth: true },
      },
    ],
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册' },
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('../views/ProductDetail.vue'),
    meta: { title: '商品详情' },
  },
  {
    path: '/publish',
    name: 'Publish',
    component: () => import('../views/Publish.vue'),
    meta: { title: '发布商品', requiresAuth: true },
  },
  {
    path: '/edit-product/:id',
    name: 'EditProduct',
    component: () => import('../views/Publish.vue'),
    meta: { title: '编辑商品', requiresAuth: true },
  },
  {
    path: '/chat/:id',
    name: 'ChatDetail',
    component: () => import('../views/ChatDetail.vue'),
    meta: { title: '聊天', requiresAuth: true },
  },
  {
    path: '/my-products',
    name: 'MyProducts',
    component: () => import('../views/MyProducts.vue'),
    meta: { title: '我的发布', requiresAuth: true },
  },
  {
    path: '/my-favorites',
    name: 'MyFavorites',
    component: () => import('../views/MyFavorites.vue'),
    meta: { title: '我的收藏', requiresAuth: true },
  },
  {
    path: '/edit-profile',
    name: 'EditProfile',
    component: () => import('../views/EditProfile.vue'),
    meta: { title: '编辑资料', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 校园二手交易` : '校园二手交易平台'
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      return next('/login')
    }
  }
  next()
})

export default router

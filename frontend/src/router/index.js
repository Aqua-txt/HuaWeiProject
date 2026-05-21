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
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/Orders.vue'),
        meta: { title: '我的订单', requiresAuth: true },
      },
      {
        path: 'orders/:id',
        name: 'OrderDetail',
        component: () => import('../views/OrderDetail.vue'),
        meta: { title: '订单详情', requiresAuth: true },
      },
      {
        path: 'orders/:id/review',
        name: 'Review',
        component: () => import('../views/Review.vue'),
        meta: { title: '评价订单', requiresAuth: true },
      },
      {
        path: 'wanteds',
        name: 'Wanteds',
        component: () => import('../views/Wanteds.vue'),
        meta: { title: '求购专区' },
      },
      {
        path: 'wanted/publish',
        name: 'PublishWanted',
        component: () => import('../views/PublishWanted.vue'),
        meta: { title: '发布求购', requiresAuth: true },
      },
      {
        path: 'wanted/:id',
        name: 'WantedDetail',
        component: () => import('../views/WantedDetail.vue'),
        meta: { title: '求购详情' },
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
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/AdminLogin.vue'),
    meta: { title: '管理员登录' },
  },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    meta: { requiresAdmin: true },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../views/admin/AdminDashboard.vue'),
        meta: { title: '数据看板' },
      },
      {
        path: 'reports',
        name: 'AdminReports',
        component: () => import('../views/admin/AdminReports.vue'),
        meta: { title: '举报管理' },
      },
      {
        path: 'products',
        name: 'AdminProducts',
        component: () => import('../views/admin/AdminProducts.vue'),
        meta: { title: '商品管理' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/admin/AdminUsers.vue'),
        meta: { title: '用户管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 校园二手交易` : '校园二手交易平台'
  
  if (to.meta.requiresAdmin) {
    const adminToken = localStorage.getItem('admin_token')
    if (!adminToken && to.path !== '/admin/login') {
      return next('/admin/login')
    }
    return next()
  }
  
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      return next('/login')
    }
  }
  next()
})

export default router

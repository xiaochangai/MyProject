<template>
  <div class="app-container">
    <el-container>
      <el-header height="60px">
        <div class="header-content">
          <h1 class="system-title">个人记账系统</h1>
          <div class="nav-links" v-if="isLoggedIn">
            <router-link to="/">账目列表</router-link>
            <router-link to="/statistics">统计分析</router-link>
            <a href="#" @click.prevent="handleLogout" class="logout-link">退出登录</a>
          </div>
          <el-button v-if="isLoggedIn" class="menu-button" icon="el-icon-menu" @click="showMobileMenu = true" />
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
      <el-footer height="40px">
        <div class="footer-content">
          © {{ new Date().getFullYear() }} 个人记账系统
        </div>
      </el-footer>
    </el-container>

    <!-- 移动端菜单 -->
    <el-drawer v-model="showMobileMenu" title="菜单" direction="rtl" size="70%">
      <div class="mobile-menu">
        <router-link to="/" @click="showMobileMenu = false">账目列表</router-link>
        <router-link to="/statistics" @click="showMobileMenu = false">统计分析</router-link>
        <a href="#" @click.prevent="handleLogout">退出登录</a>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, provide } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const isLoggedIn = ref(false);
const showMobileMenu = ref(false);

// 提供全局状态
provide('isLoggedIn', isLoggedIn);

// 提供更新登录状态的方法
provide('updateLoginStatus', (status) => {
  isLoggedIn.value = status;
});

onMounted(() => {
  // 检查是否有token，判断登录状态
  const token = localStorage.getItem('token');
  isLoggedIn.value = !!token;
});

const handleLogout = () => {
  // 清除本地存储的token和用户信息
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  
  // 清除axios请求头中的token
  delete axios.defaults.headers.common['Authorization'];
  
  // 更新登录状态
  isLoggedIn.value = false;
  showMobileMenu.value = false;
  
  // 重定向到登录页
  router.push('/login');
};
</script>

<style>
.app-container {
  height: 100vh;
  width: 100%;
}

.el-header {
  background-color: #409EFF;
  color: white;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.system-title {
  margin: 0;
  font-size: 1.5rem;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-size: 16px;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
  overflow-x: hidden;
}

.el-footer {
  background-color: #f5f7fa;
  color: #606266;
  display: flex;
  justify-content: center;
  align-items: center;
  border-top: 1px solid #e4e7ed;
}

.menu-button {
  display: none;
  background: none;
  border: none;
  color: white;
  padding: 0;
}

.mobile-menu {
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.mobile-menu a {
  color: #303133;
  text-decoration: none;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
  font-size: 16px;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .system-title {
    font-size: 1.2rem;
  }

  .nav-links {
    display: none;
  }

  .menu-button {
    display: block;
  }

  .el-main {
    padding: 15px;
  }
}
</style>
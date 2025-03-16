<template>
  <div class="app-container">
    <el-container>
      <el-header height="60px">
        <div class="header-content">
          <h1>个人记账系统</h1>
          <div class="nav-links" v-if="isLoggedIn">
            <router-link to="/">账目列表</router-link>
            <router-link to="/statistics">统计分析</router-link>
            <a href="#" @click.prevent="handleLogout" class="logout-link">退出登录</a>
          </div>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const isLoggedIn = ref(false);

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
}

.el-footer {
  background-color: #f5f7fa;
  color: #606266;
  display: flex;
  justify-content: center;
  align-items: center;
  border-top: 1px solid #e4e7ed;
}
</style>
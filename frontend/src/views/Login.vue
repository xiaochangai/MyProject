<template>
  <div class="login-container">
    <div class="login-card">
      <h2>个人记账系统</h2>
      <div class="login-form">
        <el-form :model="form" :rules="rules" ref="loginForm" label-width="0px">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" prefix-icon="el-icon-user"></el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="el-icon-lock" show-password></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="handleLogin" class="login-button">登录</el-button>
          </el-form-item>
        </el-form>
        <div class="login-error" v-if="errorMessage">
          {{ errorMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Login',
  inject: ['updateLoginStatus'],
  data() {
    return {
      form: {
        username: 'wuz11',  // 默认填入指定的用户名
        password: ''  // 密码不预填
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      loading: false,
      errorMessage: ''
    };
  },
  methods: {
    async handleLogin() {
      try {
        this.errorMessage = '';
        const valid = await this.$refs.loginForm.validate();
        
        if (!valid) return;
        
        this.loading = true;
        
        // 调用登录API
        const response = await axios.post('/api/auth/login', {
          username: this.form.username,
          password: this.form.password
        });
        
        // 保存token到localStorage
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // 设置axios默认请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
        
        // 更新登录状态
        this.updateLoginStatus(true);
        
        // 跳转到首页
        this.$router.push('/');
      } catch (error) {
        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.error || '登录失败，请重试';
        } else {
          this.errorMessage = '网络错误，请稍后重试';
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-card h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #409EFF;
  font-size: 1.8rem;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  width: 100%;
  margin-top: 10px;
  height: 40px;
  font-size: 16px;
}

.login-error {
  color: #F56C6C;
  font-size: 14px;
  text-align: center;
  margin-top: 15px;
}

/* 响应式设计 */
@media screen and (max-width: 480px) {
  .login-container {
    padding: 15px;
  }

  .login-card {
    padding: 20px;
  }

  .login-card h2 {
    font-size: 1.5rem;
    margin-bottom: 20px;
  }

  .el-input {
    font-size: 14px;
  }

  .login-button {
    height: 36px;
    font-size: 14px;
  }
}
</style>
<template>
  <div class="transactions">
    <div class="card">
      <div class="filter-section">
        <h2>账目列表</h2>
        <el-button type="primary" @click="showAddDialog">添加记录</el-button>
        <el-button type="info" @click="fetchTransactions">刷新</el-button>
        <el-button type="success" @click="exportTransactions">导出</el-button>
      </div>
      
      <!-- 移动端卡片列表 -->
      <div class="mobile-list" v-if="isMobile">
        <el-card v-for="row in transactions" :key="row.id" class="transaction-card">
          <div class="card-header">
            <span class="date">{{ row.date }}</span>
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'">
              {{ row.type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </div>
          <div class="card-content">
            <div class="amount-row">
              <span class="label">金额：</span>
              <span :class="row.type === 'income' ? 'income-amount' : 'expense-amount'">
                {{ row.type === 'income' ? '+' : '-' }} {{ row.amount }}
              </span>
            </div>
            <div class="category-row">
              <span class="label">分类：</span>
              <span>{{ row.category }}</span>
            </div>
            <div class="description-row" v-if="row.description">
              <span class="label">描述：</span>
              <span>{{ row.description }}</span>
            </div>
          </div>
          <div class="card-actions">
            <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="confirmDelete(row)">删除</el-button>
          </div>
        </el-card>
      </div>
      <div class="pagination-container" v-if="isMobile">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="10"
          :total="total"
          @current-change="fetchTransactions"
          layout="prev, pager, next"
          small
        />
      </div>

      <!-- 桌面端表格 -->
      <el-table v-else :data="transactions" style="width: 100%" v-loading="loading">
        <el-table-column prop="date" label="日期" width="120">
          <template #default="{row}">
            {{ row.date }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{row}">
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'">
              {{ row.type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120"></el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{row}">
            <span :class="row.type === 'income' ? 'income-amount' : 'expense-amount'">
              {{ row.type === 'income' ? '+' : '-' }} {{ row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述"></el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container" v-if="!isMobile">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="10"
          :total="total"
          @current-change="fetchTransactions"
          layout="prev, pager, next"
        />
      </div>
    </div>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      :title="isEdit ? '编辑记录' : '添加记录'"
      v-model="dialogVisible"
      :width="isMobile ? '90%' : '500px'"
    >
      <el-form :model="form" :label-width="isMobile ? '60px' : '80px'" :rules="rules" ref="formRef">
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio label="income">收入</el-radio>
            <el-radio label="expense">支出</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="金额" prop="amount">
          <el-input-number v-model="form.amount" :min="0" :precision="2" :step="10" style="width: 100%"></el-input-number>
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="选择分类" style="width: 100%">
            <el-option-group label="收入分类" v-if="form.type === 'income'">
              <el-option v-for="item in incomeCategories" :key="item" :label="item" :value="item"></el-option>
            </el-option-group>
            <el-option-group label="支出分类" v-else>
              <el-option v-for="item in expenseCategories" :key="item" :label="item" :value="item"></el-option>
            </el-option-group>
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期" prop="date">
          <el-date-picker v-model="form.date" type="date" placeholder="选择日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%"></el-date-picker>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述信息"></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import axios from 'axios';
import { ElMessage, ElMessageBox } from 'element-plus';

// 响应式判断
const isMobile = computed(() => window.innerWidth <= 768);

// 数据
const transactions = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const isEdit = ref(false);
const formRef = ref(null);
const currentPage = ref(1);
const total = ref(0);
const totalPages = ref(0);

// 表单数据
const form = reactive({
  id: null,
  type: 'expense',
  amount: 0,
  category: '',
  date: new Date().toISOString().split('T')[0],
  description: ''
});

// 表单验证规则
const rules = {
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }]
};

// 分类选项
const incomeCategories = [
  '工资',
  '奖金',
  '投资收益',
  '兼职收入',
  '其他收入'
];

const expenseCategories = [
  '餐饮',
  '购物',
  '交通',
  '住房',
  '娱乐',
  '医疗',
  '教育',
  '旅行',
  '其他支出'
];

// 获取所有交易记录
const exportTransactions = async () => {
  try {
    const response = await axios.get('/api/transactions/export', {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `transactions_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    ElMessage.error('导出失败');
  }
};

const fetchTransactions = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`/api/transactions?page=${currentPage.value}`);
    transactions.value = response.data.items;
    total.value = response.data.total;
    totalPages.value = response.data.pages;
  } catch (error) {
    console.error('获取交易记录失败:', error);
    ElMessage.error('获取交易记录失败');
  } finally {
    loading.value = false;
  }
};

// 显示添加对话框
const showAddDialog = () => {
  isEdit.value = false;
  resetForm();
  dialogVisible.value = true;
};

// 显示编辑对话框
const showEditDialog = (row) => {
  isEdit.value = true;
  Object.assign(form, row);
  dialogVisible.value = true;
};

// 重置表单
const resetForm = () => {
  form.id = null;
  form.type = 'expense';
  form.amount = 0;
  form.category = '';
  form.date = new Date().toISOString().split('T')[0];
  form.description = '';
};

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          // 编辑现有记录
          await axios.put(`/api/transactions/${form.id}`, form);
          ElMessage.success('更新成功');
        } else {
          // 添加新记录
          await axios.post('/api/transactions', form);
          ElMessage.success('添加成功');
        }
        dialogVisible.value = false;
        fetchTransactions();
      } catch (error) {
        console.error('操作失败:', error);
        ElMessage.error('操作失败');
      }
    }
  });
};

// 确认删除
const confirmDelete = (row) => {
  ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/api/transactions/${row.id}`);
      ElMessage.success('删除成功');
      fetchTransactions();
    } catch (error) {
      console.error('删除失败:', error);
      ElMessage.error('删除失败');
    }
  }).catch(() => {});
};

// 初始化
onMounted(() => {
  fetchTransactions();
});
</script>

<style scoped>
.transactions {
  padding: 20px;
}

.card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-section h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #303133;
}

.income-amount {
  color: #67C23A;
  font-weight: bold;
}

.expense-amount {
  color: #F56C6C;
  font-weight: bold;
}

/* 移动端样式 */
.mobile-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.transaction-card {
  margin-bottom: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.card-content {
  margin: 15px 0;
}

.card-content > div {
  margin-bottom: 8px;
}

.card-content .label {
  color: #909399;
  margin-right: 8px;
}

.card-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .transactions {
    padding: 10px;
  }

  .card {
    padding: 15px;
  }

  .filter-section h2 {
    font-size: 1.2rem;
  }

  .el-dialog__wrapper .el-dialog {
    width: 90%;
  }

  .el-form-item {
    margin-bottom: 15px;
  }
}
</style>
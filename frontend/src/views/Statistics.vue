<template>
  <div class="statistics">
    <div class="card mb-20">
      <div class="filter-section">
        <h2>支出分类统计</h2>
        <div class="filters">
          <el-select v-model="selectedMonth" placeholder="选择月份">
            <el-option 
              v-for="month in 12" 
              :key="month" 
              :label="month + '月'" 
              :value="month">
            </el-option>
          </el-select>
        </div>
      </div>
      <div class="chart-container" ref="categoryChartRef"></div>
    </div>
    
    <div class="card">
      <div class="filter-section">
        <h2>收支统计</h2>
        <div class="filters">
          <el-select v-model="selectedYear" placeholder="选择年份">
            <el-option 
              v-for="year in availableYears" 
              :key="year" 
              :label="year + '年'" 
              :value="year">
            </el-option>
          </el-select>
        </div>
      </div>
      <div class="chart-container" ref="monthlyChartRef"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import * as echarts from 'echarts';

// 数据和引用
const monthlyChartRef = ref(null);
const categoryChartRef = ref(null);
const monthlyChart = ref(null);
const categoryChart = ref(null);

const availableYears = ref([]);
const selectedYear = ref(new Date().getFullYear());
const selectedMonth = ref(new Date().getMonth() + 1);

const monthlyData = ref([]);
const categoryData = ref([]);

// 获取可用年份
const fetchYears = async () => {
  try {
    const response = await axios.get('/api/statistics/yearly');
    let years = response.data.map(item => item.year);
    
    // 确保包含最近5年的年份选项
    const currentYear = new Date().getFullYear();
    for (let i = 0; i < 5; i++) {
      const year = currentYear - i;
      if (!years.includes(year)) {
        years.push(year);
      }
    }
    
    // 按降序排列年份
    availableYears.value = years.sort((a, b) => b - a);
    
    // 如果没有选择年份或选择的年份不在可用年份中，默认选择最新的年份
    if (!selectedYear.value || !availableYears.value.includes(selectedYear.value)) {
      selectedYear.value = availableYears.value[0];
    }
  } catch (error) {
    console.error('获取年份数据失败:', error);
    // 发生错误时，生成最近5年的年份选项
    const currentYear = new Date().getFullYear();
    availableYears.value = Array.from({length: 5}, (_, i) => currentYear - i).sort((a, b) => b - a);
    selectedYear.value = currentYear;
  }
};

// 获取月度数据
const fetchMonthlyData = async () => {
  try {
    const response = await axios.get(`/api/statistics/monthly?year=${selectedYear.value}`);
    monthlyData.value = response.data;
    renderMonthlyChart();
  } catch (error) {
    console.error('获取月度数据失败:', error);
  }
};

// 获取分类数据
const fetchCategoryData = async () => {
  try {
    const response = await axios.get(`/api/statistics/categories?year=${selectedYear.value}&month=${selectedMonth.value}`);
    categoryData.value = response.data;
    renderCategoryChart();
  } catch (error) {
    console.error('获取分类数据失败:', error);
  }
};

// 渲染月度图表
const renderMonthlyChart = () => {
  if (!monthlyChartRef.value) return;
  
  if (!monthlyChart.value) {
    monthlyChart.value = echarts.init(monthlyChartRef.value);
  }
  
  const months = monthlyData.value.map(item => `${item.month}月`);
  const incomes = monthlyData.value.map(item => item.income);
  const expenses = monthlyData.value.map(item => item.expense);
  const balances = monthlyData.value.map(item => item.balance);
  
  const option = {
    title: {
      text: `${selectedYear.value}年收支统计`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>';
        params.forEach(param => {
          const value = param.value.toLocaleString('zh-CN', {
            style: 'currency',
            currency: 'CNY'
          });
          result += param.marker + param.seriesName + ': ' + value + '<br/>';
        });
        return result;
      }
    },
    legend: {
      data: ['收入', '支出', '结余'],
      bottom: 10
    },
    xAxis: {
      type: 'category',
      data: months
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '收入',
        type: 'bar',
        data: incomes,
        itemStyle: { color: '#67C23A' },
        label: {
          show: false,
          position: 'top',
          formatter: function(params) {
            return params.value.toLocaleString('zh-CN', {
              style: 'currency',
              currency: 'CNY'
            });
          }
        },
        emphasis: {
          label: {
            show: true
          }
        }
      },
      {
        name: '支出',
        type: 'bar',
        data: expenses,
        itemStyle: { color: '#F56C6C' },
        label: {
          show: false,
          position: 'top',
          formatter: function(params) {
            return params.value.toLocaleString('zh-CN', {
              style: 'currency',
              currency: 'CNY'
            });
          }
        },
        emphasis: {
          label: {
            show: true
          }
        }
      },
      {
        name: '结余',
        type: 'line',
        data: balances,
        itemStyle: { color: '#409EFF' },
        label: {
          show: false,
          position: 'top',
          formatter: function(params) {
            return params.value.toLocaleString('zh-CN', {
              style: 'currency',
              currency: 'CNY'
            });
          }
        },
        emphasis: {
          label: {
            show: true
          }
        }
      }
    ]
  };
  
  monthlyChart.value.setOption(option);
};

// 渲染分类图表
const renderCategoryChart = () => {
  if (!categoryChartRef.value) return;
  
  if (!categoryChart.value) {
    categoryChart.value = echarts.init(categoryChartRef.value);
  }
  
  const option = {
    title: {
      text: `${selectedYear.value}年${selectedMonth.value}月支出分类`,
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        center: ['60%', '50%'],
        data: categoryData.value.map(item => ({
          name: item.category,
          value: item.amount
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };
  
  categoryChart.value.setOption(option);
};

// 监听窗口大小变化，调整图表大小
const handleResize = () => {
  monthlyChart.value?.resize();
  categoryChart.value?.resize();
};

// 监听年份变化
watch(selectedYear, (newYear) => {
  fetchMonthlyData();
  fetchCategoryData();
});

// 监听月份变化
watch(selectedMonth, (newMonth) => {
  fetchCategoryData();
});

onMounted(() => {
  fetchYears();
  fetchMonthlyData();
  fetchCategoryData();
  
  window.addEventListener('resize', handleResize);
});
</script>

<style scoped>
.statistics {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.mb-20 {
  margin-bottom: 20px;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-container {
  height: 400px;
  width: 100%;
}
</style>
<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>Страница не найдена</h2>
      <p>Извините, но страница, которую вы ищете, не существует.</p>
      <button @click="goHome" class="home-btn">Вернуться на главную</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.not-found-content {
  text-align: center;
  background: white;
  padding: 3rem 2rem;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
}

.not-found-content h1 {
  font-size: 6rem;
  color: #667eea;
  margin: 0;
  line-height: 1;
}

.not-found-content h2 {
  color: #333;
  margin: 1rem 0 0.5rem 0;
  font-size: 1.5rem;
}

.not-found-content p {
  color: #666;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.home-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.home-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}
</style>
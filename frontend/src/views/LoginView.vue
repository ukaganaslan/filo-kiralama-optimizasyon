<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-brand">Araç Kiralama</div>
      <h2>Giriş Yap</h2>
    

      <div class="field">
        <label>KULLANICI ADI</label>
        <input v-model="username" type="text" placeholder="Kullanıcı adınız" />
      </div>

      <div class="field">
        <label>ŞİFRE</label>
        <input v-model="password" type="password" placeholder="Şifreniz" @keyup.enter="handleLogin" />
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <button @click="handleLogin">Giriş Yap →</button>

      <p class="switch">Hesabın yok mu? <a @click="router.push('/register')">Kayıt Ol</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()
const auth = useAuthStore()

async function handleLogin() {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/login/', {
      username: username.value,
      password: password.value,
    })
    auth.login(response.data.token, response.data.username, response.data.is_staff)
    if (response.data.is_staff) {
      router.push('/operator')
    } else {
      router.push('/dashboard')
    }
  } catch {
    error.value = 'Kullanıcı adı veya şifre hatalı'
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: sans-serif;
}
.auth-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  padding: 40px;
  width: 380px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.auth-brand {
  font-size: 16px;
  font-weight: 700;
  color: #6366f1;
  margin-bottom: 4px;
}
h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}
.subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
label {
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
  letter-spacing: 0.08em;
}
input {
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border 0.2s;
}
input:focus {
  border-color: #6366f1;
}
button {
  padding: 12px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 4px;
}
button:hover { background: #4f46e5; }
.error { color: #dc2626; font-size: 13px; margin: 0; }
.switch {
  text-align: center;
  font-size: 13px;
  color: #64748b;
}
.switch a { color: #6366f1; cursor: pointer; font-weight: 600; }
</style>

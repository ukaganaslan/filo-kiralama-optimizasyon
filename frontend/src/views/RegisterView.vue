<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-brand">Araç Kiralama</div>
      <h2>Kayıt Ol</h2>


      <div class="field">
        <label>AD SOYAD</label>
        <input v-model="fullName" type="text" placeholder="Ad Soyad" />
      </div>

      <div class="row">
        <div class="field">
          <label>TELEFON</label>
          <input v-model="phone" type="text" placeholder="05xx xxx xx xx" />
        </div>
        <div class="field">
          <label>E-POSTA</label>
          <input v-model="email" type="email" placeholder="ornek@mail.com" />
        </div>
      </div>

      <div class="field">
        <label>KULLANICI ADI</label>
        <input v-model="username" type="text" placeholder="Kullanıcı adı" />
      </div>

      <div class="field">
        <label>ŞİFRE</label>
        <input v-model="password" type="password" placeholder="Şifre" />
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <button @click="handleRegister">Kayıt Ol →</button>

      <p class="switch">Hesabın var mı? <a @click="router.push('/')">Giriş Yap</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const fullName = ref('')
const phone = ref('')
const email = ref('')
const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()
const auth = useAuthStore()

async function handleRegister() {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/register/', {
      full_name: fullName.value,
      phone: phone.value,
      email: email.value,
      username: username.value,
      password: password.value,
    })
    auth.login(response.data.token, response.data.username, response.data.is_staff)
    router.push('/dashboard')
  } catch {
    error.value = 'Kayıt sırasında hata oluştu'
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
  width: 420px;
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
.row {
  display: flex;
  gap: 12px;
}
.row .field { flex: 1; }
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
input:focus { border-color: #6366f1; }
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

<template>
  <div class="auth-layout">
    <div class="auth-left">
      <div class="auth-brand">
        <div class="brand-icon">K</div>
        <span>Filo Yönetimi</span>
      </div>
      <div class="auth-tagline">
        <h1>Araç Kiralama</h1>
        <p></p>
      </div>
      <ul class="feature-list">
      </ul>
    </div>

    <div class="auth-right">
      <div class="auth-form">
        <h2>Giriş Yap</h2>
        <p class="form-sub">Hesabınıza devam edin</p>

        <div class="field">
          <label>Kullanıcı Adı</label>
          <input v-model="username" type="text" placeholder="kullanici_adi" @keyup.enter="handleLogin" />
        </div>
        <div class="field">
          <label>Şifre</label>
          <input v-model="password" type="password" placeholder="••••••••" @keyup.enter="handleLogin" />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button class="btn-submit" @click="handleLogin">Giriş Yap →</button>

        <button class="btn-guest" @click="router.push('/misafir')">Giriş Yapmadan Devam Et →</button>

        <p class="switch">Hesabın yok mu? <a @click="router.push('/register')">Kayıt Ol</a></p>
      </div>
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
    const { token, username: uname, role } = response.data
    auth.login(token, uname, role)
    if (role === 'admin') router.push('/operator')
    else if (role === 'representative') router.push('/representative')
    else router.push('/dashboard')
  } catch {
    error.value = 'Kullanıcı adı veya şifre hatalı.'
  }
}
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
}

/* Left */
.auth-left {
  width: 44%;
  background: linear-gradient(160deg, #1e293b 0%, #312e81 100%);
  padding: 48px 52px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.auth-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 700;
  color: white;
}
.brand-icon {
  width: 36px;
  height: 36px;
  background: #6366f1;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
  color: white;
}
.auth-tagline h1 {
  font-size: 32px;
  font-weight: 800;
  color: white;
  line-height: 1.2;
  margin-bottom: 14px;
}
.auth-tagline p { font-size: 15px; color: #94a3b8; line-height: 1.6; }
.feature-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px; }
.feature-list li { display: flex; align-items: center; gap: 10px; font-size: 14px; color: #cbd5e1; }
.feat-icon { width: 20px; height: 20px; background: rgba(99,102,241,0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #a5b4fc; font-weight: 700; flex-shrink: 0; }

/* Right */
.auth-right {
  flex: 1;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 40px;
}
.auth-form {
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
h2 { font-size: 26px; font-weight: 800; color: #0f172a; margin: 0; }
.form-sub { font-size: 14px; color: #94a3b8; margin: -8px 0 0; }
.field { display: flex; flex-direction: column; gap: 7px; }
.field label { font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; }
.field input { padding: 11px 14px; border: 1.5px solid #e2e8f0; border-radius: 9px; font-size: 14px; outline: none; transition: border-color 0.2s; }
.field input:focus { border-color: #6366f1; }
.btn-submit { padding: 13px; background: #6366f1; color: white; border: none; border-radius: 10px; font-size: 15px; font-weight: 700; cursor: pointer; transition: background 0.2s, transform 0.1s; margin-top: 4px; }
.btn-submit:hover { background: #4f46e5; transform: translateY(-1px); }
.btn-submit:active { transform: translateY(0); }
.btn-guest { padding: 13px; background: white; color: #6366f1; border: 1.5px solid #6366f1; border-radius: 10px; font-size: 15px; font-weight: 700; cursor: pointer; margin-top: -4px; }
.btn-guest:hover { background: #f5f3ff; }
.error { color: #dc2626; font-size: 13px; background: #fff1f2; padding: 10px 14px; border-radius: 8px; margin: 0; }
.switch { text-align: center; font-size: 13px; color: #64748b; margin: 0; }
.switch a { color: #6366f1; cursor: pointer; font-weight: 700; }

@media (max-width: 768px) {
  .auth-layout { flex-direction: column; }
  .auth-left { width: 100%; padding: 32px 24px; }
  .auth-tagline h1 { font-size: 24px; }
  .feature-list { display: none; }
  .auth-right { padding: 32px 24px; }
}
</style>

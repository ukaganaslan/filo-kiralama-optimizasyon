<template>
  <div class="register-page">

    <!-- Header -->
    <header class="page-header">
      <div class="brand">
        <div class="brand-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 17H3a2 2 0 01-2-2V9a2 2 0 012-2h2M17 17h2a2 2 0 002-2V9a2 2 0 00-2-2h-2"/>
            <rect x="5" y="7" width="14" height="10" rx="2"/>
            <circle cx="7.5" cy="17" r="1.5"/><circle cx="16.5" cy="17" r="1.5"/>
          </svg>
        </div>
        <span class="brand-name">FiloRent</span>
      </div>

    </header>

    <!-- Center Form -->
    <main class="page-center">
      <div class="form-wrap">
        <div class="form-heading">
          <h1>Hesap Oluştur</h1>
          <p>Birkaç bilgiyle hemen başlayın</p>
        </div>

        <div class="fields">
          <input v-model="fullName" type="text" placeholder="Ad Soyad" />
          <div class="field-row">
            <input v-model="email" type="email" placeholder="E-posta" />
            <input v-model="phone" type="tel" placeholder="Telefon" />
          </div>
          <input v-model="username" type="text" placeholder="Kullanıcı adı" autocomplete="username" />
          <input v-model="password" type="password" placeholder="Şifre" autocomplete="new-password" @keyup.enter="handleRegister" />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button class="btn-register" :disabled="loading" @click="handleRegister">{{ loading ? 'Kayıt oluşturuluyor...' : 'Kayıt Ol' }}</button>

        <p class="login-link">
          Hesabın var mı?
          <a @click="router.push('/')">Giriş Yap</a>
        </p>
      </div>
    </main>

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
const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()

async function handleRegister() {
  loading.value = true
  try {
    const response = await axios.post('/api/register/', {
      full_name: fullName.value,
      phone: phone.value,
      email: email.value,
      username: username.value,
      password: password.value,
    })
    auth.login(response.data.token, response.data.username, response.data.role)
    router.push('/dashboard')
  } catch {
    error.value = 'Kayıt sırasında hata oluştu.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.register-page {
  min-height: 100vh;
  background: linear-gradient(160deg, #080618 0%, #0f0b35 45%, #1B1063 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.register-page::before {
  content: '';
  position: absolute;
  top: -200px; left: 50%; transform: translateX(-50%);
  width: 700px; height: 700px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(91,79,205,0.18) 0%, transparent 70%);
  pointer-events: none;
}

.register-page::after {
  content: '';
  position: absolute;
  bottom: -260px; right: -120px;
  width: 560px; height: 560px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(155,145,245,0.12) 0%, transparent 70%);
  pointer-events: none;
}

/* ── Header ── */
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 22px 40px;
  position: relative; z-index: 10;
}

.brand { display: flex; align-items: center; gap: 10px; }
.brand-icon {
  width: 34px; height: 34px;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  color: white;
  transition: background 0.2s, transform 0.2s;
}
.brand:hover .brand-icon { background: rgba(255,255,255,0.18); transform: translateY(-1px); }
.brand-name { font-size: 16px; font-weight: 800; color: white; letter-spacing: -0.01em; }

.header-login-btn {
  font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.5);
  background: none; border: none; cursor: pointer;
  transition: color 0.2s; padding: 6px 0;
}
.header-login-btn:hover { color: rgba(255,255,255,0.85); }

/* ── Center ── */
.page-center {
  flex: 1;
  display: flex; align-items: center; justify-content: center;
  padding: 40px 24px 80px;
  position: relative; z-index: 10;
}

.form-wrap {
  width: 100%;
  max-width: 400px;
  display: flex; flex-direction: column; gap: 14px;
  animation: formIn 0.5s cubic-bezier(0.4,0,0.2,1);
}

@keyframes formIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ── Heading ── */
.form-heading { margin-bottom: 10px; }
.form-heading h1 {
  font-size: 32px; font-weight: 900; color: white;
  letter-spacing: -0.03em; line-height: 1.1;
  margin-bottom: 8px;
}
.form-heading p { font-size: 14px; color: rgba(255,255,255,0.45); }

/* ── Inputs ── */
.fields { display: flex; flex-direction: column; gap: 10px; }

.field-row { display: flex; gap: 10px; }
.field-row input { flex: 1; }

.fields input {
  width: 100%;
  padding: 14px 16px;
  background: rgba(255,255,255,0.07);
  backdrop-filter: blur(8px);
  border: 1.5px solid rgba(255,255,255,0.14);
  border-radius: 12px;
  font-size: 15px;
  color: white;
  outline: none;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.fields input::placeholder { color: rgba(255,255,255,0.3); }
.fields input:focus {
  border-color: rgba(255,255,255,0.4);
  background: rgba(255,255,255,0.1);
  box-shadow: 0 0 0 4px rgba(155,145,245,0.12);
}

/* ── Error ── */
.error-msg {
  font-size: 13px; color: #f87171;
  background: rgba(248,113,113,0.1);
  border: 1px solid rgba(248,113,113,0.25);
  padding: 10px 14px; border-radius: 9px;
}

/* ── Register Button ── */
.btn-register {
  width: 100%; padding: 14px;
  background: white; color: #0f0b35;
  border: none; border-radius: 12px;
  font-size: 15px; font-weight: 800;
  cursor: pointer; transition: all 0.2s;
  margin-top: 4px;
}
.btn-register:hover:not(:disabled) { background: rgba(255,255,255,0.9); transform: translateY(-1px); box-shadow: 0 8px 20px rgba(0,0,0,0.25); }
.btn-register:active:not(:disabled) { transform: translateY(0); }
.btn-register:disabled { opacity: 0.7; }

/* ── Login Link ── */
.login-link {
  text-align: center; font-size: 13px;
  color: rgba(255,255,255,0.35);
  margin-top: 4px;
}
.login-link a {
  color: rgba(255,255,255,0.75);
  cursor: pointer; font-weight: 700;
  transition: color 0.2s;
}
.login-link a:hover { color: white; }

/* ── Responsive ── */
@media (max-width: 480px) {
  .page-header { padding: 18px 20px; }
  .form-heading h1 { font-size: 26px; }
  .header-login-btn { display: none; }
  .field-row { flex-direction: column; }
}
</style>

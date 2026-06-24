<template>
  <div class="auth-layout">
    <div class="auth-left">
      <div class="auth-brand">
        <div class="brand-icon">A</div>
        <span>Araç Kiralama</span>
      </div>
      <div class="auth-tagline">
        <h1>Hızlı kayıt, anında rezervasyon.</h1>
        <p>Üye olun, şubenizi seçin ve aracınızı dakikalar içinde kiralayın.</p>
      </div>
      <ul class="feature-list">
        <li><span class="feat-icon">✓</span> Ücretsiz hesap oluşturma</li>
        <li><span class="feat-icon">✓</span> Anlık müsaitlik görüntüleme</li>
        <li><span class="feat-icon">✓</span> Kolay iptal ve değişiklik</li>
      </ul>
    </div>

    <div class="auth-right">
      <div class="auth-form">
        <h2>Hesap Oluştur</h2>
        <p class="form-sub">Birkaç bilgiyle hemen başlayın</p>

        <div class="field">
          <label>Ad Soyad</label>
          <input v-model="fullName" type="text" placeholder="Ad Soyad" />
        </div>
        <div class="field-row">
          <div class="field">
            <label>Telefon</label>
            <input v-model="phone" type="text" placeholder="05xx xxx xx xx" />
          </div>
          <div class="field">
            <label>E-posta</label>
            <input v-model="email" type="email" placeholder="ornek@mail.com" />
          </div>
        </div>
        <div class="field">
          <label>Kullanıcı Adı</label>
          <input v-model="username" type="text" placeholder="kullanici_adi" />
        </div>
        <div class="field">
          <label>Şifre</label>
          <input v-model="password" type="password" placeholder="••••••••" @keyup.enter="handleRegister" />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button class="btn-submit" @click="handleRegister">Kayıt Ol →</button>

        <p class="switch">Hesabın var mı? <a @click="router.push('/')">Giriş Yap</a></p>
      </div>
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
    auth.login(response.data.token, response.data.username, response.data.role)
    router.push('/dashboard')
  } catch {
    error.value = 'Kayıt sırasında hata oluştu.'
  }
}
</script>

<style scoped>
.auth-layout { min-height: 100vh; display: flex; }
.auth-left { width: 44%; background: linear-gradient(160deg, #1e293b 0%, #312e81 100%); padding: 48px 52px; display: flex; flex-direction: column; justify-content: space-between; }
.auth-brand { display: flex; align-items: center; gap: 12px; font-size: 18px; font-weight: 700; color: white; }
.brand-icon { width: 36px; height: 36px; background: #6366f1; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; color: white; }
.auth-tagline h1 { font-size: 32px; font-weight: 800; color: white; line-height: 1.2; margin-bottom: 14px; }
.auth-tagline p { font-size: 15px; color: #94a3b8; line-height: 1.6; }
.feature-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px; }
.feature-list li { display: flex; align-items: center; gap: 10px; font-size: 14px; color: #cbd5e1; }
.feat-icon { width: 20px; height: 20px; background: rgba(99,102,241,0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #a5b4fc; font-weight: 700; flex-shrink: 0; }
.auth-right { flex: 1; background: white; display: flex; align-items: center; justify-content: center; padding: 48px 40px; }
.auth-form { width: 100%; max-width: 400px; display: flex; flex-direction: column; gap: 16px; }
h2 { font-size: 26px; font-weight: 800; color: #0f172a; margin: 0; }
.form-sub { font-size: 14px; color: #94a3b8; margin: -6px 0 0; }
.field-row { display: flex; gap: 12px; }
.field-row .field { flex: 1; }
.field { display: flex; flex-direction: column; gap: 7px; }
.field label { font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; }
.field input { padding: 11px 14px; border: 1.5px solid #e2e8f0; border-radius: 9px; font-size: 14px; outline: none; transition: border-color 0.2s; }
.field input:focus { border-color: #6366f1; }
.btn-submit { padding: 13px; background: #6366f1; color: white; border: none; border-radius: 10px; font-size: 15px; font-weight: 700; cursor: pointer; transition: background 0.2s, transform 0.1s; margin-top: 4px; }
.btn-submit:hover { background: #4f46e5; transform: translateY(-1px); }
.btn-submit:active { transform: translateY(0); }
.error { color: #dc2626; font-size: 13px; background: #fff1f2; padding: 10px 14px; border-radius: 8px; margin: 0; }
.switch { text-align: center; font-size: 13px; color: #64748b; margin: 0; }
.switch a { color: #6366f1; cursor: pointer; font-weight: 700; }
@media (max-width: 768px) {
  .auth-layout { flex-direction: column; }
  .auth-left { width: 100%; padding: 32px 24px; }
  .auth-tagline h1 { font-size: 24px; }
  .feature-list { display: none; }
  .auth-right { padding: 32px 24px; }
  .field-row { flex-direction: column; }
}
</style>

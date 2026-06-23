<template>
  <div class="page">
    <div class="topbar">
      <div class="brand-group">
        <router-link to="/operator" class="back-link">← Geri</router-link>
        <span class="brand">Profil Ayarları</span>
      </div>
      <span class="role-badge">Operatör</span>
    </div>

    <div class="content">
      <div class="card">
        <h2>Hesap Bilgileri</h2>

        <div class="field">
          <label>Kullanıcı Adı</label>
          <input v-model="form.username" type="text" />
        </div>
        <div class="field">
          <label>Ad Soyad</label>
          <input v-model="form.full_name" type="text" placeholder="Ad Soyad" />
        </div>
        <div class="field">
          <label>E-posta</label>
          <input v-model="form.email" type="email" placeholder="E-posta" />
        </div>
        <div class="field">
          <label>Telefon</label>
          <input v-model="form.phone" type="text" placeholder="Telefon" />
        </div>

        <div class="divider"></div>
        <h3>Şifre Değiştir</h3>
        <div class="field">
          <label>Yeni Şifre</label>
          <input v-model="form.new_password" type="password" placeholder="Boş bırakırsan değişmez" />
        </div>

        <p v-if="success" class="success">{{ success }}</p>
        <p v-if="error" class="error">{{ error }}</p>

        <button class="btn-save" @click="handleSave">Kaydet</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()

const form = ref({ username: '', full_name: '', email: '', phone: '', new_password: '' })
const success = ref('')
const error = ref('')

onMounted(async () => {
  const res = await axios.get('http://127.0.0.1:8000/api/profile/')
  form.value = { ...res.data, new_password: '' }
})

async function handleSave() {
  success.value = ''
  error.value = ''
  try {
    const res = await axios.patch('http://127.0.0.1:8000/api/profile/', {
      username: form.value.username,
      email: form.value.email,
      full_name: form.value.full_name,
      phone: form.value.phone,
      new_password: form.value.new_password || undefined,
    })
    success.value = 'Profil güncellendi.'
    form.value.new_password = ''
    auth.setUsername(form.value.username)
    if (res.data.token) {
      auth.login(res.data.token, form.value.username, auth.isStaff)
    }
  } catch (e) {
    error.value = e.response?.data?.error || 'Güncelleme başarısız.'
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: #f8f9fa; font-family: sans-serif; }
.topbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 40px; background: white; border-bottom: 1px solid #e5e7eb;
}
.brand-group { display: flex; align-items: center; gap: 16px; }
.back-link { font-size: 14px; color: #6366f1; text-decoration: none; font-weight: 500; }
.back-link:hover { text-decoration: underline; }
.brand { font-size: 18px; font-weight: 700; color: #1e293b; }
.role-badge {
  padding: 4px 12px; background: #ede9fe; color: #6366f1;
  border-radius: 50px; font-size: 12px; font-weight: 700;
}
.content { max-width: 520px; margin: 40px auto; padding: 0 24px; }
.card {
  background: white; border-radius: 12px;
  padding: 32px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
h2 { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0 0 24px; }
h3 { font-size: 15px; font-weight: 700; color: #1e293b; margin: 0 0 16px; }
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.field label { font-size: 12px; font-weight: 600; color: #6366f1; text-transform: uppercase; letter-spacing: 0.05em; }
.field input {
  padding: 10px 12px; border: 1px solid #e5e7eb; border-radius: 8px;
  font-size: 14px; color: #1e293b; outline: none;
  background: white;
  color-scheme: light;
}
.field input:focus { border-color: #6366f1; }
.field input:disabled { background: #f8fafc; color: #94a3b8; }
.divider { height: 1px; background: #e5e7eb; margin: 24px 0 20px; }
.btn-save {
  margin-top: 8px; padding: 10px 28px;
  background: #6366f1; color: white; border: none;
  border-radius: 50px; font-size: 14px; font-weight: 600; cursor: pointer;
}
.btn-save:hover { background: #4f46e5; }
.success { color: #16a34a; font-size: 14px; margin-bottom: 8px; }
.error { color: #dc2626; font-size: 14px; margin-bottom: 8px; }
</style>

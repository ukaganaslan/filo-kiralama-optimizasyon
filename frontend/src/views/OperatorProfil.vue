<template>
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
.content { max-width: 560px; margin: 0 auto; padding: 40px 24px; }
.card { background: white; border-radius: 14px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04); }
h2 { font-size: 16px; font-weight: 700; color: #1e293b; margin: 0 0 20px; }
h3 { font-size: 14px; font-weight: 700; color: #1e293b; margin: 0 0 16px; }
.field { display: flex; flex-direction: column; gap: 7px; margin-bottom: 16px; }
.field label { font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; }
.field input { padding: 11px 14px; border: 1.5px solid #e2e8f0; border-radius: 9px; font-size: 14px; color: #1e293b; outline: none; }
.field input:focus { border-color: #6366f1; }
.divider { height: 1px; background: #f1f5f9; margin: 24px 0 20px; }
.btn-save { margin-top: 8px; padding: 11px 28px; background: #6366f1; color: white; border: none; border-radius: 9px; font-size: 14px; font-weight: 700; cursor: pointer; }
.btn-save:hover { background: #4f46e5; }
.success { color: #16a34a; font-size: 13px; background: #f0fdf4; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; font-weight: 500; }
.error { color: #dc2626; font-size: 13px; background: #fff1f2; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; }
</style>

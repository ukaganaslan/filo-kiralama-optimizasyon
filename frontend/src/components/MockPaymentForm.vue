<template>
  <div class="mock-payment">
    <div class="demo-notice">
      <span class="demo-badge">Demo</span>
        Demo Ödeme Ekranı
    </div>

    <div v-if="amount !== null" class="pay-summary">
      <span>Ödenecek Tutar</span>
      <span class="pay-amount">{{ amount.toLocaleString('tr-TR') }} ₺</span>
    </div>

    <div class="card-grid">
      <div class="loc-field loc-field--full">
        <div class="loc-label"><span>Kart Üzerindeki İsim</span></div>
        <input v-model="cardName" type="text" placeholder="AD SOYAD" />
      </div>
      <div class="loc-field loc-field--full">
        <div class="loc-label"><span>Kart Numarası</span></div>
        <input v-model="cardNumber" type="text" maxlength="19" placeholder="0000 0000 0000 0000" @input="formatCardNumber" />
      </div>
      <div class="loc-field">
        <div class="loc-label"><span>Son Kullanma Tarihi</span></div>
        <input v-model="expiry" type="text" maxlength="5" placeholder="AA/YY" @input="formatExpiry" />
      </div>
      <div class="loc-field">
        <div class="loc-label"><span>CVV</span></div>
        <input v-model="cvv" type="text" maxlength="3" placeholder="123" />
      </div>
    </div>

    <p v-if="error" class="form-error">{{ error }}</p>

    <button class="btn-pay" :disabled="submitting" @click="submit">
      <span v-if="submitting" class="pay-spinner"></span>
      {{ submitting ? 'İşleniyor...' : 'Ödemeyi Tamamla' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  amount: { type: Number, default: null },
})
const emit = defineEmits(['confirmed'])

const cardName = ref('')
const cardNumber = ref('')
const expiry = ref('')
const cvv = ref('')
const error = ref('')
const submitting = ref(false)

function formatCardNumber() {
  cardNumber.value = cardNumber.value.replace(/\D/g, '').slice(0, 16).replace(/(.{4})/g, '$1 ').trim()
}

function formatExpiry() {
  let v = expiry.value.replace(/\D/g, '').slice(0, 4)
  if (v.length > 2) v = v.slice(0, 2) + '/' + v.slice(2)
  expiry.value = v
}

function submit() {
  error.value = ''
  const digits = cardNumber.value.replace(/\s/g, '')

  if (!cardName.value.trim()) { error.value = 'Kart üzerindeki ismi girin.'; return }
  if (digits.length !== 16) { error.value = 'Kart numarası 16 haneli olmalı.'; return }

  const match = expiry.value.match(/^(\d{2})\/(\d{2})$/)
  if (!match || Number(match[1]) < 1 || Number(match[1]) > 12) {
    error.value = 'Geçerli bir son kullanma tarihi girin (AA/YY).'
    return
  }
  const expMonth = Number(match[1])
  const expYear = 2000 + Number(match[2])
  const now = new Date()
  if (expYear < now.getFullYear() || (expYear === now.getFullYear() && expMonth < now.getMonth() + 1)) {
    error.value = 'Kartın son kullanma tarihi geçmiş.'
    return
    }
  if (!/^\d{3}$/.test(cvv.value)) { error.value = 'CVV 3 haneli olmalı.'; return }

  submitting.value = true
  setTimeout(() => {
    submitting.value = false
    emit('confirmed')
  }, 600)
}
</script>

<style scoped>
.demo-notice {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 10px;
  font-size: 13.5px;
  color: #92400e;
  font-weight: 500;
  margin-bottom: 20px;
}
.demo-badge {
  background: #F59E0B;
  color: white;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 3px 8px;
  border-radius: 6px;
  flex-shrink: 0;
}

.pay-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 12px;
  margin-bottom: 24px;
  font-size: 13px;
  font-weight: 600;
  color: #4338ca;
}
.pay-amount { font-size: 18px; font-weight: 700; color: #4f46e5; }

.card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.loc-field { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.loc-field--full { grid-column: 1 / -1; }
.loc-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11px;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.loc-field input {
  padding: 12px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 11px;
  font-size: 14px;
  color: #111827;
  outline: none;
  background: #fafafa;
  transition: border 0.2s, color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}
.loc-field input:focus {
  border-color: #1B1063;
  background: white;
  box-shadow: 0 0 0 3px rgba(27,16,99,0.08);
}

.form-error {
  color: #DC2626;
  font-size: 13px;
  background: #fff1f2;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid #fecdd3;
  margin-top: 16px;
}

.btn-pay {
  margin-top: 20px;
  width: 100%;
  padding: 13px 32px;
  background: linear-gradient(135deg, #16A34A, #15803d);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(22,163,74,0.3);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.pay-spinner {
  width: 15px; height: 15px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: white;
  border-radius: 50%;
  animation: paySpin 0.7s linear infinite;
}
@keyframes paySpin { to { transform: rotate(360deg); } }
.btn-pay:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(22,163,74,0.4);
}
.btn-pay:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  box-shadow: none;
  cursor: not-allowed;
  transform: none;
}
</style>
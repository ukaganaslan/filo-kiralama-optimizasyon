<template>
  <div class="notif-bell" ref="root">
    <button class="bell-btn" @click="toggle">
      <i class="pi pi-bell"></i>
      <span v-if="store.unreadCount > 0" class="bell-badge">{{ store.unreadCount > 9 ? '9+' : store.unreadCount }}</span>
    </button>
    <div v-if="open" class="bell-dropdown">
      <div class="bell-header">
        <span>Bildirimler</span>
        <button v-if="store.unreadCount > 0" class="mark-all-btn" @click="store.markAllRead()">Tümünü Okundu İşaretle</button>
      </div>
      <div v-if="store.items.length === 0" class="bell-empty">Bildirim yok</div>
      <div v-else class="bell-list">
        <div
          v-for="n in store.items"
          :key="n.id"
          class="bell-item"
          :class="{ unread: !n.is_read }"
          @click="handleClick(n)"
        >
          <div class="bell-item-title">{{ n.title }}</div>
          <div class="bell-item-message">{{ n.message }}</div>
          <div class="bell-item-time">{{ formatTime(n.created_at) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '../stores/notifications'

const store = useNotificationStore()
const router = useRouter()
const open = ref(false)
const root = ref(null)

function toggle() {
  open.value = !open.value
  if (open.value) store.fetchList()
}

function handleClick(n) {
  if (!n.is_read) store.markRead(n.id)
  open.value = false
  if (n.link) router.push(n.link)
}

function formatTime(iso) {
  const d = new Date(iso)
  return d.toLocaleString('tr-TR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function handleOutsideClick(e) {
  if (root.value && !root.value.contains(e.target)) open.value = false
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  store.startPolling()
})
onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
  store.stopPolling()
})
</script>

<style scoped>
.notif-bell { position: relative; margin-left: auto; }

.bell-btn {
  position: relative;
  background: none; border: none; padding: 6px; border-radius: 7px;
  color: #64748b; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s, color 0.15s;
}
.bell-btn:hover { background: #f1f5f9; color: #1e293b; }
.bell-btn i { font-size: 18px; }

.bell-badge {
  position: absolute; top: 2px; right: 2px;
  background: #dc2626; color: white;
  font-size: 10px; font-weight: 700;
  min-width: 16px; height: 16px; padding: 0 3px;
  border-radius: 50px;
  display: flex; align-items: center; justify-content: center;
  line-height: 1;
  animation: badgePop 0.2s cubic-bezier(0.4,0,0.2,1);
}

@keyframes badgePop {
  from { transform: scale(0.4); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.bell-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  width: 340px; max-height: 420px; overflow-y: auto;
  background: white; border: 1px solid #e2e8f0; border-radius: 14px;
  box-shadow: 0 8px 28px rgba(15,23,42,0.14); z-index: 300;
  animation: bellDropIn 0.15s cubic-bezier(0.4,0,0.2,1);
}

@keyframes bellDropIn {
  from { opacity: 0; transform: translateY(-6px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.bell-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; border-bottom: 1px solid #f1f5f9;
  font-size: 13.5px; font-weight: 700; color: #0f172a;
}

.mark-all-btn {
  background: none; border: none; color: #5548c8;
  font-size: 12px; font-weight: 600; cursor: pointer; padding: 0;
}
.mark-all-btn:hover { text-decoration: underline; }

.bell-empty { padding: 32px 16px; text-align: center; color: #94a3b8; font-size: 13px; }

.bell-item { padding: 12px 16px; border-bottom: 1px solid #f8fafc; cursor: pointer; transition: background 0.15s; }
.bell-item:hover { background: #f8fafc; }
.bell-item:last-child { border-bottom: none; }
.bell-item.unread { background: #f5f3ff; }
.bell-item.unread:hover { background: #ede9fe; }

.bell-item-title { font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 2px; }
.bell-item-message { font-size: 12.5px; color: #475569; line-height: 1.4; }
.bell-item-time { font-size: 11px; color: #94a3b8; margin-top: 4px; }
</style>

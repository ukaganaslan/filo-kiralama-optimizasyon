<template>
  <div class="car-damage-map">
    <div ref="svgWrapper" class="svg-wrapper" @click="handleClick" v-html="svgRaw"></div>

    <div v-if="activePart" class="picker-backdrop" @click="activePart = null"></div>
    <div v-if="activePart" class="damage-picker" :style="pickerStyle" @click.stop>
      <div class="picker-label">{{ partLabel(activePart) }}</div>
      <button
        v-for="(ds, key) in DAMAGE_STATES"
        :key="key"
        :style="{ background: ds.color }"
        @click="setDamage(Number(key))"
      >{{ ds.label }}</button>
    </div>

    <div class="damage-legend">
      <span v-for="(ds, key) in DAMAGE_STATES" :key="key" class="legend-item">
        <span class="legend-dot" :style="{ background: ds.color }"></span>{{ ds.label }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import svgRaw from '@/assets/cardamage_frame.svg?raw'

const props = defineProps({ modelValue: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:modelValue'])

const svgWrapper = ref(null)
const activePart = ref(null)
const pickerPos = ref({ x: 0, y: 0 })

const CAR_PARTS = [
  { id: 'on_tampon',         label: 'Ön Tampon' },
  { id: 'kaput',             label: 'Kaput' },
  { id: 'on_sol_camurluk',   label: 'Ön Sol Çamurluk' },
  { id: 'on_sag_camurluk',   label: 'Ön Sağ Çamurluk' },
  { id: 'on_sol_kapi',       label: 'Ön Sol Kapı' },
  { id: 'tavan',             label: 'Tavan' },
  { id: 'on_sag_kapi',       label: 'Ön Sağ Kapı' },
  { id: 'arka_sol_kapi',     label: 'Arka Sol Kapı' },
  { id: 'arka_sag_kapi',     label: 'Arka Sağ Kapı' },
  { id: 'arka_sol_camurluk', label: 'Arka Sol Çamurluk' },
  { id: 'bagaj',             label: 'Bagaj' },
  { id: 'arka_sag_camurluk', label: 'Arka Sağ Çamurluk' },
  { id: 'arka_tampon',       label: 'Arka Tampon' },
]

const PART_IDS = CAR_PARTS.map(p => p.id)

const DAMAGE_STATES = {
  0: { label: 'Orijinal', color: '#f1f5f9' },
  1: { label: 'Sürtme',   color: '#fef9c3' },
  2: { label: 'Göçük',    color: '#fed7aa' },
  3: { label: 'Çizik',    color: '#fecaca' },
  4: { label: 'Leke',     color: '#dbeafe' },
  5: { label: 'Çatlak',   color: '#e9d5ff' },
  6: { label: 'Eksik',    color: '#fda4af' },
}

const pickerStyle = computed(() => ({
  position: 'fixed',
  left: Math.min(pickerPos.value.x, window.innerWidth - 120) + 'px',
  top: Math.min(pickerPos.value.y, window.innerHeight - 240) + 'px',
}))

function partLabel(id) {
  return CAR_PARTS.find(p => p.id === id)?.label || id
}

function handleClick(e) {
  let el = e.target
  while (el && el !== svgWrapper.value) {
    if (el.id && PART_IDS.includes(el.id)) {
      activePart.value = el.id
      pickerPos.value = { x: e.clientX + 10, y: e.clientY + 10 }
      return
    }
    el = el.parentElement
  }
  activePart.value = null
}

function setDamage(stateVal) {
  const updated = { ...props.modelValue }
  if (stateVal === 0) delete updated[activePart.value]
  else updated[activePart.value] = stateVal
  emit('update:modelValue', updated)
  activePart.value = null
}

function updateColors() {
  if (!svgWrapper.value) return
  PART_IDS.forEach(id => {
    const el = svgWrapper.value.querySelector(`#${id}`)
    if (!el) return
    const state = props.modelValue[id] || 0
    el.setAttribute('fill', DAMAGE_STATES[state].color)
    el.setAttribute('fill-opacity', '0.72')
    el.style.cursor = 'pointer'
    el.style.transition = 'fill 0.15s'
  })
}

onMounted(updateColors)
watch(() => props.modelValue, updateColors, { deep: true })
</script>

<style scoped>
.car-damage-map { display: flex; flex-direction: column; gap: 12px; align-items: center; }
.svg-wrapper { border-radius: 10px; overflow: hidden; max-width: 280px; }
.svg-wrapper :deep(svg) { display: block; width: 100%; height: auto; }
.picker-backdrop { position: fixed; inset: 0; z-index: 999; }
.damage-picker { position: fixed; z-index: 1000; background: white; border: 1px solid #e2e8f0; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.14); padding: 8px; display: flex; flex-direction: column; gap: 4px; min-width: 110px; }
.picker-label { font-size: 10px; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.06em; padding: 2px 4px 6px; border-bottom: 1px solid #f1f5f9; margin-bottom: 2px; }
.damage-picker button { padding: 6px 10px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 12px; cursor: pointer; text-align: left; }
.damage-picker button:hover { filter: brightness(0.92); }
.damage-legend { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; max-width: 280px; }
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 11px; color: #475569; }
.legend-dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; border: 1px solid #cbd5e1; }
</style>

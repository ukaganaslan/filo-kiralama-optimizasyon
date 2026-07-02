import { ref, computed } from 'vue'

// Tablo başlığına tıklayınca sıralama sağlar.
// rows: ref/computed (dizi). accessors: { kolonAnahtarı: (satır) => değer } — özel/hesaplanan kolonlar için.
export function useTableSort(rows, accessors = {}) {
  const sortKey = ref('')
  const sortDir = ref('asc')

  function sortBy(key) {
    if (sortKey.value === key) {
      sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey.value = key
      sortDir.value = 'asc'
    }
  }

  function sortArrow(key) {
    if (sortKey.value !== key) return ''
    return sortDir.value === 'asc' ? '▲' : '▼'
  }

  function valueOf(row, key) {
    const acc = accessors[key]
    const v = acc ? acc(row) : row[key]
    return v == null ? '' : v
  }

  const sorted = computed(() => {
    const list = rows.value ? [...rows.value] : []
    if (!sortKey.value) return list
    return list.sort((a, b) => {
      const va = valueOf(a, sortKey.value)
      const vb = valueOf(b, sortKey.value)
      const cmp = (typeof va === 'number' && typeof vb === 'number')
        ? va - vb
        : String(va).localeCompare(String(vb), 'tr', { numeric: true })
      return sortDir.value === 'asc' ? cmp : -cmp
    })
  })

  return { sortKey, sortDir, sortBy, sortArrow, sorted }
}

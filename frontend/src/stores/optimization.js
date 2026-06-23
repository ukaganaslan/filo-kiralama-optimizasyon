import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useOptimizationStore = defineStore('optimization', () => {
  const result = ref(null)

  function setResult(data) {
    result.value = data
  }

  return { result, setResult }
})

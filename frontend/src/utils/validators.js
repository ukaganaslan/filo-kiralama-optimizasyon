export function isValidTCKN(value) {
  if (!/^\d{11}$/.test(value || '')) return false
  const lastDigit = Number(String(value)[10])
  return lastDigit % 2 === 0
}

export function isValidVKN(value) {
  return /^\d{10}$/.test(value || '')
}
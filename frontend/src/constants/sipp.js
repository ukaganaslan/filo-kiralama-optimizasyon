export const CATEGORY_LABELS = {
  M: 'Mini',
  E: 'Ekonomi',
  C: 'Kompakt',
  I: 'Orta',
  S: 'Standart',
  F: 'Tam Boyut',
  P: 'Premium',
  L: 'Lüks',
  X: 'Özel',
}

export const CATEGORY_ORDER = ['M', 'E', 'C', 'I', 'S', 'F', 'P', 'L', 'X']

export const CATEGORY_COLORS = {
  M: { bg: '#fef3c7', border: '#d97706', text: '#92400e' },
  E: { bg: '#ede9fe', border: '#7c3aed', text: '#5b21b6' },
  C: { bg: '#e0f2fe', border: '#0284c7', text: '#075985' },
  I: { bg: '#dbeafe', border: '#2563eb', text: '#1e40af' },
  S: { bg: '#ccfbf1', border: '#0d9488', text: '#115e59' },
  F: { bg: '#d1fae5', border: '#059669', text: '#065f46' },
  P: { bg: '#ffedd5', border: '#ea580c', text: '#9a3412' },
  L: { bg: '#fce7f3', border: '#db2777', text: '#9d174d' },
  X: { bg: '#f1f5f9', border: '#475569', text: '#1e293b' },
}

export function categoryLabel(code) {
  return CATEGORY_LABELS[code] || code
}

import ilIlceData from '../data/turkiyeIlIlce.json'

export const ILLER = Object.keys(ilIlceData).sort((a, b) => a.localeCompare(b, 'tr'))

export function getIlceler(il) {
  if (!il || !ilIlceData[il]) return []
  return [...ilIlceData[il]].sort((a, b) => a.localeCompare(b, 'tr'))
}

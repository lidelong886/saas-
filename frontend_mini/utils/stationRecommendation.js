function toNumber(value, fallback = 0) {
  const num = Number(value)
  return Number.isFinite(num) ? num : fallback
}

function normalizeDistance(distance) {
  const num = toNumber(distance, Infinity)
  if (!Number.isFinite(num)) return Infinity
  return num > 100 ? num / 1000 : num
}

function isInBusinessHours(station) {
  if (!station) return 1
  if (station.is_24_hour) return 1
  if (!station.business_hours) return 1

  const match = String(station.business_hours).match(/(\d{2}):(\d{2})\s*[-–]\s*(\d{2}):(\d{2})/)
  if (!match) return 1

  const now = new Date()
  const currentMinutes = now.getHours() * 60 + now.getMinutes()
  const openMinutes = Number(match[1]) * 60 + Number(match[2])
  const closeMinutes = Number(match[3]) * 60 + Number(match[4])

  if (closeMinutes < openMinutes) {
    return currentMinutes >= openMinutes || currentMinutes <= closeMinutes ? 1 : 0.1
  }

  return currentMinutes >= openMinutes && currentMinutes <= closeMinutes ? 1 : 0.1
}

function pickRecommendedStation(stations, batteryInsight) {
  if (!Array.isArray(stations) || stations.length === 0) return null

  const candidates = stations.filter((station) => {
    const status = station.status || 'active'
    return status === 'active' && toNumber(station.available_batteries) > 0
  })

  const pool = candidates.length > 0 ? candidates : stations
  const maxDistance = Math.max(...pool.map((station) => normalizeDistance(station.distance)).filter(Number.isFinite), 1)
  const maxAvailable = Math.max(...pool.map((station) => toNumber(station.available_batteries, 0)), 1)
  const alertLevel = batteryInsight && batteryInsight.alertLevel
  const isUrgent = alertLevel === 'warning' || alertLevel === 'emergency'

  let best = null
  let bestScore = -Infinity

  pool.forEach((station) => {
    const available = toNumber(station.available_batteries, 0)
    const distanceKm = normalizeDistance(station.distance)
    const status = station.status || 'active'
    const distanceScore = Number.isFinite(distanceKm) ? 1 - Math.min(distanceKm / maxDistance, 1) : 0
    const availabilityScore = Math.min(available / maxAvailable, 1)
    const statusScore = status === 'active' ? 1 : status === 'maintenance' ? 0.25 : 0.1
    const businessScore = isInBusinessHours(station)
    const baseScore = distanceScore * (isUrgent ? 0.65 : 0.45) + availabilityScore * (isUrgent ? 0.25 : 0.45) + statusScore * 0.1
    const score = baseScore * businessScore

    if (score > bestScore) {
      bestScore = score
      best = {
        ...station,
        recommendScore: Number(score.toFixed(3))
      }
    }
  })

  return best
}

function getRecommendationReason(station, batteryInsight) {
  if (!station) return ''

  const available = toNumber(station.available_batteries, 0)
  const distanceKm = normalizeDistance(station.distance)
  const alertLevel = batteryInsight && batteryInsight.alertLevel
  const distanceText = Number.isFinite(distanceKm)
    ? (distanceKm < 0.1 ? '100米内' : distanceKm < 1 ? `${Math.round(distanceKm * 1000)}米` : `${distanceKm.toFixed(1)}km`)
    : '附近'

  if (alertLevel === 'emergency') {
    if (Number.isFinite(distanceKm) && distanceKm <= 1) {
      return `电量紧急！最近站点在${distanceText}，有${available}块电池可换，建议立即前往`
    }
    return `电量紧急！推荐前往${station.name}（${distanceText}），有${available}块可用电池`
  }

  if (alertLevel === 'warning') {
    return `电量偏低，建议尽快去${station.name}换电（${distanceText}，${available}块电池可用）`
  }

  if (available >= 5) {
    return `${station.name}电池充足（${available}块可用），距你${distanceText}`
  }
  if (Number.isFinite(distanceKm) && distanceKm <= 0.5) {
    return `${station.name}就在附近（${distanceText}），有${available}块电池`
  }
  return `综合推荐${station.name}，距离${distanceText}，${available}块电池可用`
}

module.exports = {
  pickRecommendedStation,
  getRecommendationReason
}

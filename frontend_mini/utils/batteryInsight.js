function clamp(value, min, max) {
  return Math.min(Math.max(Number(value) || 0, min), max)
}

function normalizePowerLevel(battery) {
  if (!battery) return 0
  if (battery.power_level != null) return clamp(battery.power_level, 0, 100)
  if (battery.power != null) return clamp(battery.power, 0, 100)
  return 0
}

function getAlertLevel(powerLevel) {
  if (powerLevel <= 20) return 'emergency'
  if (powerLevel <= 35) return 'warning'
  if (powerLevel >= 90) return 'excellent'
  return 'normal'
}

function getAlertText(level) {
  if (level === 'emergency') return '电量很低，建议立即前往换电'
  if (level === 'warning') return '电量偏低，建议尽快规划换电'
  if (level === 'excellent') return '电量充足，可放心继续骑行'
  return '当前电量稳定，可继续接单'
}

function getAlertTag(level) {
  if (level === 'emergency') return '紧急'
  if (level === 'warning') return '注意'
  if (level === 'excellent') return '充足'
  return '正常'
}

function estimateRangeKm(powerLevel) {
  const fullRangeKm = 110
  const safeReserve = powerLevel <= 15 ? 0.85 : 1
  return Math.max(0, Number(((powerLevel / 100) * fullRangeKm * safeReserve).toFixed(1)))
}

function estimateMinutes(rangeKm) {
  const avgSpeedKmH = 22
  return Math.max(0, Math.round((rangeKm / avgSpeedKmH) * 60))
}

function getBatteryInsight(battery) {
  const powerLevel = normalizePowerLevel(battery)
  const estimatedRangeKm = estimateRangeKm(powerLevel)
  const estimatedMinutes = estimateMinutes(estimatedRangeKm)
  const alertLevel = getAlertLevel(powerLevel)

  return {
    powerLevel,
    estimatedRangeKm,
    estimatedMinutes,
    alertLevel,
    alertTag: getAlertTag(alertLevel),
    alertText: getAlertText(alertLevel),
    rangeText: `预计还能骑行 ${estimatedRangeKm} km`,
    durationText: `按配送场景约可使用 ${estimatedMinutes} 分钟`,
    summaryText: `${powerLevel}% 电量，约 ${estimatedRangeKm} km / ${estimatedMinutes} 分钟`
  }
}

module.exports = {
  normalizePowerLevel,
  getBatteryInsight
}

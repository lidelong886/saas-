const request = require('../utils/request')

const getPackageRecommendations = (limit = 3) => {
  return request.get('/recommend/packages', { limit })
}

module.exports = {
  getPackageRecommendations
}

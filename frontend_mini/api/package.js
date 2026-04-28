const request = require('../utils/request')

const getPackages = (params) => {
  return request.get('/package/list', params)
}

const getPackageDetail = (id) => {
  return request.get(`/package/${id}`)
}

const getRiderPackages = () => {
  return request.get('/rider/packages')
}

module.exports = {
  getPackages,
  getPackageDetail,
  getRiderPackages
}

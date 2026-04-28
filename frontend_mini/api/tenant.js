const request = require('../utils/request')

const getTenantList = () => request.get('/tenant/list')

const submitTenantApplication = (data) => request.post('/tenant/apply', data)

module.exports = {
  getTenantList,
  submitTenantApplication
}

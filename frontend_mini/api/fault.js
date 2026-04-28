// 故障报修相关API
const request = require('../utils/request')

// 提交故障报修
const submitFaultReport = (data) => {
  return request.post('/fault-report', data)
}

// 获取我的报修列表
const getMyFaultReports = (params) => {
  return request.get('/fault-report/my', params)
}

// 获取报修详情
const getFaultReportDetail = (reportNo) => {
  return request.get(`/fault-report/${reportNo}`)
}

module.exports = {
  submitFaultReport,
  getMyFaultReports,
  getFaultReportDetail
}

// 站点页面共享方法 mixin
import { ElMessage } from 'element-plus'
import { geocodeAddress } from '@/api/station'

export default {
  data() {
    return {
      locating: false
    }
  },
  methods: {
    /**
     * 按地址自动定位经纬度
     * @param {string} address - 地址字符串（由组件显式传入，不再依赖 this.form）
     */
    async handleLocateByAddress(address) {
      const addr = (address || '').toString().trim()
      if (!addr) {
        ElMessage.warning('请先输入详细地址')
        return
      }

      this.locating = true
      try {
        const res = await geocodeAddress({ address: addr })

        // axios 拦截器已自动 unwrap: res = { code: 200, message: '...', data: {...} }
        if (!res) {
          ElMessage.warning('接口返回数据异常，请检查网络')
          return
        }

        // res.data 是 geocode 的结果：{ longitude, latitude, address, ... }
        const geoData = res?.data
        if (!geoData || !geoData.latitude || !geoData.longitude) {
          ElMessage.warning('未找到匹配地址，请补充更详细的位置描述')
          return
        }

        // 填充到 form（兼容 create/edit 的 this.form 和 index 的 this.formData）
        const targetForm = this.form ?? this.formData
        if (targetForm) {
          targetForm.latitude = Number(geoData.latitude)
          targetForm.longitude = Number(geoData.longitude)
          if (geoData.address) {
            targetForm.address = geoData.address
          }
        }

        ElMessage.success('已根据地址自动定位')
      } catch (error) {
        console.error('[Geocode] 定位失败', error)
        const backendMsg = error?.response?.data?.message || error?.message
        ElMessage.error(backendMsg || '地址定位失败，请手动填写经纬度')
      } finally {
        this.locating = false
      }
    }
  }
}

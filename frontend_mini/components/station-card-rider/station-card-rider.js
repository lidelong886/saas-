// 骑手站点卡片组件
Component({
  properties: {
    // 站点信息
    station: {
      type: Object,
      value: {},
      observer: function(newVal) {
        if (newVal && newVal.available_batteries !== undefined) {
          this.updateBatteryStatus(newVal.available_batteries);
        }
      }
    }
  },

  data: {
    batteryStatus: 'available' // available | low | empty
  },

  methods: {
    // 更新电池状态
    updateBatteryStatus(count) {
      let status = 'available';
      if (count === 0) {
        status = 'empty';
      } else if (count > 0 && count <= 5) {
        status = 'low';
      }
      this.setData({ batteryStatus: status });
    },

    // 导航到站点
    onNavigate(e) {
      e.stopPropagation();
      const { station } = this.data;

      if (!station || !station.lat || !station.lng) {
        wx.showToast({
          title: '站点位置信息缺失',
          icon: 'none'
        });
        return;
      }

      // 触发父组件的导航事件
      this.triggerEvent('navigate', {
        station: station
      });

      // 调用微信地图导航
      wx.openLocation({
        latitude: station.lat,
        longitude: station.lng,
        name: station.name,
        address: station.address || '',
        scale: 15
      });
    }
  }
});

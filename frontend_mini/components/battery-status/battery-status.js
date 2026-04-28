// 电池状态指示灯组件
Component({
  properties: {
    // 电池数量
    count: {
      type: Number,
      value: 0,
      observer: function(newVal) {
        this.updateStatus(newVal);
      }
    }
  },

  data: {
    status: 'empty', // available | low | empty
    statusText: '无电池'
  },

  lifetimes: {
    attached() {
      this.updateStatus(this.data.count);
    }
  },

  methods: {
    // 根据电池数量更新状态
    updateStatus(count) {
      let status = 'empty';
      let statusText = '无电池';

      if (count > 5) {
        status = 'available';
        statusText = '可用';
      } else if (count >= 1 && count <= 5) {
        status = 'low';
        statusText = '紧张';
      }

      this.setData({
        status,
        statusText
      });
    }
  }
});

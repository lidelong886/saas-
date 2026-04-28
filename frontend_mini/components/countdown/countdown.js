Component({
  properties: {
    // 结束时间戳（毫秒）
    endTime: {
      type: Number,
      value: 0,
      observer: 'startCountdown'
    },
    // 标签文本
    label: {
      type: String,
      value: '剩余时间'
    },
    // 是否显示进度条
    showProgress: {
      type: Boolean,
      value: true
    },
    // 总时长（用于计算进度，毫秒）
    totalDuration: {
      type: Number,
      value: 30 * 60 * 1000 // 默认30分钟
    },
    // 自定义样式类
    className: {
      type: String,
      value: ''
    }
  },

  data: {
    minutes: 0,
    seconds: 0,
    progress: 100,
    timer: null
  },

  lifetimes: {
    detached() {
      this.clearTimer();
    }
  },

  methods: {
    startCountdown() {
      this.clearTimer();
      this.updateTime();

      const timer = setInterval(() => {
        this.updateTime();
      }, 1000);

      this.setData({ timer });
    },

    updateTime() {
      const now = Date.now();
      const remaining = Math.max(0, this.data.endTime - now);

      if (remaining === 0) {
        this.clearTimer();
        this.triggerEvent('timeout');
        return;
      }

      const totalSeconds = Math.floor(remaining / 1000);
      const minutes = Math.floor(totalSeconds / 60);
      const seconds = totalSeconds % 60;

      // 计算进度百分比
      const elapsed = this.data.totalDuration - remaining;
      const progress = Math.max(0, Math.min(100, 100 - (elapsed / this.data.totalDuration * 100)));

      this.setData({
        minutes,
        seconds,
        progress
      });

      // 剩余时间少于5分钟时触发警告
      if (remaining <= 5 * 60 * 1000 && remaining > 4 * 60 * 1000) {
        this.triggerEvent('warning', { remaining });
      }
    },

    clearTimer() {
      if (this.data.timer) {
        clearInterval(this.data.timer);
        this.setData({ timer: null });
      }
    }
  }
});

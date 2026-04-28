const { getReservationList, cancelReservation } = require('../../../api/reservation')
const { formatTime } = require('../../../utils/util')

Page({
  data: {
    tabs: [
      { key: 'active', label: '进行中' },
      { key: 'completed', label: '已完成' },
      { key: 'all', label: '全部' }
    ],
    activeTab: 'active',
    reservations: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false,
    refreshing: false
  },

  onLoad() {
    this.loadReservations();
  },

  onShow() {
    // 每次显示页面时刷新数据
    this.refreshData();
  },

  switchTab(e) {
    const key = e.currentTarget.dataset.key;
    this.setData({
      activeTab: key,
      reservations: [],
      page: 1,
      hasMore: true
    });
    this.loadReservations();
  },

  async loadReservations() {
    if (this.data.loading || !this.data.hasMore) return;

    try {
      this.setData({ loading: true });

      const params = {
        page: this.data.page,
        page_size: this.data.pageSize
      };

      // 根据标签筛选状态
      if (this.data.activeTab === 'active') {
        params.status = 'active';
      } else if (this.data.activeTab === 'completed') {
        params.status = 'completed';
      }

      const res = await getReservationList(params);

      if (res.code === 200) {
        const newReservations = res.data.items.map(item => {
          // 格式化时间
          item.reserved_at_formatted = formatTime(new Date(item.reserved_at));
          item.expires_at_formatted = formatTime(new Date(item.expires_at));
          if (item.completed_at) {
            item.completed_at_formatted = formatTime(new Date(item.completed_at));
          }

          // 转换时间戳为毫秒
          item.expires_at = new Date(item.expires_at).getTime();

          return item;
        });

        this.setData({
          reservations: [...this.data.reservations, ...newReservations],
          hasMore: res.data.has_more,
          page: this.data.page + 1
        });
      }
    } catch (error) {
      console.error('加载预约列表失败:', error);
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  async onRefresh() {
    this.setData({
      refreshing: true,
      reservations: [],
      page: 1,
      hasMore: true
    });

    await this.loadReservations();

    this.setData({ refreshing: false });
  },

  onLoadMore() {
    this.loadReservations();
  },

  refreshData() {
    this.setData({
      reservations: [],
      page: 1,
      hasMore: true
    });
    this.loadReservations();
  },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/reservation/detail/detail?id=${id}`
    });
  },

  cancelReservation(e) {
    const id = e.currentTarget.dataset.id;

    wx.showModal({
      title: '确认取消',
      content: '确定要取消这个预约吗？',
      confirmText: '确认取消',
      confirmColor: '#FF3B30',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '取消中...' });
            const result = await cancelReservation(id);

            wx.hideLoading();

            if (result.code === 200) {
              wx.showToast({
                title: '已取消预约',
                icon: 'success'
              });

              // 刷新列表
              setTimeout(() => {
                this.refreshData();
              }, 1500);
            } else {
              wx.showModal({
                title: '取消失败',
                content: result.message || '请稍后重试',
                showCancel: false
              });
            }
          } catch (error) {
            wx.hideLoading();
            console.error('取消预约失败:', error);
            wx.showModal({
              title: '取消失败',
              content: '网络错误，请稍后重试',
              showCancel: false
            });
          }
        }
      }
    });
  },

  goToStation(e) {
    const station = e.currentTarget.dataset.station;

    wx.openLocation({
      latitude: parseFloat(station.latitude),
      longitude: parseFloat(station.longitude),
      name: station.name,
      address: station.address,
      scale: 15
    });
  },

  goToStationList() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  }
});

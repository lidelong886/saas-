const PORT = process.env.PORT || 8083

module.exports = {
  // 禁用ESLint
  lintOnSave: false,

  // 开发服务器配置
  devServer: {
    port: PORT,
    host: 'localhost',
    open: true,

    // 关键配置：代理API请求到后端
    proxy: {
      '/api/v1': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
        ws: true,
        logLevel: 'debug'
      }
    },

    // 解决页面刷新404问题
    historyApiFallback: {
      rewrites: [
        { from: /.*/, to: '/index.html' }
      ]
    }
  },

  // 构建配置
  configureWebpack: {
    resolve: {
      alias: {
        '@': require('path').resolve(__dirname, 'src')
      }
    }
  }
}

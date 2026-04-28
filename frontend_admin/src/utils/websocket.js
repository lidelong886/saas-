import { io } from 'socket.io-client'
import { getToken } from './auth'

class WebSocketService {
  constructor() {
    this.socket = null
    this.listeners = new Map()
  }

  connect() {
    if (this.socket?.connected) {
      return
    }

    const token = getToken()
    this.socket = io(process.env.VUE_APP_BASE_API || 'http://localhost:5000', {
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
    })

    // 注册所有监听器
    this.listeners.forEach((callback, event) => {
      this.socket.on(event, callback)
    })
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  on(event, callback) {
    this.listeners.set(event, callback)
    if (this.socket?.connected) {
      this.socket.on(event, callback)
    }
  }

  off(event) {
    this.listeners.delete(event)
    if (this.socket) {
      this.socket.off(event)
    }
  }

  emit(event, data) {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    }
  }
}

export default new WebSocketService()

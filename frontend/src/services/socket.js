import { io } from 'socket.io-client'

// Same-origin by default (Vite proxies /socket.io). Override with VITE_API_URL if needed.
const SOCKET_URL = import.meta.env.VITE_API_URL || undefined

let socket = null

export function getAdminSocket() {
  if (!socket) {
    socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      autoConnect: false,
    })
  }
  return socket
}

export function connectAdminSocket() {
  const instance = getAdminSocket()
  if (!instance.connected) {
    instance.connect()
  }
  return instance
}

export function disconnectAdminSocket() {
  if (socket?.connected) {
    socket.disconnect()
  }
}

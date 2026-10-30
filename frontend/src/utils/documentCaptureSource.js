// Keep the source with the actual File across front/back navigation. An arbitrary
// uploaded File never inherits the source of a previously captured photo.
const sources = new WeakMap()

export function markCameraCapture(file) {
  sources.set(file, 'camera')
  return file
}

export function documentCaptureSource(file) {
  return file ? sources.get(file) || 'upload' : null
}

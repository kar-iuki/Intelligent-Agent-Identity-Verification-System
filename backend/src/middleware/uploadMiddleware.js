import multer from 'multer'

const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png']
const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB

const storage = multer.memoryStorage()

function fileFilter(_req, file, cb) {
  if (!ALLOWED_MIME_TYPES.includes(file.mimetype)) {
    return cb(new Error('Only JPEG and PNG image files are allowed'))
  }
  cb(null, true)
}

const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: MAX_FILE_SIZE,
  },
})

export const uploadAgentDocuments = upload.fields([
  { name: 'documentImage', maxCount: 1 },
  { name: 'selfieImage', maxCount: 1 },
])

export function handleMulterError(err, _req, res, next) {
  if (!err) return next()

  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'Each file must be 5MB or smaller' })
    }
    return res.status(400).json({ error: err.message })
  }

  if (err.message) {
    return res.status(400).json({ error: err.message })
  }

  return next(err)
}

export default upload

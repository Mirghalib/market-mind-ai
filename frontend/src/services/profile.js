import api from './api'

/**
 * Profile endpoints — multipart upload for the avatar image.
 * The axios interceptor already attaches the Bearer token.
 */
export const profileService = {
  /**
   * Update profile fields (JSON).
   */
  updateProfile: (data) => api.patch('/profile', data),

  /**
   * Upload the avatar image as multipart/form-data.
   * Accepts a callback for upload progress (0-100).
   */
  uploadAvatar: (file, onProgress) => {
    const formData = new FormData()
    formData.append('avatar', file)
    return api.post('/profile/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          onProgress(Math.round((event.loaded / event.total) * 100))
        }
      },
    })
  },
}

import api from './api'

/**
 * Profile endpoints. Profile update + avatar upload are handled by the
 * backend's PUT /dashboard/profile (multipart/form-data with optional
 * `full_name` and `profile_image` fields). The axios interceptor
 * already attaches the Bearer token.
 */
export const profileService = {
  /**
   * Update the own profile. Pass `{ full_name }` and/or a `File` as
   * `profile_image`. Returns the updated ProfileResponse.
   */
  updateProfile: (data, onProgress) => {
    const formData = new FormData()
    if (data?.full_name) formData.append('full_name', data.full_name)
    if (data?.profile_image instanceof File) {
      formData.append('profile_image', data.profile_image)
    }
    return api.put('/dashboard/profile', formData, {
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          onProgress(Math.round((event.loaded / event.total) * 100))
        }
      },
    })
  },

  /** Get the own profile (includes role and profile image URL). */
  getProfile: () => api.get('/dashboard/profile'),
}

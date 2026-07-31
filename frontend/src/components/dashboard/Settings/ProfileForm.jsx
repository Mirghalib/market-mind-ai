import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Camera, CheckCircle2, Image, Loader2, Save, Trash2, Upload, User, XCircle } from 'lucide-react'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'
import Button from '@/components/ui/Button'
import { useAuth } from '@/context/AuthContext'
import { profileService } from '@/services/profile'
import { cn } from '@/utils/cn'

const ROLES = ['Marketing Lead', 'Founder', 'Marketer', 'Agency Owner', 'Other']

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const ACCEPTED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']
const MAX_SIZE_MB = 5
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

function getInitials(name) {
  return (name || 'User')
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

function validateImage(file) {
  const extension = file.name.split('.').pop()?.toLowerCase()
  const typeOk = ACCEPTED_TYPES.includes(file.type) || ACCEPTED_EXTENSIONS.includes(extension)
  if (!typeOk) {
    return `Unsupported format. Use JPG, PNG, JPEG, or WEBP (got .${extension || 'unknown'}).`
  }
  if (file.size > MAX_SIZE_BYTES) {
    return `Image is too large (${(file.size / (1024 * 1024)).toFixed(1)} MB). Maximum is ${MAX_SIZE_MB} MB.`
  }
  return null
}

/**
 * Profile form with avatar upload. Supports drag-and-drop or file
 * selection, previews the image, validates type/size, submits the
 * avatar as multipart/form-data, and shows upload progress.
 */
export default function ProfileForm() {
  const { user } = useAuth()
  const [values, setValues] = useState({
    name: user?.name ?? '',
    email: user?.email ?? '',
    company: '',
    role: '',
  })

  const [avatarUrl, setAvatarUrl] = useState(user?.avatarUrl ?? user?.avatar ?? '')
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [fileError, setFileError] = useState('')
  const [dragging, setDragging] = useState(false)
  const [saving, setSaving] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState(null) // { type: 'success' | 'error', message }
  const inputRef = useRef(null)

  // Revoke object URLs to avoid memory leaks.
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const handleFile = (file) => {
    if (!file) return
    const error = validateImage(file)
    setFileError(error ?? '')
    if (error) return

    setSelectedFile(file)
    setStatus(null)
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(URL.createObjectURL(file))
  }

  const handleInputChange = (event) => {
    handleFile(event.target.files?.[0])
    event.target.value = '' // allow re-selecting the same file
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setDragging(false)
    handleFile(event.dataTransfer.files?.[0])
  }

  const removeImage = () => {
    setSelectedFile(null)
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(null)
    setAvatarUrl('')
    setFileError('')
    setStatus(null)
  }

  const handleChange = (event) => {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setStatus(null)

    try {
      setSaving(true)
      await profileService.updateProfile(values)
      setStatus({ type: 'success', message: 'Profile updated successfully.' })
    } catch (err) {
      setStatus({
        type: 'error',
        message: err.response?.data?.message || err.message || 'Could not save profile.',
      })
    } finally {
      setSaving(false)
    }

    if (!selectedFile) return

    try {
      setUploading(true)
      setProgress(0)
      const { data } = await profileService.uploadAvatar(selectedFile, setProgress)
      setSelectedFile(null)
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
      setAvatarUrl(data?.avatarUrl ?? data?.avatar ?? previewUrl ?? '')
      setStatus({ type: 'success', message: 'Profile image uploaded successfully.' })
    } catch (err) {
      setStatus({
        type: 'error',
        message: err.response?.data?.message || err.message || 'Could not upload image.',
      })
    } finally {
      setUploading(false)
    }
  }

  const showImage = previewUrl || avatarUrl

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm sm:p-8 dark:border-white/10 dark:bg-white/[0.03] dark:shadow-lg dark:shadow-black/20 dark:backdrop-blur"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-600 dark:text-indigo-400">
          <User size={19} strokeWidth={1.75} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-white">Profile</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Update your personal information.</p>
        </div>
      </div>

      {status && (
        <div
          role="status"
          className={cn(
            'mt-6 flex items-center gap-2 rounded-xl border px-4 py-3 text-sm font-medium',
            status.type === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-400'
              : 'border-red-200 bg-red-50 text-red-700 dark:border-red-500/20 dark:bg-red-500/10 dark:text-red-400'
          )}
        >
          {status.type === 'success' ? <CheckCircle2 size={17} /> : <XCircle size={17} />}
          {status.message}
        </div>
      )}

      {/* Avatar upload */}
      <div className="mt-6 flex flex-col items-center gap-6 sm:flex-row sm:items-start">
        {/* Circular preview */}
        <div className="relative shrink-0">
          <div className="flex h-28 w-28 items-center justify-center overflow-hidden rounded-full border-4 border-zinc-200 bg-zinc-100 dark:border-white/10 dark:bg-zinc-800">
            {showImage ? (
              <img
                src={showImage}
                alt="Profile preview"
                className="h-full w-full object-cover"
              />
            ) : (
              <span className="text-3xl font-semibold text-zinc-500 dark:text-zinc-400">
                {getInitials(values.name)}
              </span>
            )}
          </div>
          {/* Camera badge */}
          <span className="absolute -right-1 -bottom-1 flex h-9 w-9 items-center justify-center rounded-full border-2 border-white bg-indigo-500 text-white dark:border-zinc-900">
            <Camera size={15} />
          </span>
        </div>

        {/* Drop zone + actions */}
        <div className="w-full flex-1">
          <div
            role="button"
            tabIndex={0}
            aria-label="Upload profile image"
            onClick={() => inputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click()
            }}
            onDragOver={(e) => {
              e.preventDefault()
              setDragging(true)
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            className={cn(
              'flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-6 text-center transition-colors',
              dragging
                ? 'border-indigo-500 bg-indigo-500/[0.06]'
                : 'border-zinc-300 hover:border-indigo-400 dark:border-zinc-700 dark:hover:border-indigo-500'
            )}
          >
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-600 dark:text-indigo-400">
              <Upload size={18} strokeWidth={1.75} />
            </span>
            <div>
              <p className="text-sm font-medium text-zinc-900 dark:text-white">
                Drag & drop or{' '}
                <span className="text-indigo-600 dark:text-indigo-400">browse</span>
              </p>
              <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                JPG, PNG, JPEG or WEBP · max {MAX_SIZE_MB} MB
              </p>
            </div>
          </div>

          <input
            ref={inputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
            onChange={handleInputChange}
            className="hidden"
            aria-hidden
          />

          {fileError && (
            <p className="mt-2 flex items-center gap-1.5 text-sm text-red-500 dark:text-red-400">
              <XCircle size={14} />
              {fileError}
            </p>
          )}

          {(selectedFile || avatarUrl) && (
            <button
              type="button"
              onClick={removeImage}
              className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-red-500 transition-colors hover:text-red-400 dark:text-red-400 dark:hover:text-red-300"
            >
              <Trash2 size={14} />
              Remove image
            </button>
          )}

          {/* Upload progress */}
          {uploading && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-400">
                <span className="flex items-center gap-1.5">
                  <Loader2 size={13} className="animate-spin" />
                  Uploading…
                </span>
                <span className="font-medium">{progress}%</span>
              </div>
              <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-zinc-100 dark:bg-white/5">
                <motion.div
                  animate={{ width: `${progress}%` }}
                  transition={{ ease: 'easeOut' }}
                  className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 grid gap-5 border-t border-zinc-100 pt-6 sm:grid-cols-2 dark:border-white/5">
        <Input
          id="profile-name"
          name="name"
          label="Full name"
          placeholder="Jane Cooper"
          value={values.name}
          onChange={handleChange}
        />
        <Input
          id="profile-email"
          name="email"
          type="email"
          label="Email address"
          placeholder="jane@company.com"
          value={values.email}
          onChange={handleChange}
        />
        <Input
          id="profile-company"
          name="company"
          label="Company"
          placeholder="Acme Inc."
          value={values.company}
          onChange={handleChange}
        />
        <Select
          id="profile-role"
          name="role"
          label="Role"
          value={values.role}
          onChange={handleChange}
        >
          <option value="">Select role</option>
          {ROLES.map((role) => (
            <option key={role} value={role}>
              {role}
            </option>
          ))}
        </Select>
      </div>

      <div className="mt-6">
        <Button type="submit" disabled={saving || uploading}>
          {saving || uploading ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              {uploading ? 'Uploading…' : 'Saving…'}
            </>
          ) : (
            <>
              <Image size={16} />
              Save changes
            </>
          )}
        </Button>
      </div>
    </motion.form>
  )
}

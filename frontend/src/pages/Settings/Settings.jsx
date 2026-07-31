export default function Settings() {
  return (
    <div className="mx-auto max-w-7xl p-6 sm:p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-white">Settings</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Manage your account and preferences
        </p>
      </div>

      <div className="max-w-xl space-y-6">
        <section className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6">
          <h2 className="font-medium text-white">Profile</h2>
          <p className="mt-1 text-sm text-zinc-500">
            Update your personal information.
          </p>
        </section>
        <section className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6">
          <h2 className="font-medium text-white">Preferences</h2>
          <p className="mt-1 text-sm text-zinc-500">
            Customize your experience.
          </p>
        </section>
      </div>
    </div>
  )
}

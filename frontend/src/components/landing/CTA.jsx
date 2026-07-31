import Button from '@/components/ui/Button'

export default function CTA() {
  return (
    <section id="cta" aria-label="Get started" className="bg-zinc-950 py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Content: final call-to-action panel */}
        <Button to="/register" size="lg">
          Get started free
        </Button>
      </div>
    </section>
  )
}

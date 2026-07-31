import SectionTitle from '@/components/ui/SectionTitle'

export default function Features() {
  return (
    <section id="features" className="bg-zinc-950 py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Features"
          title="Everything you need to win"
          description="Placeholder description for the features section."
          align="center"
        />
        {/* Content: feature grid */}
      </div>
    </section>
  )
}

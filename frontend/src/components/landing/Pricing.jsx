import SectionTitle from '@/components/ui/SectionTitle'

export default function Pricing() {
  return (
    <section id="pricing" className="bg-zinc-950 py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Pricing"
          title="Simple, transparent pricing"
          description="Placeholder description for the pricing section."
          align="center"
        />
        {/* Content: pricing tiers */}
      </div>
    </section>
  )
}

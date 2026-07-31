import SectionTitle from '@/components/ui/SectionTitle'

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-zinc-950 py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="How it works"
          title="From idea to strategy in three steps"
          description="Placeholder description for the process section."
          align="center"
        />
        {/* Content: step-by-step process */}
      </div>
    </section>
  )
}

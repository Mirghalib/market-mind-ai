import SectionTitle from '@/components/ui/SectionTitle'

export default function Testimonials() {
  return (
    <section id="testimonials" className="bg-zinc-950 py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="Testimonials"
          title="Loved by marketing teams"
          description="Placeholder description for the testimonials section."
          align="center"
        />
        {/* Content: customer quotes */}
      </div>
    </section>
  )
}

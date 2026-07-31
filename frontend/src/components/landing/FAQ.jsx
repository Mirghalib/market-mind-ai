import SectionTitle from '@/components/ui/SectionTitle'

export default function FAQ() {
  return (
    <section id="faq" className="bg-zinc-950 py-24">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <SectionTitle
          eyebrow="FAQ"
          title="Frequently asked questions"
          description="Placeholder description for the FAQ section."
          align="center"
        />
        {/* Content: accordion Q&A */}
      </div>
    </section>
  )
}

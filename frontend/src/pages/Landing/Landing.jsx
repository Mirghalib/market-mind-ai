import Navbar from '@/components/common/Navbar'
import Hero from '@/components/landing/Hero'
import TrustedBy from '@/components/landing/TrustedBy'
import Features from '@/components/landing/Features'
import HowItWorks from '@/components/landing/HowItWorks'
import Capabilities from '@/components/landing/Capabilities'
import Testimonials from '@/components/landing/Testimonials'
import Pricing from '@/components/landing/Pricing'
import FAQ from '@/components/landing/FAQ'
import CTA from '@/components/landing/CTA'
import Footer from '@/components/common/Footer'

export default function Landing() {
  return (
    <div className="flex min-h-screen flex-col bg-landing-bg text-landing-text">
      <Navbar />
      <main className="flex-1">
        <Hero />
        <TrustedBy />
        <Features />
        <HowItWorks />
        <Capabilities />
        <Testimonials />
        <Pricing />
        <FAQ />
        <CTA />
      </main>
      <Footer />
    </div>
  )
}

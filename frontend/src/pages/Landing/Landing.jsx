import Navbar from '@/components/common/Navbar'
import Footer from '@/components/common/Footer'
import Hero from '@/components/landing/Hero'

export default function Landing() {
  return (
    <div className="flex min-h-screen flex-col bg-zinc-950 text-zinc-100">
      <Navbar />
      <main className="flex-1">
        <Hero />
      </main>
      <Footer />
    </div>
  )
}

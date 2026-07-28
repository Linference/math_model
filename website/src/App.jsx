import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Features from './components/Features'
import Comparison from './components/Comparison'
import Workflow from './components/Workflow'
import Setup from './components/Setup'
import Download from './components/Download'
import Footer from './components/Footer'

export default function App() {
  return (
    <div className="min-h-screen bg-zinc-950">
      <Navbar />
      <Hero />
      <Features />
      <Comparison />
      <Workflow />
      <Setup />
      <Download />
      <Footer />
    </div>
  )
}

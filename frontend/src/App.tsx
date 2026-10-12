import { Routes, Route, Link } from 'react-router-dom'
import { Shield, List, UploadCloud } from 'lucide-react'
import UploadView from './views/UploadView'
import ResultView from './views/ResultView'
import CaseList from './views/CaseList'
import CyberBackground from './components/CyberBackground'

function App() {
  return (
    <div className="min-h-screen flex flex-col relative font-sans text-gray-100 selection:bg-cyan-900 selection:text-cyan-100">
      <CyberBackground />
      
      <header className="bg-gray-950/70 backdrop-blur-lg border-b border-cyan-900/40 p-4 sticky top-0 z-50 shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3 text-cyan-400 font-bold text-2xl tracking-tight">
            <Shield className="w-8 h-8 drop-shadow-[0_0_10px_rgba(34,211,238,0.5)]" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500 drop-shadow-sm">
              ThreatMatrix
            </span>
          </div>
          <nav className="flex gap-8">
            <Link to="/" className="flex items-center gap-2 text-gray-300 hover:text-cyan-400 hover:drop-shadow-[0_0_8px_rgba(34,211,238,0.8)] transition-all font-medium tracking-wide">
              <UploadCloud className="w-5 h-5" /> Analyze Email
            </Link>
            <Link to="/cases" className="flex items-center gap-2 text-gray-300 hover:text-cyan-400 hover:drop-shadow-[0_0_8px_rgba(34,211,238,0.8)] transition-all font-medium tracking-wide">
              <List className="w-5 h-5" /> Case History
            </Link>
          </nav>
        </div>
      </header>
      
      <main className="flex-1 max-w-6xl mx-auto w-full p-6 z-10 relative">
        <Routes>
          <Route path="/" element={<UploadView />} />
          <Route path="/cases" element={<CaseList />} />
          <Route path="/case/:id" element={<ResultView />} />
        </Routes>
      </main>
    </div>
  )
}

export default App

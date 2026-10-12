import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Loader2, Activity } from 'lucide-react'

export default function CaseList() {
  const [cases, setCases] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:8000/cases')
      .then(res => res.json())
      .then(data => {
        setCases(data)
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  return (
    <div className="bg-gray-900/70 backdrop-blur-xl border border-cyan-900/40 rounded-2xl shadow-[0_10px_40px_rgba(0,0,0,0.6)] overflow-hidden flex flex-col animate-in fade-in duration-700">
      <div className="p-6 border-b border-cyan-900/40 flex justify-between items-center bg-gray-950/40">
        <h2 className="text-xl font-bold tracking-wide flex items-center gap-3">
          <Activity className="w-6 h-6 text-cyan-400" />
          Intelligence Log
        </h2>
        <div className="relative">
          <Search className="w-4 h-4 absolute left-4 top-3 text-cyan-600" />
          <input type="text" placeholder="Search intercepted targets..." 
            className="bg-gray-950/60 border border-gray-700/80 text-sm font-medium rounded-xl pl-10 pr-4 py-2.5 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 w-72 shadow-inner placeholder-gray-600 transition-all"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-950/80 text-cyan-600/80 uppercase text-[10px] font-bold tracking-widest">
            <tr>
              <th className="px-6 py-5">Case ID</th>
              <th className="px-6 py-5">Filename</th>
              <th className="px-6 py-5">Sender Identity</th>
              <th className="px-6 py-5">Origin Node</th>
              <th className="px-6 py-5">Threat Score</th>
              <th className="px-6 py-5">Classification</th>
              <th className="px-6 py-5">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-cyan-500">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]" />
                </td>
              </tr>
            ) : cases.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-gray-500 font-medium tracking-wide">
                  No cases in database. Feed an email to the pipeline.
                </td>
              </tr>
            ) : cases.map((c) => (
              <tr key={c.id} className="hover:bg-cyan-900/20 transition-colors group">
                <td className="px-6 py-5 text-gray-500 font-mono">#{c.id.toString().padStart(4, '0')}</td>
                <td className="px-6 py-5 font-medium text-gray-200 group-hover:text-white transition-colors">{c.filename}</td>
                <td className="px-6 py-5 text-gray-400 truncate max-w-[200px] font-mono text-xs">{c.sender}</td>
                <td className="px-6 py-5 text-gray-400">{c.origin_country}</td>
                <td className="px-6 py-5">
                  <span className={`px-3 py-1.5 rounded-lg text-xs font-bold drop-shadow-sm border ${
                    c.fraud_score > 70 ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                    c.fraud_score > 30 ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30' :
                    'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  }`}>
                    {c.fraud_score.toFixed(1)}
                  </span>
                </td>
                <td className="px-6 py-5">
                  <span className="uppercase text-[10px] font-black tracking-widest text-cyan-600 bg-cyan-950/50 px-2 py-1 rounded border border-cyan-900/50">{c.ml_label}</span>
                </td>
                <td className="px-6 py-5">
                  <Link to={`/case/${c.id}`} className="text-cyan-400 hover:text-white font-bold text-xs tracking-wider uppercase border border-cyan-500/30 bg-cyan-500/10 hover:bg-cyan-500/20 px-4 py-2 rounded-lg transition-all shadow-[0_0_10px_rgba(34,211,238,0.1)] hover:shadow-[0_0_15px_rgba(34,211,238,0.3)]">
                    View intel
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

import { useEffect, useState } from 'react'
import { useParams, useLocation, Link } from 'react-router-dom'
import { AlertTriangle, ShieldCheck, MapPin, Tag, ArrowLeft, Info, Server, Fingerprint } from 'lucide-react'
import MapComponent from '../components/MapComponent'

export default function ResultView() {
  const { id } = useParams()
  const location = useLocation()
  const [data, setData] = useState<any>(location.state?.result || null)
  const [loading, setLoading] = useState(!data)

  useEffect(() => {
    if (!data) {
      fetch(`http://localhost:8000/cases/${id}`)
        .then(res => res.json())
        .then(json => {
          setData(json)
          setLoading(false)
        })
        .catch(err => {
          console.error(err)
          setLoading(false)
        })
    }
  }, [id, data])

  if (loading) return <div className="p-12 flex justify-center"><div className="animate-spin w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full"></div></div>
  if (!data) return <div className="p-12 text-center text-red-400 font-bold text-xl backdrop-blur-md bg-red-950/30 rounded-xl border border-red-500/30">Case not found.</div>

  const fraudScore = data.fraud_assessment?.fraud_score || 0
  const isHighRisk = fraudScore > 70
  const isMedRisk = fraudScore > 30 && !isHighRisk
  
  const scoreColor = isHighRisk ? 'text-red-500 drop-shadow-[0_0_10px_rgba(239,68,68,0.8)]' : isMedRisk ? 'text-yellow-400 drop-shadow-[0_0_10px_rgba(250,204,21,0.8)]' : 'text-emerald-400 drop-shadow-[0_0_10px_rgba(52,211,153,0.8)]'
  const strokeColor = isHighRisk ? 'stroke-red-500' : isMedRisk ? 'stroke-yellow-400' : 'stroke-emerald-400'
  const panelStyle = "bg-gray-900/60 backdrop-blur-xl border border-cyan-900/40 p-7 rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.5)] hover:border-cyan-500/40 transition-colors"

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
      <Link to="/cases" className="flex items-center gap-2 text-cyan-500 hover:text-cyan-300 hover:drop-shadow-[0_0_5px_rgba(34,211,238,0.8)] self-start font-semibold tracking-wide transition-all">
        <ArrowLeft className="w-5 h-5" /> Back to Intelligence Feed
      </Link>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Core Score Panel */}
        <div className={`${panelStyle} flex flex-col items-center justify-center relative overflow-hidden`}>
          {isHighRisk && <div className="absolute inset-0 bg-red-500/5 animate-pulse rounded-2xl pointer-events-none"></div>}
          <h2 className="text-gray-400 font-bold mb-6 tracking-widest uppercase text-xs flex items-center gap-2">
            <Fingerprint className="w-4 h-4 text-cyan-500" /> Threat Confidence
          </h2>
          <div className="relative flex items-center justify-center w-48 h-48 drop-shadow-xl">
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="96" cy="96" r="84" className="stroke-gray-800" strokeWidth="14" fill="none" />
              <circle cx="96" cy="96" r="84" className={`${strokeColor} transition-all duration-1000 ease-out`} strokeWidth="14" fill="none" 
                strokeDasharray={`${(fraudScore / 100) * 527} 527`} strokeLinecap="round" />
            </svg>
            <div className={`absolute text-6xl font-black tracking-tighter ${scoreColor}`}>{fraudScore}</div>
          </div>
          <div className="mt-6 text-center">
            <div className="text-xs text-gray-500 uppercase tracking-widest font-bold mb-1">AI Classification</div>
            <div className="bg-gray-950/50 border border-gray-800 rounded px-4 py-1.5 inline-block text-cyan-300 font-bold uppercase tracking-wide shadow-inner">
              {data.fraud_assessment?.ml_label} ({(data.fraud_assessment?.ml_confidence * 100).toFixed(1)}%)
            </div>
          </div>
        </div>

        {/* Metadata & Auth */}
        <div className={`${panelStyle} md:col-span-2 flex flex-col gap-6`}>
          <div>
            <h2 className="text-gray-400 font-bold tracking-widest uppercase text-xs mb-3 flex items-center gap-2">
              <Server className="w-4 h-4 text-cyan-500" /> Intercepted Metadata
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="bg-gray-950/60 p-4 rounded-xl border border-gray-800/80 shadow-inner">
                <span className="text-cyan-600/80 font-bold uppercase text-[10px] tracking-widest block mb-1">Sender Identifier</span>
                <span className="text-gray-100 font-mono text-sm truncate block">{data.sender}</span>
              </div>
              <div className="bg-gray-950/60 p-4 rounded-xl border border-gray-800/80 shadow-inner">
                <span className="text-cyan-600/80 font-bold uppercase text-[10px] tracking-widest block mb-1">Subject Vector</span>
                <span className="text-gray-100 font-medium text-sm truncate block">{data.subject}</span>
              </div>
            </div>
          </div>

          <div className="mt-auto">
            <h2 className="text-gray-400 font-bold tracking-widest uppercase text-xs mb-3 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-cyan-500" /> Cryptographic Signatures
            </h2>
            <div className="flex flex-wrap gap-4">
              <Badge label="SPF" result={data.security_analysis?.spf_result} />
              <Badge label="DKIM" result={data.security_analysis?.dkim_result} />
              <Badge label="DMARC" result={data.security_analysis?.dmarc_result} />
              <Badge label="Alignment" result={data.security_analysis?.alignment_pass ? 'pass' : 'fail'} />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Anomalies */}
        <div className={panelStyle}>
           <h2 className="text-gray-400 font-bold tracking-widest uppercase text-xs mb-5 flex items-center gap-2">
             <AlertTriangle className="w-4 h-4 text-yellow-500" /> Behavioral Anomalies
           </h2>
           {data.security_analysis?.anomaly_flags?.length > 0 ? (
             <ul className="flex flex-col gap-3">
               {data.security_analysis.anomaly_flags.map((flag: string, i: number) => (
                 <li key={i} className="flex items-start gap-3 bg-gradient-to-r from-red-950/60 to-gray-900/60 border border-red-500/30 p-4 rounded-xl text-red-200 text-sm font-medium leading-relaxed shadow-[0_0_15px_rgba(239,68,68,0.05)] hover:border-red-500/60 transition-colors">
                   <Tag className="w-5 h-5 mt-0.5 text-red-500 shrink-0 drop-shadow-[0_0_5px_rgba(239,68,68,0.8)]" />
                   <span>{flag}</span>
                 </li>
               ))}
             </ul>
           ) : (
             <div className="flex items-center gap-3 text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 p-5 rounded-xl font-medium tracking-wide">
               <ShieldCheck className="w-6 h-6" /> Infrastructure appears fully legitimate.
             </div>
           )}
        </div>

        {/* Geolocation Map */}
        <div className={`${panelStyle} flex flex-col p-0 overflow-hidden`}>
          <div className="p-6 pb-4">
            <h2 className="text-gray-400 font-bold tracking-widest uppercase text-xs mb-4 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-blue-400" /> Origin Network Trace
            </h2>
            <div className="bg-gray-950/60 p-4 rounded-xl border border-gray-800/80 flex flex-wrap gap-x-8 gap-y-3 text-sm shadow-inner">
              <div><span className="text-cyan-600/80 font-bold uppercase text-[10px] tracking-widest block mb-1">Origin IP</span> <span className="font-mono text-cyan-100">{data.geo_assessment?.origin_ip || 'N/A'}</span></div>
              <div><span className="text-cyan-600/80 font-bold uppercase text-[10px] tracking-widest block mb-1">Location</span> <span className="text-gray-200">{data.geo_assessment?.city}, {data.geo_assessment?.country}</span></div>
              <div><span className="text-cyan-600/80 font-bold uppercase text-[10px] tracking-widest block mb-1">Provider</span> <span className="text-gray-200">{data.geo_assessment?.isp}</span></div>
            </div>
          </div>
          
          <div className="flex-1 bg-gray-950 relative min-h-[300px] border-t border-gray-800">
            {data.geo_assessment?.lat ? (
              <div className="absolute inset-0 saturate-[0.8] contrast-[1.2] hue-rotate-[180deg] invert-[0.9]">
                <MapComponent lat={data.geo_assessment.lat} lon={data.geo_assessment.lon} />
              </div>
            ) : (
               <div className="absolute inset-0 flex items-center justify-center text-gray-500 font-mono text-sm tracking-widest uppercase">
                 <Info className="w-5 h-5 mr-3 text-gray-600" /> Coordinates Unavailable
               </div>
            )}
            {/* Overlay to give map a cyber tint */}
            <div className="absolute inset-0 bg-blue-900/10 pointer-events-none mix-blend-screen shadow-[inset_0_0_40px_rgba(0,0,0,0.8)]"></div>
          </div>
        </div>
      </div>
    </div>
  )
}

function Badge({ label, result }: { label: string, result: string }) {
  const isPass = result?.includes('pass')
  const color = isPass 
    ? 'bg-emerald-950/40 text-emerald-400 border-emerald-500/40 shadow-[0_0_10px_rgba(52,211,153,0.1)]' 
    : 'bg-red-950/40 text-red-400 border-red-500/40 shadow-[0_0_10px_rgba(239,68,68,0.1)]'
  return (
    <div className={`px-5 py-2.5 rounded-xl border flex flex-col items-center flex-1 min-w-[90px] ${color}`}>
      <span className="text-[10px] font-bold tracking-widest uppercase opacity-80 mb-1">{label}</span>
      <span className="font-bold text-sm tracking-wide">{result || 'none'}</span>
    </div>
  )
}

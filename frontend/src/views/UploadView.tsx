import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, AlertCircle, Loader2 } from 'lucide-react'

export default function UploadView() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.eml')) {
      setError("Please upload a valid .eml file")
      return
    }

    setLoading(true)
    setError(null)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData
      })
      if (!res.ok) throw new Error("Analysis failed. Is the FastAPI backend running on port 8000?")
      const data = await res.json()
      navigate(`/case/${data.case_id}`, { state: { result: data } })
    } catch (err: any) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center h-[75vh] animate-in fade-in duration-700">
      <div className="text-center mb-10">
        <h1 className="text-5xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-cyan-200 via-white to-sky-300 drop-shadow-[0_4px_20px_rgba(0,0,0,0.9)]">
          Forensic Email Ingestion
        </h1>
        <p className="text-cyan-100/90 text-lg tracking-wide font-medium drop-shadow-[0_2px_10px_rgba(0,0,0,0.85)]">
          Drop a raw .eml file into the analysis matrix
        </p>
      </div>

      <div 
        className={`w-full max-w-xl p-14 border-2 border-dashed rounded-3xl flex flex-col items-center justify-center transition-all duration-300 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.7)]
          ${loading 
            ? 'border-cyan-400 bg-cyan-950/70 shadow-[0_0_50px_rgba(34,211,238,0.3)]' 
            : 'border-cyan-500/30 bg-gray-950/75 hover:border-cyan-400 hover:bg-gray-900/80 hover:shadow-[0_0_40px_rgba(34,211,238,0.25)]'}`}
      >
        {loading ? (
          <div className="flex flex-col items-center text-cyan-400">
            <Loader2 className="w-16 h-16 animate-spin mb-6 drop-shadow-[0_0_10px_rgba(34,211,238,0.8)]" />
            <span className="font-bold tracking-widest uppercase text-lg animate-pulse">Running Neural Pipeline...</span>
          </div>
        ) : (
          <>
            <Upload className="w-16 h-16 text-cyan-500/60 mb-6 group-hover:text-cyan-400 transition-colors" />
            <label className="cursor-pointer bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white px-8 py-3 rounded-lg font-bold tracking-wide transition-all shadow-[0_0_20px_rgba(8,145,178,0.4)] hover:shadow-[0_0_30px_rgba(34,211,238,0.6)] hover:-translate-y-1">
              Select .eml File
              <input type="file" className="hidden" accept=".eml" onChange={(e) => {
                if (e.target.files?.[0]) handleFile(e.target.files[0])
              }} />
            </label>
            <p className="mt-6 text-sm text-gray-400 font-medium tracking-wider">OR DRAG AND DROP HERE</p>
          </>
        )}
      </div>
      
      {error && (
        <div className="mt-8 flex items-center gap-3 text-red-300 bg-red-950/80 border border-red-500/50 backdrop-blur-md px-6 py-4 rounded-xl shadow-[0_0_20px_rgba(239,68,68,0.2)]">
          <AlertCircle className="w-6 h-6 shrink-0" />
          <span className="font-medium tracking-wide">{error}</span>
        </div>
      )}
    </div>
  )
}

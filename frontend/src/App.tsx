import {
  AlertCircle,
  BarChart3,
  Camera,
  CheckCircle2,
  ImageIcon,
  LoaderCircle,
  RefreshCcw,
  Server,
  StopCircle,
  Upload,
  WifiOff,
} from 'lucide-react'
import { type ChangeEvent, type DragEvent, useCallback, useEffect, useMemo, useRef, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type PredictionResponse = {
  prediction: string
  confidence: number
  rotten_percentage: number
  other_similarities: Record<string, number>
}

type ApiHealthResponse = {
  status: string
  model_loaded: boolean
}

type Status = 'idle' | 'loading' | 'success' | 'error'
type ApiStatus = 'checking' | 'online' | 'offline'
type Mode = 'upload' | 'camera'

function formatClassName(value: string) {
  return value
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/fresh/gi, 'Fresh ')
    .replace(/rotten/gi, 'Rotten ')
    .replace(/\s+/g, ' ')
    .trim()
}

function formatPercent(value: number) {
  return `${value.toFixed(2)}%`
}

function confidenceToPercent(value: number) {
  return value <= 1 ? value * 100 : value
}

function App() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const trackerCanvasRef = useRef<HTMLCanvasElement | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const frameIntervalRef = useRef<number | null>(null)
  const trackerIntervalRef = useRef<number | null>(null)

  const [mode, setMode] = useState<Mode>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [status, setStatus] = useState<Status>('idle')
  const [result, setResult] = useState<PredictionResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [apiStatus, setApiStatus] = useState<ApiStatus>('checking')
  const [apiHealth, setApiHealth] = useState<ApiHealthResponse | null>(null)
  const [isCameraActive, setIsCameraActive] = useState(false)

  // Tracking State
  const [roiPos, setRoiPos] = useState({ x: 0.5, y: 0.5 })
  const currentPosRef = useRef({ x: 0.5, y: 0.5 })
  const targetPosRef = useRef({ x: 0.5, y: 0.5 })

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file])

  const wsUrl = useMemo(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    if (API_BASE_URL.startsWith('http')) {
      const url = new URL(API_BASE_URL)
      const wsProtocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
      return `${wsProtocol}//${url.host}/ws/predict`
    }
    return `${protocol}//${window.location.host}${API_BASE_URL}/ws/predict`
  }, [])

  const sortedSimilarities = useMemo(() => {
    if (!result) return []
    return Object.entries(result.other_similarities)
      .sort(([, first], [, second]) => second - first)
      .slice(0, 6)
  }, [result])

  useEffect(() => {
    return () => { if (previewUrl) URL.revokeObjectURL(previewUrl) }
  }, [previewUrl])

  useEffect(() => { void checkApiHealth() }, [])

  useEffect(() => { return () => stopCamera() }, [])

  async function checkApiHealth() {
    setApiStatus('checking')
    try {
      const response = await fetch(`${API_BASE_URL}/`)
      if (!response.ok) throw new Error(`API status ${response.status}`)
      const data = (await response.json()) as ApiHealthResponse
      setApiHealth(data)
      setApiStatus('online')
    } catch {
      setApiHealth(null)
      setApiStatus('offline')
    }
  }

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      })
      if (videoRef.current) videoRef.current.srcObject = stream
      streamRef.current = stream
      setIsCameraActive(true)
      setStatus('loading')
      setErrorMessage('')
      setResult(null)

      const ws = new WebSocket(wsUrl)
      ws.binaryType = 'arraybuffer'
      ws.onopen = () => {
        console.log('WebSocket Connected')
        setStatus('success')
        frameIntervalRef.current = window.setInterval(sendFrame, 150)
        trackerIntervalRef.current = window.setInterval(updateTracker, 40)
      }
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data) as PredictionResponse
        setResult(data)
      }
      ws.onerror = () => {
        setErrorMessage('Kesalahan koneksi WebSocket.')
        setStatus('error')
        stopCamera()
      }
      wsRef.current = ws
    } catch (err) {
      setErrorMessage('Gagal mengakses kamera.')
      setStatus('error')
    }
  }

  const stopCamera = () => {
    if (frameIntervalRef.current) clearInterval(frameIntervalRef.current)
    if (trackerIntervalRef.current) clearInterval(trackerIntervalRef.current)
    if (wsRef.current) wsRef.current.close()
    if (streamRef.current) streamRef.current.getTracks().forEach((track) => track.stop())
    setIsCameraActive(false)
  }

  // LOGIKA SMART TRACKER (WEB): Menghindari warna kulit, mencari warna buah
  const updateTracker = useCallback(() => {
    if (!videoRef.current) return
    if (!trackerCanvasRef.current) trackerCanvasRef.current = document.createElement('canvas')

    const video = videoRef.current
    const canvas = trackerCanvasRef.current
    const ctx = canvas.getContext('2d', { willReadFrequently: true })

    if (ctx && video.videoWidth > 0) {
      const sw = 50, sh = 50
      canvas.width = sw
      canvas.height = sh
      ctx.drawImage(video, 0, 0, sw, sh)

      const imageData = ctx.getImageData(0, 0, sw, sh)
      const data = imageData.data
      let sumX = 0, sumY = 0, count = 0

      for (let y = 0; y < sh; y++) {
        for (let x = 0; x < sw; x++) {
          const i = (y * sw + x) * 4
          const r = data[i], g = data[i+1], b = data[i+2]
          
          // 1. Deteksi Warna Kulit (Skin Tone Filter)
          const isSkin = r > 95 && g > 40 && b > 20 && 
                         (Math.max(r, g, b) - Math.min(r, g, b) > 15) && 
                         Math.abs(r - g) > 15 && r > g && r > b

          // 2. Deteksi Warna Buah (Fruit Priority)
          const max = Math.max(r, g, b)
          const min = Math.min(r, g, b)
          const saturation = (max - min) / (max + 1)
          
          if (!isSkin && saturation > 0.3 && max > 50) {
            sumX += x
            sumY += y
            count++
          }
        }
      }

      if (count > 10) {
        targetPosRef.current = { x: sumX / count / sw, y: sumY / count / sh }
      } else {
        // Kembali ke tengah jika tidak ada target
        targetPosRef.current = { x: 0.5, y: 0.5 }
      }

      // Smoothing Movement
      currentPosRef.current.x += (targetPosRef.current.x - currentPosRef.current.x) * 0.12
      currentPosRef.current.y += (targetPosRef.current.y - currentPosRef.current.y) * 0.12
      setRoiPos({ x: currentPosRef.current.x, y: currentPosRef.current.y })
    }
  }, [])

  const sendFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const context = canvas.getContext('2d', { alpha: false })

    if (context && video.videoWidth > 0) {
      const { x: rx, y: ry } = currentPosRef.current
      const size = Math.min(video.videoWidth, video.videoHeight) * 0.55
      let cx = rx * video.videoWidth - size / 2
      let cy = ry * video.videoHeight - size / 2
      cx = Math.max(0, Math.min(video.videoWidth - size, cx))
      cy = Math.max(0, Math.min(video.videoHeight - size, cy))

      canvas.width = 224
      canvas.height = 224
      context.imageSmoothingEnabled = true
      context.drawImage(video, cx, cy, size, size, 0, 0, 224, 224)

      canvas.toBlob((blob) => {
        if (blob && wsRef.current?.readyState === WebSocket.OPEN) {
          blob.arrayBuffer().then((buffer) => wsRef.current?.send(buffer))
        }
      }, 'image/jpeg', 0.8)
    }
  }, [])

  function selectFile(nextFile: File | null) {
    if (!nextFile || !nextFile.type.startsWith('image/')) return
    setFile(nextFile)
    setResult(null)
    setErrorMessage('')
    setStatus('idle')
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    selectFile(event.target.files?.[0] ?? null)
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault()
    setIsDragging(false)
    selectFile(event.dataTransfer.files?.[0] ?? null)
  }

  async function handleSubmit() {
    if (!file) return
    setStatus('loading')
    setResult(null)
    const formData = new FormData()
    formData.append('file', file)
    try {
      const response = await fetch(`${API_BASE_URL}/predict`, { method: 'POST', body: formData })
      const data = (await response.json()) as PredictionResponse
      setResult(data)
      setStatus('success')
    } catch { setStatus('error') }
  }

  function resetUpload() {
    setFile(null); setResult(null); setStatus('idle')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const confidencePercent = result ? confidenceToPercent(result.confidence) : 0
  const isFresh = result ? result.rotten_percentage < 50 : false

  return (
    <main className="min-h-screen bg-[#f7f8f5] text-slate-950 font-sans">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-4 py-6 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-bold text-emerald-700 uppercase tracking-wider">AI Vision System</p>
            <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
              Klasifikasi Kesegaran Buah
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
              Deteksi otomatis jenis dan tingkat kebusukan buah menggunakan <strong>MobileNetV2 + Smart Tracker</strong>.
            </p>
          </div>
          <div className="flex flex-col gap-2 sm:items-end">
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-1.5 text-xs font-semibold text-slate-600 shadow-sm">
              <span className={['h-2 w-2 rounded-full', apiStatus === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'].join(' ')} />
              {API_BASE_URL}
            </div>
          </div>
        </header>

        <nav className="mt-6 flex gap-2">
          <button onClick={() => { setMode('upload'); stopCamera() }} className={['px-5 py-2.5 rounded-full text-sm font-bold transition-all flex items-center gap-2', mode === 'upload' ? 'bg-slate-900 text-white shadow-lg' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'].join(' ')}>
            <Upload size={18} /> Unggah File
          </button>
          <button onClick={() => { setMode('camera'); resetUpload() }} className={['px-5 py-2.5 rounded-full text-sm font-bold transition-all flex items-center gap-2', mode === 'camera' ? 'bg-emerald-600 text-white shadow-lg' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'].join(' ')}>
            <Camera size={18} /> Kamera Real-time
          </button>
        </nav>

        <section className="grid flex-1 gap-6 py-6 lg:grid-cols-[1fr_400px]">
          <div className="flex flex-col gap-4">
            {mode === 'upload' ? (
              <label className={['flex min-h-[450px] cursor-pointer flex-col items-center justify-center rounded-2xl border-4 border-dashed bg-white p-6 text-center transition-all', isDragging ? 'border-emerald-500 bg-emerald-50' : 'border-slate-200 hover:border-emerald-400'].join(' ')} onDragEnter={() => setIsDragging(true)} onDragOver={(e) => e.preventDefault()} onDragLeave={() => setIsDragging(false)} onDrop={handleDrop}>
                <input ref={fileInputRef} className="hidden" type="file" accept="image/*" onChange={handleFileChange} />
                {previewUrl ? <img className="max-h-[400px] w-full rounded-xl object-contain shadow-md" src={previewUrl} /> : <div className="flex flex-col items-center text-slate-400"><ImageIcon size={64} className="mb-4 opacity-20" /> <p className="text-lg font-bold text-slate-900">Letakkan gambar di sini</p> <p className="text-sm">Klik atau tarik file JPG/PNG</p></div>}
              </label>
            ) : (
              <div className="relative min-h-[450px] overflow-hidden rounded-2xl border-4 border-slate-900 bg-slate-950 shadow-2xl group">
                <video ref={videoRef} autoPlay playsInline muted className={['absolute inset-0 h-full w-full object-cover transition-opacity duration-500', isCameraActive ? 'opacity-100' : 'opacity-0'].join(' ')} />
                <canvas ref={canvasRef} className="hidden" />
                
                {isCameraActive && (
                  <>
                    <div className="pointer-events-none absolute h-[220px] w-[220px] -translate-x-1/2 -translate-y-1/2 rounded-3xl border-4 border-emerald-400 transition-[top,left] duration-150 ease-out shadow-[0_0_0_9999px_rgba(0,0,0,0.6)]" style={{ left: `${roiPos.x * 100}%`, top: `${roiPos.y * 100}%` }}>
                      <div className="absolute -top-10 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full bg-emerald-500 px-4 py-1 text-[11px] font-black text-white shadow-xl flex items-center gap-2">
                        <RefreshCcw size={12} className="animate-spin" /> SMART TRACKER ACTIVE
                      </div>
                      <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap text-emerald-400 text-[10px] font-bold tracking-widest uppercase">Targeting Object...</div>
                    </div>
                    <div className="absolute top-6 right-6 flex items-center gap-3 rounded-full bg-red-600/90 px-4 py-1.5 text-[10px] font-black tracking-tighter text-white uppercase backdrop-blur-sm">
                      <span className="h-2 w-2 animate-ping rounded-full bg-white" /> Live Stream
                    </div>
                  </>
                )}

                {!isCameraActive && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center text-white">
                    <div className="mb-6 rounded-full bg-emerald-500/10 p-6 text-emerald-400"><Camera size={48} /></div>
                    <h3 className="text-xl font-black mb-2">Kamera Belum Aktif</h3>
                    <p className="text-slate-400 text-sm max-w-xs">Aktifkan kamera untuk menggunakan fitur tracking otomatis yang mengabaikan wajah.</p>
                  </div>
                )}
              </div>
            )}

            <div className="flex gap-3">
              {mode === 'camera' ? (
                !isCameraActive ? (
                  <button onClick={startCamera} className="flex-1 h-14 rounded-xl bg-emerald-600 text-white font-black text-lg shadow-lg hover:bg-emerald-700 transition-all flex items-center justify-center gap-3">
                    <Camera size={24} /> MULAI SCANNING
                  </button>
                ) : (
                  <button onClick={stopCamera} className="flex-1 h-14 rounded-xl bg-red-600 text-white font-black text-lg shadow-lg hover:bg-red-700 transition-all flex items-center justify-center gap-3">
                    <StopCircle size={24} /> BERHENTI
                  </button>
                )
              ) : (
                <button disabled={status === 'loading' || !file} onClick={handleSubmit} className="flex-1 h-14 rounded-xl bg-slate-900 text-white font-black text-lg shadow-lg hover:bg-slate-800 disabled:bg-slate-200 transition-all flex items-center justify-center gap-3">
                  {status === 'loading' ? <LoaderCircle className="animate-spin" /> : <CheckCircle2 />} PROSES KLASIFIKASI
                </button>
              )}
            </div>
          </div>

          <aside className="flex flex-col gap-5">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xl relative overflow-hidden">
               <div className={['absolute top-0 left-0 w-1 h-full', isFresh ? 'bg-emerald-500' : result ? 'bg-red-500' : 'bg-slate-200'].join(' ')} />
              <h2 className="text-xl font-black text-slate-900 mb-6 flex items-center justify-between">
                Hasil Analisis {status === 'success' && <CheckCircle2 className="text-emerald-500" />}
              </h2>
              {result ? (
                <div className="space-y-6">
                  <div>
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1 block">Hasil Deteksi</label>
                    <p className="text-3xl font-black text-slate-900 tracking-tight leading-none">{formatClassName(result.prediction)}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="rounded-2xl bg-emerald-50 p-4 border border-emerald-100">
                      <span className="text-[10px] font-bold text-emerald-700 uppercase">Akurasi</span>
                      <p className="text-2xl font-black text-emerald-900">{formatPercent(confidencePercent)}</p>
                    </div>
                    <div className="rounded-2xl bg-red-50 p-4 border border-red-100">
                      <span className="text-[10px] font-bold text-red-700 uppercase">Kebusukan</span>
                      <p className="text-2xl font-black text-red-900">{formatPercent(result.rotten_percentage)}</p>
                    </div>
                  </div>
                  <div className={['p-4 rounded-xl text-sm font-bold flex items-center gap-3 border', isFresh ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'].join(' ')}>
                    {isFresh ? 'Kondisi Buah Segar ✓' : 'Kondisi Buah Busuk ✗'}
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-slate-300">
                   <BarChart3 size={48} className="mx-auto mb-4 opacity-10" />
                   <p className="text-sm font-bold">Menunggu data masuk...</p>
                </div>
              )}
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
              <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest mb-6">Distribusi Probabilitas</h3>
              <div className="space-y-4">
                {sortedSimilarities.length > 0 ? sortedSimilarities.map(([label, val]) => (
                  <div key={label}>
                    <div className="flex justify-between text-xs font-bold mb-1.5">
                      <span className="text-slate-700">{formatClassName(label)}</span>
                      <span className="text-slate-400">{formatPercent(val)}</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full transition-all duration-500" style={{ width: `${val}%` }} />
                    </div>
                  </div>
                )) : [1,2,3].map(i => <div key={i} className="h-4 bg-slate-50 rounded animate-pulse" />)}
              </div>
            </div>
          </aside>
        </section>
      </div>
    </main>
  )
}

export default App

'use client'

import { useState, useCallback } from 'react'
import {
  AlertCircle,
  CheckCircle,
  Download,
  FileArchive,
  FileAudio,
  Loader2,
  Music,
  RotateCcw,
  Upload,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'

type AppState = 'upload' | 'ready' | 'processing' | 'complete' | 'error'

const SUPPORTED_FORMATS = ['.wav', '.mp3', '.aiff', '.m4a', '.flac', '.ogg']
const STEMS = ['Drums', 'Bass', 'Vocals', 'Other']
const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB

export default function AudioSplitter() {
  const [state, setState] = useState<AppState>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string>('')
  const [downloadUrl, setDownloadUrl] = useState<string>('')
  const [isDragOver, setIsDragOver] = useState(false)

  const validateFile = (file: File): string | null => {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!SUPPORTED_FORMATS.includes(extension)) {
      return `Unsupported format. Please use: ${SUPPORTED_FORMATS.join(', ')}`
    }
    if (file.size > MAX_FILE_SIZE) {
      return 'File too large. Maximum size is 100MB.'
    }
    return null
  }

  const handleFileSelect = useCallback((selectedFile: File) => {
    const validationError = validateFile(selectedFile)
    if (validationError) {
      setError(validationError)
      setState('error')
      return
    }

    setFile(selectedFile)
    setError('')
    setState('ready')
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }, [handleFileSelect])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }, [handleFileSelect])

  const processAudio = async () => {
    if (!file) return

    setState('processing')

    try {
      console.log('Starting audio separation with backend...')

      const formData = new FormData()
      formData.append('file', file)

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      console.log('Calling API at:', apiUrl)

      const response = await fetch(`${apiUrl}/separate`, {
        method: 'POST',
        body: formData,
        headers: {},
      })

      if (!response.ok) {
        let errorMessage = 'Processing failed'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch {
          errorMessage = `Server error: ${response.status} ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)

      setDownloadUrl(url)
      setState('complete')

      console.log('Audio separation complete.')
    } catch (err) {
      console.error('Separation failed:', err)

      let errorMessage = 'Processing failed'
      if (err instanceof Error) {
        if (err.message.includes('Failed to fetch')) {
          errorMessage = 'Cannot connect to server. Make sure your backend is running on http://localhost:8000'
        } else {
          errorMessage = err.message
        }
      }

      setError(errorMessage)
      setState('error')
    }
  }

  const reset = () => {
    setState('upload')
    setFile(null)
    setError('')
    if (downloadUrl) {
      URL.revokeObjectURL(downloadUrl)
      setDownloadUrl('')
    }
  }

  const downloadFile = () => {
    if (downloadUrl && file) {
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `${file.name.split('.')[0]}_separated.zip`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  }

  const fileSize = file ? `${(file.size / 1024 / 1024).toFixed(1)} MB` : null

  return (
    <main className="min-h-screen bg-[#f7f8f3] text-zinc-950">
      <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 py-5 sm:px-6 lg:px-8">
        <header className="grid gap-5 border-b border-zinc-200 pb-5 sm:grid-cols-[1fr_auto] sm:items-end">
          <div>
            <h1 className="text-3xl font-semibold text-zinc-950 sm:text-4xl">
              Stem Splitter
            </h1>
            <p className="mt-2 max-w-xl text-sm leading-6 text-zinc-600 sm:text-base">
              Upload one track and get clean drums, bass, vocals, and other stems back as a zip.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-2 text-sm sm:w-64">
            <div className="rounded-md border border-zinc-200 bg-white p-3 shadow-sm">
              <p className="text-xs font-medium uppercase text-zinc-500">Max file</p>
              <p className="mt-1 font-semibold text-zinc-900">100MB</p>
            </div>
            <div className="rounded-md border border-zinc-200 bg-white p-3 shadow-sm">
              <p className="text-xs font-medium uppercase text-zinc-500">Output</p>
              <p className="mt-1 font-semibold text-zinc-900">4 stems</p>
            </div>
          </div>
        </header>

        <section className="grid items-start gap-5 py-5 lg:grid-cols-[minmax(0,1fr)_18rem]">
          <Card className="h-fit rounded-lg border-zinc-200 bg-white shadow-sm">
            <CardHeader className="border-b border-zinc-100 text-left">
              <CardTitle className="text-xl text-zinc-950">
                {state === 'upload' && 'Upload audio'}
                {state === 'ready' && 'Ready to process'}
                {state === 'processing' && 'Processing audio'}
                {state === 'complete' && 'Ready to download'}
                {state === 'error' && 'Processing failed'}
              </CardTitle>
              <CardDescription className="text-zinc-500">
                {state === 'upload' && 'Choose an audio file to split into individual tracks.'}
                {state === 'ready' && 'Start separation or choose a different track.'}
                {state === 'processing' && 'The backend is separating your file. Large tracks can take a few minutes.'}
                {state === 'complete' && 'Your separated stems are packaged in a zip file.'}
                {state === 'error' && 'Check the message below and try again.'}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-5 pt-6">
              {state === 'upload' && (
                <>
                  <div
                    className={`rounded-lg border border-dashed p-8 text-center transition-colors ${
                      isDragOver
                        ? 'border-teal-500 bg-teal-50'
                        : 'border-zinc-300 bg-zinc-50/70 hover:border-teal-500 hover:bg-white'
                    }`}
                    onDrop={handleDrop}
                    onDragOver={(e) => {
                      e.preventDefault()
                      setIsDragOver(true)
                    }}
                    onDragLeave={() => setIsDragOver(false)}
                  >
                    <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-lg bg-white text-teal-700 shadow-sm ring-1 ring-zinc-200">
                      <Upload className="h-6 w-6" />
                    </div>
                    <p className="text-base font-medium text-zinc-900">
                      Drop your audio file here
                    </p>
                    <p className="mt-1 text-sm text-zinc-500">
                      or browse from your computer
                    </p>
                    <Button variant="outline" asChild className="mt-5 cursor-pointer">
                      <label>
                        Browse files
                        <input
                          type="file"
                          className="hidden"
                          accept={SUPPORTED_FORMATS.join(',')}
                          onChange={handleFileInput}
                        />
                      </label>
                    </Button>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-medium text-zinc-600">Formats</span>
                    {SUPPORTED_FORMATS.map((format) => (
                      <Badge key={format} variant="outline" className="border-zinc-200 bg-white text-zinc-600">
                        {format.toUpperCase()}
                      </Badge>
                    ))}
                  </div>

                </>
              )}

              {state === 'ready' && file && (
                <div className="space-y-4">
                  <div className="rounded-lg border border-zinc-200 bg-white">
                    <div className="flex items-center gap-3 p-4">
                      <div className="flex h-11 w-11 items-center justify-center rounded-md bg-teal-50 text-teal-700">
                        <FileAudio className="h-5 w-5" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate font-medium text-zinc-950">{file.name}</p>
                        <p className="text-sm text-zinc-500">{fileSize}</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
                    <Button
                      onClick={processAudio}
                      className="bg-teal-700 text-white hover:bg-teal-800"
                    >
                      <Music className="h-4 w-4" />
                      Start separation
                    </Button>
                    <Button
                      onClick={reset}
                      variant="outline"
                    >
                      <RotateCcw className="h-4 w-4" />
                      Choose different file
                    </Button>
                  </div>
                </div>
              )}

              {state === 'processing' && (
                <div className="space-y-6 py-4 text-center" role="status" aria-live="polite">
                  <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-lg bg-teal-50 text-teal-700 ring-1 ring-teal-100">
                    <Loader2 className="h-10 w-10 animate-spin" />
                  </div>
                  <div>
                    <p className="text-lg font-medium text-zinc-950">
                      Separating stems
                    </p>
                    <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-zinc-500">
                      Keep this tab open while Demucs splits the track into drums, bass, vocals, and other.
                    </p>
                  </div>
                  <div className="mx-auto grid max-w-sm grid-cols-4 gap-2">
                    {STEMS.map((stem) => (
                      <div key={stem} className="rounded-md border border-zinc-200 bg-zinc-50 px-2 py-2 text-xs font-medium text-zinc-600">
                        {stem}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {state === 'complete' && (
                <div className="space-y-6 py-2 text-center">
                  <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100">
                    <CheckCircle className="h-8 w-8" />
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-zinc-950">Separation complete</h3>
                    <p className="mt-2 text-sm text-zinc-500">
                      Download the zip file to get each stem as its own audio track.
                    </p>
                  </div>

                  <div className="flex flex-wrap justify-center gap-2">
                    {STEMS.map((stem) => (
                      <Badge key={stem} variant="outline" className="border-emerald-200 bg-emerald-50 text-emerald-700">
                        {stem}
                      </Badge>
                    ))}
                  </div>

                  <div className="space-y-3">
                    <Button
                      onClick={downloadFile}
                      size="lg"
                      className="w-full bg-zinc-950 text-white hover:bg-zinc-800"
                    >
                      <Download className="h-4 w-4" />
                      Download separated tracks
                    </Button>
                    <Button
                      onClick={reset}
                      variant="outline"
                      className="w-full"
                    >
                      <RotateCcw className="h-4 w-4" />
                      Process another file
                    </Button>
                  </div>
                </div>
              )}

              {state === 'error' && (
                <div className="space-y-4">
                  <Alert className="border-red-200 bg-red-50 text-red-900">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription>
                      {error}
                    </AlertDescription>
                  </Alert>
                  <Button
                    onClick={reset}
                    variant="outline"
                    className="w-full"
                  >
                    Try again
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          <aside className="space-y-4">
            <div className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm">
              <div className="flex items-center gap-2 text-sm font-semibold text-zinc-900">
                <FileArchive className="h-4 w-4 text-teal-700" />
                Stem package
              </div>
              <div className="mt-4 space-y-2">
                {STEMS.map((stem) => (
                  <div key={stem} className="flex items-center justify-between rounded-md bg-zinc-50 px-3 py-2 text-sm">
                    <span className="font-medium text-zinc-700">{stem}</span>
                    <span className="text-xs text-zinc-500">.wav</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-zinc-200 bg-white p-4 text-sm leading-6 text-zinc-600 shadow-sm">
              Files stay local to this app session. When processing finishes, the browser downloads the separated archive directly from the backend.
            </div>
          </aside>
        </section>
      </div>
    </main>
  )
}

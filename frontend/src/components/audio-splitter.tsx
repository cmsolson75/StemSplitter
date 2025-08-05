'use client'

import { useState, useCallback } from 'react'
import { Upload, Music, Download, AlertCircle, FileAudio, Loader2, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'

type AppState = 'upload' | 'processing' | 'complete' | 'error'

const SUPPORTED_FORMATS = ['.wav', '.mp3', '.aiff', '.m4a', '.flac', '.ogg']
const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB

export default function AudioSplitter() {
  const [state, setState] = useState<AppState>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string>('')
  const [progress, setProgress] = useState(0)
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
    setState('upload')
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
    setProgress(0)

    try {
      console.log('🎵 Starting audio separation with backend...')
      
      // Create FormData for multipart upload
      const formData = new FormData()
      formData.append('file', file)

      // Simple spinner - no progress tracking needed for real processing
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      console.log('Calling API at:', apiUrl)
      
      const response = await fetch(`${apiUrl}/separate`, {
        method: 'POST',
        body: formData,
        // Add headers for CORS if needed
        headers: {
          // Don't set Content-Type - let browser set it with boundary for multipart
        },
      })

      if (!response.ok) {
        // Handle API errors
        let errorMessage = 'Processing failed'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch {
          errorMessage = `Server error: ${response.status} ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      // Handle successful response - get the ZIP blob
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      
      setDownloadUrl(url)
      setState('complete')

      console.log('✅ Audio separation complete!')

    } catch (err) {
      console.error('❌ Separation failed:', err)
      
      // Better error messages for common issues
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
      setProgress(0)
    }
  }

  const reset = () => {
    setState('upload')
    setFile(null)
    setError('')
    setProgress(0)
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 p-4">
      <div className="max-w-2xl mx-auto pt-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Music className="h-8 w-8 text-purple-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Song Splitter
            </h1>
          </div>
          <p className="text-gray-600 text-lg">
            Separate your audio into individual stems using AI
          </p>
        </div>

        {/* Main Card */}
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">
              {state === 'upload' && 'Upload Your Audio'}
              {state === 'processing' && 'Processing Audio'}
              {state === 'complete' && 'Separation Complete!'}
              {state === 'error' && 'Something Went Wrong'}
            </CardTitle>
            <CardDescription>
              {state === 'upload' && 'Choose an audio file to separate into drums, bass, vocals, and other'}
              {state === 'processing' && 'AI is separating your audio into individual stems...'}
              {state === 'complete' && 'Your audio has been separated into individual tracks'}
              {state === 'error' && 'Please try again or choose a different file'}
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Upload State */}
            {state === 'upload' && (
              <>
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    isDragOver
                      ? 'border-purple-400 bg-purple-50'
                      : 'border-gray-300 hover:border-purple-400 hover:bg-gray-50'
                  }`}
                  onDrop={handleDrop}
                  onDragOver={(e) => {
                    e.preventDefault()
                    setIsDragOver(true)
                  }}
                  onDragLeave={() => setIsDragOver(false)}
                >
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-700 mb-2">
                    Drop your audio file here
                  </p>
                  <p className="text-gray-500 mb-4">or</p>
                  <Button variant="outline" asChild className="cursor-pointer">
                    <label>
                      Browse Files
                      <input
                        type="file"
                        className="hidden"
                        accept={SUPPORTED_FORMATS.join(',')}
                        onChange={handleFileInput}
                      />
                    </label>
                  </Button>
                </div>

                <div className="flex flex-wrap gap-2 justify-center">
                  <span className="text-sm text-gray-600">Supported formats:</span>
                  {SUPPORTED_FORMATS.map((format) => (
                    <Badge key={format} variant="secondary" className="text-xs">
                      {format.toUpperCase()}
                    </Badge>
                  ))}
                </div>

                {file && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <FileAudio className="h-8 w-8 text-purple-600" />
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(1)} MB
                        </p>
                      </div>
                    </div>
                    <Button 
                      onClick={processAudio} 
                      className="w-full mt-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                    >
                      <Music className="h-4 w-4 mr-2" />
                      Start Separation
                    </Button>
                  </div>
                )}
              </>
            )}

            {/* Processing State */}
            {state === 'processing' && (
              <div className="text-center space-y-6">
                <div className="relative">
                  <div className="flex justify-center">
                    <div className="relative">
                      <Loader2 className="h-20 w-20 text-purple-600 animate-spin" />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <Music className="h-8 w-8 text-purple-800" />
                      </div>
                    </div>
                  </div>
                  <div className="mt-6 flex justify-center space-x-1">
                    <div className="w-3 h-3 bg-purple-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-3 h-3 bg-purple-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-3 h-3 bg-purple-600 rounded-full animate-bounce"></div>
                  </div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-6">
                  <p className="text-lg text-purple-800 font-medium mb-2">
                    🎵 AI is separating your audio
                  </p>
                  <p className="text-sm text-purple-600">
                    This may take a few minutes depending on file size...
                  </p>
                  <p className="text-xs text-purple-500 mt-2">
                    Extracting drums, bass, vocals, and other instruments
                  </p>
                </div>
              </div>
            )}

            {/* Complete State */}
            {state === 'complete' && (
              <div className="text-center space-y-6">
                <div className="flex justify-center">
                  <div className="relative">
                    <div className="h-16 w-16 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="h-8 w-8 text-green-600" />
                    </div>
                    <div className="absolute -top-1 -right-1 h-6 w-6 bg-green-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs font-bold">✓</span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-4 mb-4">
                  <h3 className="font-medium text-green-800 mb-2">🎉 Separation Complete!</h3>
                  <p className="text-sm text-green-600">
                    Your audio has been separated into individual tracks:
                  </p>
                  <div className="flex flex-wrap gap-1 justify-center mt-2">
                    <Badge variant="secondary" className="text-xs">🥁 Drums</Badge>
                    <Badge variant="secondary" className="text-xs">🎸 Bass</Badge>
                    <Badge variant="secondary" className="text-xs">🎤 Vocals</Badge>
                    <Badge variant="secondary" className="text-xs">🎹 Other</Badge>
                  </div>
                </div>

                <div className="space-y-3">
                  <Button 
                    onClick={downloadFile}
                    size="lg"
                    className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download Separated Tracks (.zip)
                  </Button>
                  <Button 
                    onClick={reset} 
                    variant="outline"
                    className="w-full"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Process Another File
                  </Button>
                </div>
              </div>
            )}

            {/* Error State */}
            {state === 'error' && (
              <div className="space-y-4">
                <Alert className="border-red-200 bg-red-50">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800">
                    {error}
                  </AlertDescription>
                </Alert>
                <Button 
                  onClick={reset} 
                  variant="outline"
                  className="w-full"
                >
                  Try Again
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>Powered by AI • Maximum file size: 100MB</p>
        </div>
      </div>
    </div>
  )
}
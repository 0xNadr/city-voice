'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Conversation } from '@elevenlabs/client'

interface VoiceAgentProps {
  agentId: string
}

interface TranscriptMessage {
  role: 'user' | 'agent'
  text: string
}

export default function VoiceAgent({ agentId }: VoiceAgentProps) {
  const [isCallActive, setIsCallActive] = useState(false)
  const [status, setStatus] = useState<string>('Bereit')
  const [agentStatus, setAgentStatus] = useState<'listening' | 'speaking' | 'idle'>('idle')
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([])
  const [tentativeUserText, setTentativeUserText] = useState<string | null>(null)
  const conversationRef = useRef<any>(null)
  const transcriptRef = useRef<HTMLDivElement>(null)

  // Auto-scroll transcript
  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight
    }
  }, [transcript, tentativeUserText])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (conversationRef.current) {
        conversationRef.current.endSession()
      }
    }
  }, [])

  const startConversation = useCallback(async () => {
    try {
      setStatus('Verbinde...')
      setTranscript([])

      const conversation = await Conversation.startSession({
        agentId: agentId,
        onConnect: () => {
          setStatus('Verbunden')
          setIsCallActive(true)
          setAgentStatus('listening')
        },
        onDisconnect: () => {
          setStatus('Anruf beendet')
          setIsCallActive(false)
          setAgentStatus('idle')
        },
        onMessage: (message: any) => {
          if (message.message) {
            if (message.source === 'user') {
              setTentativeUserText(null)
            }
            setTranscript(prev => [...prev, {
              role: message.source === 'user' ? 'user' : 'agent',
              text: message.message
            }])
          }
        },
        onModeChange: (mode: any) => {
          setAgentStatus(mode.mode === 'speaking' ? 'speaking' : 'listening')
          if (mode.mode === 'speaking') {
            setTentativeUserText(null)
          }
        },
        onDebug: (debugEvent: any) => {
          if (debugEvent?.type === 'tentative_user_transcript') {
            const text = debugEvent?.tentative_user_transcription_event?.user_transcript
            if (text) {
              setTentativeUserText(text)
            }
          }
        },
        onError: (error: any) => {
          console.error('Conversation error:', error)
          setStatus('Fehler')
          setIsCallActive(false)
        },
      })

      conversationRef.current = conversation
    } catch (error: any) {
      console.error('Failed to start conversation:', error)
      if (error.name === 'NotAllowedError') {
        setStatus('Mikrofon verweigert')
      } else {
        setStatus('Verbindung fehlgeschlagen')
      }
    }
  }, [agentId])

  const endConversation = useCallback(async () => {
    if (conversationRef.current) {
      await conversationRef.current.endSession()
      conversationRef.current = null
    }
    setIsCallActive(false)
    setStatus('Bereit')
    setAgentStatus('idle')
  }, [])

  return (
    <div className="flex flex-col">
      {/* Status Bar with Mini Orb */}
      <div className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2.5">
          {/* Mini Orb */}
          <div className={`relative w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center ${
            !isCallActive
              ? 'bg-gradient-to-br from-base-700 to-base-800'
              : agentStatus === 'speaking'
                ? 'bg-gradient-to-br from-brand-purple to-purple-700 orb-speaking'
                : 'bg-gradient-to-br from-brand-cyan to-cyan-600 orb-listening'
          }`}>
            {isCallActive ? (
              <div className="flex items-end gap-0.5 h-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className={`w-0.5 sm:w-1 rounded-full ${
                      agentStatus === 'speaking' ? 'bg-white' : 'bg-base-bg-main'
                    } soundbar soundbar-${i}`}
                    style={{ height: '60%' }}
                  />
                ))}
              </div>
            ) : (
              <svg className="w-5 h-5 sm:w-6 sm:h-6 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            )}
          </div>

          {/* Status Text */}
          <div className="flex flex-col">
            <span className={`text-sm sm:text-base font-semibold ${
              !isCallActive
                ? 'text-text-primary'
                : agentStatus === 'speaking'
                  ? 'text-brand-purple'
                  : 'text-brand-cyan'
            }`}>
              {!isCallActive && 'Bereit'}
              {isCallActive && agentStatus === 'speaking' && 'Agent spricht'}
              {isCallActive && agentStatus === 'listening' && 'Hört zu'}
            </span>
            <span className="text-[10px] sm:text-xs text-text-muted">
              {!isCallActive && 'Klicken Sie auf Anrufen'}
              {isCallActive && agentStatus === 'speaking' && 'Bitte warten...'}
              {isCallActive && agentStatus === 'listening' && 'Sprechen Sie jetzt'}
            </span>
          </div>
        </div>

        {/* Status Indicator */}
        <div className={`w-2.5 h-2.5 rounded-full ${
          !isCallActive
            ? 'bg-text-muted'
            : agentStatus === 'speaking'
              ? 'bg-brand-purple animate-pulse'
              : 'bg-brand-cyan animate-pulse'
        }`} />
      </div>

      {/* Transcript Area - Larger */}
      <div
        ref={transcriptRef}
        className="h-[200px] sm:h-[220px] bg-base-900 border border-base-700 rounded-xl p-3 overflow-y-auto mb-4"
      >
        {transcript.length === 0 && !tentativeUserText ? (
          <div className="h-full flex items-center justify-center text-center px-4">
            <p className="text-xs sm:text-sm text-text-muted">
              {isCallActive
                ? 'Sprechen Sie jetzt - Ihre Nachricht erscheint hier'
                : 'Starten Sie einen Anruf, um mit dem Assistenten zu sprechen'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {transcript.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
              >
                <div className={`flex-shrink-0 w-6 h-6 sm:w-7 sm:h-7 rounded-full flex items-center justify-center ${
                  msg.role === 'user' ? 'bg-brand-cyan' : 'bg-brand-purple'
                }`}>
                  {msg.role === 'user' ? (
                    <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-base-bg-main" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  ) : (
                    <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  )}
                </div>
                <div className={`max-w-[85%] rounded-lg px-3 py-2 text-sm sm:text-base ${
                  msg.role === 'user'
                    ? 'bg-brand-cyan/20 text-brand-cyan border border-brand-cyan/30'
                    : 'bg-brand-purple/20 text-purple-300 border border-brand-purple/30'
                }`}>
                  {msg.text}
                </div>
              </div>
            ))}
            {tentativeUserText && (
              <div className="flex gap-2 flex-row-reverse">
                <div className="flex-shrink-0 w-6 h-6 sm:w-7 sm:h-7 rounded-full flex items-center justify-center bg-brand-cyan/50">
                  <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-base-bg-main" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <div className="max-w-[85%] rounded-lg px-3 py-2 text-sm sm:text-base bg-brand-cyan/10 text-brand-cyan/70 italic border border-brand-cyan/20">
                  {tentativeUserText}...
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Call Controls */}
      <div className="flex justify-center">
        {!isCallActive ? (
          <button
            onClick={startConversation}
            className="flex items-center gap-2 px-5 py-2.5 sm:px-6 sm:py-3 bg-brand-cyan text-base-bg-main rounded-full hover:bg-brand-cyan/90 transition-all font-semibold text-sm sm:text-base glow-cyan"
          >
            <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            Anrufen
          </button>
        ) : (
          <button
            onClick={endConversation}
            className="flex items-center gap-2 px-5 py-2.5 sm:px-6 sm:py-3 bg-red-500/90 text-white rounded-full hover:bg-red-500 transition-colors font-semibold text-sm sm:text-base shadow-lg shadow-red-500/30"
          >
            <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.493-1.498a1 1 0 00-1.21.502l-1.13 2.257a11.042 11.042 0 01-5.516-5.517l2.257-1.128a1 1 0 00.502-1.21L9.228 3.683A1 1 0 008.279 3H5z" />
            </svg>
            Beenden
          </button>
        )}
      </div>
    </div>
  )
}

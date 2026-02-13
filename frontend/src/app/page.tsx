'use client'

import VoiceAgent from '@/components/VoiceAgent'
import OpeningHours from '@/components/OpeningHours'

// ElevenLabs Agent ID - set this after creating your agent in the ElevenLabs dashboard
const AGENT_ID = process.env.NEXT_PUBLIC_ELEVENLABS_AGENT_ID || ''

export default function Home() {
  return (
    <main className="min-h-screen p-3 sm:p-4 md:p-8 bg-base-bg-main dotted-bg">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="text-center mb-6 sm:mb-8 md:mb-10">
          <h1 className="text-2xl sm:text-3xl md:text-5xl font-bold text-text-primary mb-2 sm:mb-3 tracking-tight">
            City<span className="text-brand-cyan">Voice</span>
          </h1>
          <p className="text-text-secondary text-sm sm:text-base md:text-lg">
            Ihr Sprachassistent für die Hansestadt Lüneburg
          </p>
        </header>

        {/* Main Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          {/* Left Column - Voice Agent */}
          <div className="bg-base-bg-card border border-base-700 rounded-xl sm:rounded-2xl p-4 sm:p-5 md:p-6">
            <h2 className="text-base sm:text-lg font-semibold text-text-primary mb-3 sm:mb-4 text-center flex items-center justify-center gap-2">
              <span className="w-2 h-2 rounded-full bg-brand-cyan"></span>
              Sprachassistent
            </h2>

            {AGENT_ID ? (
              <VoiceAgent agentId={AGENT_ID} />
            ) : (
              <div className="text-center py-6 sm:py-8">
                <div className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-3 sm:mb-4 rounded-full bg-base-800 border border-base-700 flex items-center justify-center">
                  <svg className="w-6 h-6 sm:w-8 sm:h-8 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <p className="text-text-secondary text-sm sm:text-base mb-2">Agent ID nicht konfiguriert</p>
                <p className="text-xs sm:text-sm text-text-muted">
                  Setzen Sie NEXT_PUBLIC_ELEVENLABS_AGENT_ID in der .env Datei
                </p>
              </div>
            )}
          </div>

          {/* Right Column - Opening Hours */}
          <div className="bg-base-bg-card border border-base-700 rounded-xl sm:rounded-2xl p-4 sm:p-5 md:p-6">
            <h2 className="text-base sm:text-lg font-semibold text-text-primary mb-3 sm:mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-brand-cyan"></span>
              Öffnungszeiten
            </h2>
            <OpeningHours />
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center mt-6 sm:mt-8 md:mt-10 text-xs sm:text-sm text-text-muted">
          <p>CityVoice - Ein Prototyp für die Hansestadt Lüneburg</p>
        </footer>
      </div>
    </main>
  )
}

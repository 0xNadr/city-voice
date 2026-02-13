'use client'

import { useState, useEffect } from 'react'

// Data format: { "Einwohnermeldeamt": { "Montag": "08:00-12:00", ... }, ... }
type OpeningHoursData = Record<string, Record<string, string>>

const dayOrder = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
const dayShort: Record<string, string> = {
  'Montag': 'Mo',
  'Dienstag': 'Di',
  'Mittwoch': 'Mi',
  'Donnerstag': 'Do',
  'Freitag': 'Fr',
  'Samstag': 'Sa',
  'Sonntag': 'So',
}

export default function OpeningHours() {
  const [data, setData] = useState<OpeningHoursData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/opening-hours`)
        if (!response.ok) throw new Error('Failed to fetch')
        const result = await response.json()
        console.log('Opening hours data:', result)
        setData(result)
      } catch (err) {
        setError('Öffnungszeiten konnten nicht geladen werden')
        console.error('Error fetching opening hours:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="h-[280px] sm:h-[300px] animate-pulse space-y-2">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-10 sm:h-11 bg-base-800 rounded-lg" />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[280px] sm:h-[300px] flex flex-col items-center justify-center text-center text-text-muted">
        <p className="text-sm">{error}</p>
        <p className="text-xs mt-2">Fragen Sie den Sprachassistenten nach Öffnungszeiten</p>
      </div>
    )
  }

  const departments = data ? Object.entries(data) : []

  if (departments.length === 0) {
    return (
      <div className="h-[280px] sm:h-[300px] flex items-center justify-center text-text-muted">
        <p className="text-sm">Keine Öffnungszeiten verfügbar</p>
      </div>
    )
  }

  return (
    <div className="h-[280px] sm:h-[300px] space-y-2 overflow-y-auto">
      {departments.map(([deptName, hours]) => (
        <div
          key={deptName}
          className="border border-base-700 rounded-lg overflow-hidden"
        >
          <button
            onClick={() => setExpanded(expanded === deptName ? null : deptName)}
            className="w-full px-3 py-2.5 sm:px-4 sm:py-3 text-left bg-base-800 hover:bg-base-700 transition-colors flex justify-between items-center"
          >
            <span className="font-medium text-text-primary text-xs sm:text-sm">{deptName}</span>
            <svg
              className={`w-3.5 h-3.5 sm:w-4 sm:h-4 text-text-muted transition-transform flex-shrink-0 ${expanded === deptName ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {expanded === deptName && (
            <div className="px-3 py-2.5 sm:px-4 sm:py-3 bg-base-900">
              <div className="space-y-1 text-[10px] sm:text-xs">
                {dayOrder.map((day) => {
                  const time = hours[day]
                  if (!time) return null
                  return (
                    <div key={day} className="flex justify-between py-0.5">
                      <span className="text-text-muted">{dayShort[day]}:</span>
                      <span className={`${time === 'geschlossen' ? 'text-red-400' : 'text-text-secondary'}`}>
                        {time}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

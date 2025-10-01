import { useState } from 'react'
import { searchApi } from './services/api'
import type { SearchResults } from './types'
import SearchForm from './components/SearchForm'
import ResultsTable from './components/ResultsTable'
import './App.css'

function App() {
  const [results, setResults] = useState<SearchResults | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (location: string, checkIn: string, checkOut: string, guests: number, discountTypes: string[]) => {
    setLoading(true)
    setError(null)

    try {
      // Create mock search (with instant results)
      const response = await fetch('http://localhost:8000/api/mock/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      const searchData = await response.json()

      // Get results
      const resultsData = await searchApi.getResults(searchData.search_id)
      setResults(resultsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch results')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Travel Discount Comparison
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Compare hotel rates across AARP, AAA, Senior, and other discount programs
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <SearchForm onSearch={handleSearch} loading={loading} />

          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              <strong className="font-bold">Error: </strong>
              <span>{error}</span>
            </div>
          )}

          {loading && (
            <div className="mt-8 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
              <p className="mt-4 text-gray-600">Searching hotels...</p>
            </div>
          )}

          {results && !loading && (
            <div className="mt-8">
              <ResultsTable results={results} />
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App

import { useState } from 'react'

interface SearchFormProps {
  onSearch: (location: string, checkIn: string, checkOut: string, guests: number, discountTypes: string[]) => void
  loading: boolean
}

export default function SearchForm({ onSearch, loading }: SearchFormProps) {
  const [location, setLocation] = useState('New York, NY')
  const [checkIn, setCheckIn] = useState(() => {
    const date = new Date()
    date.setDate(date.getDate() + 30)
    return date.toISOString().split('T')[0]
  })
  const [checkOut, setCheckOut] = useState(() => {
    const date = new Date()
    date.setDate(date.getDate() + 32)
    return date.toISOString().split('T')[0]
  })
  const [guests, setGuests] = useState(2)
  const [discountTypes, setDiscountTypes] = useState<string[]>(['aarp', 'aaa', 'senior'])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch(location, checkIn, checkOut, guests, discountTypes)
  }

  const toggleDiscountType = (type: string) => {
    if (discountTypes.includes(type)) {
      setDiscountTypes(discountTypes.filter(t => t !== type))
    } else {
      setDiscountTypes([...discountTypes, type])
    }
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {/* Location */}
          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700">
              Location
            </label>
            <input
              type="text"
              id="location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
              placeholder="City, State or Hotel Name"
              required
            />
          </div>

          {/* Guests */}
          <div>
            <label htmlFor="guests" className="block text-sm font-medium text-gray-700">
              Guests
            </label>
            <input
              type="number"
              id="guests"
              value={guests}
              onChange={(e) => setGuests(parseInt(e.target.value))}
              min="1"
              max="10"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
              required
            />
          </div>

          {/* Check-in */}
          <div>
            <label htmlFor="checkIn" className="block text-sm font-medium text-gray-700">
              Check-in Date
            </label>
            <input
              type="date"
              id="checkIn"
              value={checkIn}
              onChange={(e) => setCheckIn(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
              required
            />
          </div>

          {/* Check-out */}
          <div>
            <label htmlFor="checkOut" className="block text-sm font-medium text-gray-700">
              Check-out Date
            </label>
            <input
              type="date"
              id="checkOut"
              value={checkOut}
              onChange={(e) => setCheckOut(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
              required
            />
          </div>
        </div>

        {/* Discount Types */}
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Discount Types to Test
          </label>
          <div className="flex flex-wrap gap-3">
            {['aarp', 'aaa', 'senior'].map((type) => (
              <label key={type} className="flex items-center">
                <input
                  type="checkbox"
                  checked={discountTypes.includes(type)}
                  onChange={() => toggleDiscountType(type)}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700 uppercase">{type}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <div className="mt-6">
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Searching...' : 'Search Hotels'}
          </button>
        </div>
      </form>
    </div>
  )
}

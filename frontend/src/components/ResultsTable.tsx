import type { SearchResults } from '../types'

interface ResultsTableProps {
  results: SearchResults
}

export default function ResultsTable({ results }: ResultsTableProps) {
  // Group results by hotel
  const hotelGroups = results.results.reduce((acc, result) => {
    if (!acc[result.hotel_name]) {
      acc[result.hotel_name] = []
    }
    acc[result.hotel_name].push(result)
    return acc
  }, {} as Record<string, typeof results.results>)

  // Calculate best deal
  const allPrices = results.results
    .filter(r => r.available && r.total_price)
    .map(r => r.total_price!)
  const bestPrice = Math.min(...allPrices)

  const formatPrice = (price: number | null) => {
    return price ? `$${price.toFixed(2)}` : 'N/A'
  }

  const calculateSavings = (originalPrice: number | null, discountedPrice: number | null) => {
    if (!originalPrice || !discountedPrice) return 0
    return ((originalPrice - discountedPrice) / originalPrice * 100).toFixed(1)
  }

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">Search Results</h2>
        <p className="mt-1 text-sm text-gray-600">
          {results.location} • {results.check_in} to {results.check_out} • {results.guests} guests • {results.result_count} results
        </p>
      </div>

      {/* Results */}
      <div className="divide-y divide-gray-200">
        {Object.entries(hotelGroups).map(([hotelName, hotelResults]) => (
          <div key={hotelName} className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{hotelName}</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Discount Type
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Room Rate
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Taxes & Fees
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Savings
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {hotelResults.map((result) => {
                    const isBestDeal = result.total_price === bestPrice
                    const savings = calculateSavings(result.original_price, result.discounted_price)

                    return (
                      <tr
                        key={result.result_id}
                        className={isBestDeal ? 'bg-green-50' : ''}
                      >
                        <td className="px-4 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span className="text-sm font-medium text-gray-900 uppercase">
                              {result.discount_type}
                            </span>
                            {isBestDeal && (
                              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Best Deal
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                          {result.discount_type !== 'none' && result.original_price !== result.discounted_price ? (
                            <div>
                              <span className="line-through text-gray-400 mr-2">
                                {formatPrice(result.original_price)}
                              </span>
                              <span className="font-semibold">
                                {formatPrice(result.discounted_price)}
                              </span>
                            </div>
                          ) : (
                            <span>{formatPrice(result.discounted_price)}</span>
                          )}
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatPrice(result.taxes + result.fees)}
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                          {formatPrice(result.total_price)}
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                          {parseFloat(savings) > 0 ? (
                            <span className="text-green-600 font-medium">
                              {savings}% off
                            </span>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

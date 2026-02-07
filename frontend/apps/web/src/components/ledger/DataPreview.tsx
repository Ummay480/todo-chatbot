import React from 'react';

interface SalesEntry {
  id?: number;
  date?: string;
  nozzle_id?: string;
  fuel_type?: string;
  opening_reading?: number;
  closing_reading?: number;
  liters_sold?: number;
  rate_per_liter?: number;
  total_amount?: number;
  ocr_confidence?: number;
  is_manual_correction?: boolean;
  manual_correction_notes?: string;
}

interface DataPreviewProps {
  data: any; // The extracted ledger data
  isLoading?: boolean;
  isError?: boolean;
  errorMessage?: string;
}

const DataPreview: React.FC<DataPreviewProps> = ({ data, isLoading, isError, errorMessage }) => {
  if (isLoading) {
    return (
      <div className="data-preview loading">
        <h3>Processing Data...</h3>
        <p>Please wait while we extract and process the ledger data.</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="data-preview error">
        <h3>Error Loading Data</h3>
        <p>{errorMessage || 'An error occurred while loading the extracted data.'}</p>
      </div>
    );
  }

  if (!data || !data.extracted_rows || data.extracted_rows.length === 0) {
    return (
      <div className="data-preview empty">
        <h3>No Data Available</h3>
        <p>No extracted data to display. Please upload a ledger image to see the results.</p>
      </div>
    );
  }

  // Extract the first row to determine column names
  const firstRow = data.extracted_rows[0];
  const columnNames = firstRow ? Object.keys(firstRow) : [];

  return (
    <div className="data-preview">
      <h3>Extracted Data Preview</h3>

      {/* Display overall confidence */}
      {data.overall_confidence !== undefined && (
        <div className="confidence-summary">
          <p><strong>Overall OCR Confidence:</strong> {(data.overall_confidence * 100).toFixed(2)}%</p>
        </div>
      )}

      {/* Display detected columns */}
      {data.detected_columns && data.detected_columns.length > 0 && (
        <div className="detected-columns">
          <h4>Detected Columns:</h4>
          <ul>
            {data.detected_columns.map((col: any, index: number) => (
              <li key={index}>
                <strong>{col.name}</strong> (Position: {col.position}, Confidence: {(col.confidence * 100).toFixed(2)}%)
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Display extracted data in a table */}
      <div className="extracted-data-table">
        <h4>Extracted Entries:</h4>
        <table>
          <thead>
            <tr>
              {columnNames.map((colName: string) => (
                <th key={colName}>{colName.replace(/_/g, ' ').toUpperCase()}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.extracted_rows.map((row: any, rowIndex: number) => (
              <tr key={rowIndex}>
                {columnNames.map((colName: string, colIndex: number) => {
                  const value = row[colName];

                  // Format the value based on column type
                  let displayValue = value;
                  if (typeof value === 'number') {
                    if (colName.toLowerCase().includes('amount') || colName.toLowerCase().includes('rate')) {
                      displayValue = `₨${value.toFixed(2)}`;
                    } else if (colName.toLowerCase().includes('liter')) {
                      displayValue = value.toFixed(2);
                    }
                  }

                  return (
                    <td
                      key={`${rowIndex}-${colIndex}`}
                      className={row.needs_review ? 'needs-review' : ''}
                    >
                      {displayValue}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Show entries that need review */}
      {data.entries_needing_review && data.entries_needing_review.length > 0 && (
        <div className="review-section">
          <h4>Entries Needing Review:</h4>
          <p>{data.entries_needing_review.length} entries have low confidence and require manual verification.</p>
        </div>
      )}
    </div>
  );
};

export default DataPreview;
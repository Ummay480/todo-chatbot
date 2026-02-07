"use client";

import { useState } from 'react';

export default function Home() {
  const [message, setMessage] = useState('');

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Petrol Pump Ledger Automation</h1>
        </div>
      </header>

      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="border-4 border-dashed border-gray-200 rounded-lg p-8 text-center">
              <h2 className="text-xl font-semibold mb-4">Welcome to Petrol Pump Ledger Automation</h2>
              <p className="mb-4">This system helps digitize handwritten petrol pump ledgers using OCR and AI.</p>

              <div className="mt-6">
                <button
                  onClick={async () => {
                    try {
                      const response = await fetch('http://localhost:8000/');
                      const data = await response.json();
                      setMessage(data.message);
                    } catch (error) {
                      setMessage('Error connecting to backend');
                      console.error('Error:', error);
                    }
                  }}
                  className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                >
                  Test Backend Connection
                </button>

                {message && (
                  <div className="mt-4 p-4 bg-green-100 text-green-800 rounded">
                    Response: {message}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
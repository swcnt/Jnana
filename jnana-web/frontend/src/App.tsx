import React, { useState, useEffect } from 'react';
import { Brain } from 'lucide-react';
import './App.css';

function App() {
  const [connected, setConnected] = useState(false);
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    // Test backend connection
    fetch('/api/health')
      .then(response => response.json())
      .then(data => {
        if (data.status === 'healthy') {
          setConnected(true);
        }
      })
      .catch(error => {
        console.error('Backend connection failed:', error);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-12 px-4">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <Brain className="h-16 w-16 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Jnana Web Interface
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            AI Co-Scientist for Hypothesis Generation and Research
          </p>
          
          <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
            <h2 className="text-lg font-semibold mb-4">System Status</h2>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span>Backend Connection:</span>
                <span className={`px-2 py-1 rounded text-sm ${
                  connected 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Frontend:</span>
                <span className="px-2 py-1 rounded text-sm bg-green-100 text-green-800">
                  Running
                </span>
              </div>
            </div>
          </div>

          {connected && (
            <div className="mt-8">
              <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                Start Research Session
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

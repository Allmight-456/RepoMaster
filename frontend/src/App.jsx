import { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [documentation, setDocumentation] = useState('');
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('preview'); // 'raw' or 'preview'
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleGenerateDocs = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/generate-docs-from-url', { url: repoUrl });
      setDocumentation(response.data);
    } catch (error) {
      console.error('Error generating documentation:', error);
      alert('Failed to generate documentation');
    }
    setLoading(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(documentation).then(() => {
      alert('Documentation copied!');
    });
  };

  const formatDocumentation = (doc) => {
    return doc.replace(/\\n/g, '\n').replace(/\n\n/g, '\n');
  };

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center p-6 ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-black'}`}>
      <header className="text-center mb-8">
        <h1 className="text-4xl text-teal-600 font-semibold">RepoMaster</h1>
        <p className="text-lg mt-4">Generate documentation from a GitHub repository URL.</p>
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="mt-4 bg-gray-200 text-gray-800 py-2 px-6 rounded-lg hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
        >
          Dark Mode
        </button>
      </header>
      <div className={`w-full max-w-3xl p-6 rounded-lg shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        <div className="mb-4">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="Enter GitHub repository URL"
            className={`w-full p-4 border rounded-lg shadow-sm focus:outline-none focus:ring-2 ${darkMode ? 'bg-gray-700 border-gray-600 text-white focus:ring-blue-400' : 'bg-white border-gray-300 text-black focus:ring-blue-400'}`}
          />
        </div>
        <div className="flex justify-between mb-4">
          <button
            onClick={handleGenerateDocs}
            disabled={loading}
            className={`py-2 px-6 rounded-lg shadow-md focus:outline-none disabled:opacity-50 ${darkMode ? 'bg-teal-600 text-white hover:bg-teal-700' : 'bg-black text-white hover:bg-gray-800'}`}
          >
            Generate
          </button>
        </div>

        {loading && (
          <div className="flex justify-center items-center">
            <div className="animate-spin border-t-4 border-teal-600 border-solid rounded-full w-12 h-12"></div>
            <p className="ml-4 text-lg">Processing...</p>
          </div>
        )}

        {documentation && (
          <div className="mt-6">
            <div className="flex flex-col sm:flex-row justify-between mb-4">
              <div className="flex flex-col sm:flex-row">
                <button
                  onClick={() => setView('raw')}
                  className={`py-2 px-6 rounded-lg hover:bg-gray-300 ${view === 'raw' ? 'bg-teal-600 text-white' : ''} ${darkMode ? 'bg-gray-700 text-white hover:bg-gray-600' : 'bg-gray-200 text-gray-800'}`}
                >
                  Raw
                </button>
                <button
                  onClick={() => setView('preview')}
                  className={`py-2 px-6 rounded-lg hover:bg-gray-300 mt-2 sm:mt-0 sm:ml-2 ${view === 'preview' ? 'bg-teal-600 text-white' : ''} ${darkMode ? 'bg-gray-700 text-white hover:bg-gray-600' : 'bg-gray-200 text-gray-800'}`}
                >
                  Preview
                </button>
              </div>
              <button
                onClick={handleCopy}
                className={`bg-green-600 text-white py-2 px-6 rounded-lg shadow-md hover:bg-green-700 mt-2 sm:mt-0`}
              >
                Copy
              </button>
            </div>

            {view === 'raw' ? (
              <pre className={`p-4 rounded-lg text-sm font-mono overflow-x-auto ${darkMode ? 'bg-gray-700 text-white' : 'bg-gray-100 text-gray-800'}`}>{formatDocumentation(documentation)}</pre>
            ) : (
              <div className={`p-4 rounded-lg text-sm ${darkMode ? 'bg-gray-700 text-white' : 'bg-gray-100 text-gray-800'}`}>
                <ReactMarkdown
                  className={`prose ${darkMode ? 'prose-dark' : ''}`}
                  components={{
                    h1: ({ node, ...props }) => <h1 {...props} className="text-3xl font-semibold text-blue-600" />,
                    h2: ({ node, ...props }) => <h2 {...props} className="text-2xl font-semibold text-blue-500" />,
                    h3: ({ node, ...props }) => <h3 {...props} className="text-xl font-semibold text-blue-400" />,
                  }}
                >
                  {formatDocumentation(documentation)}
                </ReactMarkdown>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

import { useState } from 'react';
import axios from 'axios';

interface BankCard {
  issuer_name: string;
  payment_network: string;
  card_number: string;
  cardholder_name: string;
  expiry_date: string;
  card_type: string | null;
  confidence: number;
}

const API_URL = '/api/v1';

function App() {
  const [activeTab, setActiveTab] = useState<'extract' | 'history'>('extract');
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BankCard | null>(null);
  const [history, setHistory] = useState<BankCard[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const handleFile = (selectedFile: File) => {
    if (!selectedFile.type.startsWith('image/')) {
      alert('Only image files are allowed!');
      return;
    }
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setResult(null);
  };

  const extractCard = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post<BankCard>(`${API_URL}/extract`, formData);
      setResult(res.data);
    } catch (err: any) {
      alert('Error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const copyNumber = () => {
    if (result) {
      navigator.clipboard.writeText(result.card_number);
      alert('Card number copied!');
    }
  };

  // Xóa ảnh preview
  const removeImage = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
  };

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await axios.get<BankCard[]>(`${API_URL}/cards`);
      setHistory(res.data);
    } catch (err) {
      alert('Failed to load history');
    } finally {
      setHistoryLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-4xl font-bold text-center mb-10 text-indigo-700 flex items-center justify-center gap-3">
          Card Extractor
        </h1>

        {/* Tabs */}
        <div className="flex border-b mb-8">
          <button
            onClick={() => setActiveTab('extract')}
            className={`flex-1 py-4 text-lg font-semibold ${activeTab === 'extract' ? 'border-b-4 border-indigo-600 text-indigo-600' : 'text-gray-500'}`}
          >
            Extract Card
          </button>
          <button
            onClick={() => { setActiveTab('history'); loadHistory(); }}
            className={`flex-1 py-4 text-lg font-semibold ${activeTab === 'history' ? 'border-b-4 border-indigo-600 text-indigo-600' : 'text-gray-500'}`}
          >
            History
          </button>
        </div>

        {/* Extract Tab */}
        {activeTab === 'extract' && (
          <div>
            {!previewUrl ? (
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
                onClick={() => document.getElementById('fileInput')?.click()}
                className="border-4 border-dashed border-gray-300 rounded-3xl p-20 text-center hover:border-indigo-500 transition cursor-pointer"
              >
                <i className="fa-solid fa-cloud-arrow-up text-7xl text-gray-400 mb-6"></i>
                <p className="text-2xl font-medium">Drag & drop your bank card image here</p>
                <p className="text-gray-500 my-4">or</p>
                <input
                  id="fileInput"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => e.target.files && handleFile(e.target.files[0])}
                />
                <span className="bg-indigo-600 text-white px-8 py-4 rounded-2xl text-lg font-medium cursor-pointer hover:bg-indigo-700">
                  Choose Image File
                </span>
              </div>
            ) : (
              <div className="space-y-8">
                {/* Preview với nút X */}
                <div className="relative mx-auto max-w-md">
                  <img 
                    src={previewUrl} 
                    alt="preview" 
                    className="w-full rounded-3xl shadow-2xl" 
                  />
                  <button
                    onClick={removeImage}
                    className="absolute -top-3 -right-3 bg-white hover:bg-red-500 hover:text-white text-gray-700 w-9 h-9 rounded-full shadow-lg flex items-center justify-center text-2xl transition-all"
                    title="Remove image"
                  >
                    ✕
                  </button>
                </div>

                {loading ? (
                  <div className="text-center py-12">
                    <div className="animate-spin w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto"></div>
                    <p className="mt-6 text-2xl text-gray-600">Extracting with GPT-4o...</p>
                  </div>
                ) : !result ? (
                  <button
                    onClick={extractCard}
                    className="w-full bg-green-600 hover:bg-green-700 text-white py-6 rounded-3xl text-2xl font-semibold flex items-center justify-center gap-4"
                  >
                    <i className="fa-solid fa-wand-magic-sparkles"></i>
                    Extract Card Information
                  </button>
                ) : (
                  <div className="bg-white p-10 rounded-3xl shadow-2xl">
                    <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
                      <i className="fa-solid fa-credit-card"></i> Extraction Result
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-xl">
                      <div><strong>Bank:</strong> <span className="font-semibold">{result.issuer_name}</span></div>
                      <div><strong>Network:</strong> <span className="font-semibold">{result.payment_network}</span></div>
                      <div className="col-span-2">
                        <strong>Card Number:</strong>{' '}
                        <span className="font-mono text-3xl font-bold tracking-widest">{result.card_number}</span>
                        <button 
                          onClick={copyNumber} 
                          className="ml-6 text-indigo-600 hover:text-indigo-800 text-2xl"
                          title="Copy card number"
                        >
                        </button>
                      </div>
                      <div><strong>Cardholder:</strong> <span className="font-semibold">{result.cardholder_name}</span></div>
                      <div><strong>Expiry Date:</strong> <span className="font-semibold">{result.expiry_date}</span></div>
                      <div><strong>Type:</strong> <span className="font-semibold">{result.card_type || '—'}</span></div>
                    </div>

                    <button
                      onClick={removeImage}
                      className="mt-12 w-full py-6 bg-gray-200 hover:bg-gray-300 rounded-3xl text-xl font-medium"
                    >
                      Extract Another Card
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div>
            <button
              onClick={loadHistory}
              className="mb-6 bg-indigo-600 text-white px-8 py-4 rounded-2xl hover:bg-indigo-700 flex items-center gap-3"
            >
              <i className="fa-solid fa-rotate"></i> Refresh History
            </button>

            {historyLoading ? (
              <p className="text-center text-xl">Loading...</p>
            ) : history.length === 0 ? (
              <p className="text-center text-gray-500 text-xl">No cards extracted yet</p>
            ) : (
              <div className="grid gap-6">
                {history.map((card, i) => (
                  <div key={i} className="bg-white p-8 rounded-3xl shadow-xl">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-2xl font-bold">{card.issuer_name}</h3>
                        <p className="text-gray-500">{card.payment_network} • {card.card_type || ''}</p>
                      </div>
                      <div className="text-right">
                        <div className="font-mono text-3xl font-bold tracking-widest">{card.card_number}</div>
                        <div className="text-lg text-gray-400 mt-1">{card.expiry_date}</div>
                      </div>
                    </div>
                    <div className="mt-6 text-xl">Cardholder: <span className="font-semibold">{card.cardholder_name}</span></div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
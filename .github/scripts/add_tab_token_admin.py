from pathlib import Path

path = Path('app/page.js')
text = path.read_text()

# Add Ticket icon.
old_import = 'Database, FileText } from \'lucide-react\';'
new_import = 'Database, FileText, Ticket, Copy } from \'lucide-react\';'
if old_import not in text:
    raise SystemExit('Lucide import marker not found')
text = text.replace(old_import, new_import, 1)

# Add token state after upcoming-video state.
state_marker = "  const [isAddingUpcoming, setIsAddingUpcoming] = useState(false);\n"
state_block = """  const [isAddingUpcoming, setIsAddingUpcoming] = useState(false);

  // Tab Studio token management state
  const [tabTokens, setTabTokens] = useState([]);
  const [tokenStats, setTokenStats] = useState({ total: 0, active: 0, used: 0, expired: 0, disabled: 0 });
  const [tokenType, setTokenType] = useState('testing');
  const [tokenQuantity, setTokenQuantity] = useState(1);
  const [tokenUses, setTokenUses] = useState(1);
  const [tokenEmail, setTokenEmail] = useState('');
  const [tokenExpiry, setTokenExpiry] = useState('');
  const [tokenNotes, setTokenNotes] = useState('');
  const [tokenStatus, setTokenStatus] = useState({ type: '', message: '' });
  const [isLoadingTokens, setIsLoadingTokens] = useState(false);
  const [isGeneratingTokens, setIsGeneratingTokens] = useState(false);
"""
if state_marker not in text:
    raise SystemExit('Token state insertion marker not found')
text = text.replace(state_marker, state_block, 1)

# Add token functions before scheduled-video functions.
function_marker = '  // Sync scheduled videos from YouTube\n'
function_block = """  // Tab Studio token management
  const getAdminAuthorization = () => {
    const storedPassword = sessionStorage.getItem('dadrock_admin_auth') || '';
    return `Basic ${btoa(`admin:${storedPassword}`)}`;
  };

  const loadTabTokens = async () => {
    if (!isAuthenticated) return;
    setIsLoadingTokens(true);
    try {
      const response = await fetch('/api/admin/tab-tokens', {
        headers: { Authorization: getAdminAuthorization() },
        cache: 'no-store',
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to load tokens.');
      setTabTokens(data.tokens || []);
      setTokenStats(data.stats || { total: 0, active: 0, used: 0, expired: 0, disabled: 0 });
    } catch (error) {
      setTokenStatus({ type: 'error', message: error.message || 'Unable to load tokens.' });
    } finally {
      setIsLoadingTokens(false);
    }
  };

  const handleGenerateTokens = async () => {
    setIsGeneratingTokens(true);
    setTokenStatus({ type: '', message: '' });
    try {
      const response = await fetch('/api/admin/tab-tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: getAdminAuthorization(),
        },
        body: JSON.stringify({
          action: 'generate',
          type: tokenType,
          quantity: Number(tokenQuantity),
          uses: Number(tokenUses),
          assignedEmail: tokenEmail.trim(),
          expiresAt: tokenExpiry || null,
          notes: tokenNotes.trim(),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to generate tokens.');
      setTokenStatus({ type: 'success', message: `${data.tokens?.length || 0} token(s) generated successfully.` });
      await loadTabTokens();
    } catch (error) {
      setTokenStatus({ type: 'error', message: error.message || 'Unable to generate tokens.' });
    } finally {
      setIsGeneratingTokens(false);
    }
  };

  const handleTokenAction = async (id, action, active = false) => {
    try {
      const response = await fetch('/api/admin/tab-tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: getAdminAuthorization(),
        },
        body: JSON.stringify({ id, action, active }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to update token.');
      await loadTabTokens();
    } catch (error) {
      setTokenStatus({ type: 'error', message: error.message || 'Unable to update token.' });
    }
  };

  useEffect(() => {
    if (isAuthenticated && currentPage === 'admin') loadTabTokens();
  }, [isAuthenticated, currentPage]);

  // Sync scheduled videos from YouTube
"""
if function_marker not in text:
    raise SystemExit('Token function insertion marker not found')
text = text.replace(function_marker, function_block, 1)

# Insert token management as the third admin function.
ui_marker = '          {/* DadRock Tabs Quickies Sync */}\n'
ui_block = """          {/* Tab Studio Token Management - Admin Function 3 */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-5">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Ticket className="w-5 h-5 text-green-400" />
                  Tab Studio Tokens
                </h2>
                <p className="text-zinc-400 mt-1 text-sm">Generate and manage complimentary PDF unlocks, testing tokens, and promotional offers.</p>
              </div>
              <button
                onClick={loadTabTokens}
                disabled={isLoadingTokens}
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-zinc-800 px-4 py-2 text-sm font-bold text-zinc-200 hover:bg-zinc-700 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${isLoadingTokens ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-5 mb-6">
              {[
                ['Total', tokenStats.total, 'text-white'],
                ['Active', tokenStats.active, 'text-green-400'],
                ['Used', tokenStats.used, 'text-blue-400'],
                ['Expired', tokenStats.expired, 'text-amber-400'],
                ['Disabled', tokenStats.disabled, 'text-red-400'],
              ].map(([label, value, color]) => (
                <div key={label} className="rounded-lg border border-zinc-700 bg-zinc-800/60 p-3 text-center">
                  <p className={`text-2xl font-black ${color}`}>{value || 0}</p>
                  <p className="text-xs text-zinc-500">{label}</p>
                </div>
              ))}
            </div>

            <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-4 mb-6">
              <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                <Plus className="w-4 h-4 text-green-400" /> Generate Tokens
              </h3>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <label className="text-sm text-zinc-400">
                  Token Type
                  <select value={tokenType} onChange={(e) => setTokenType(e.target.value)} className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-3 text-white">
                    <option value="testing">Testing</option>
                    <option value="giveaway">Giveaway</option>
                    <option value="promotion">Promotion</option>
                    <option value="customer">Customer</option>
                    <option value="support">Customer Support</option>
                  </select>
                </label>
                <label className="text-sm text-zinc-400">
                  Quantity
                  <input type="number" min="1" max="100" value={tokenQuantity} onChange={(e) => setTokenQuantity(e.target.value)} className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-3 text-white" />
                </label>
                <label className="text-sm text-zinc-400">
                  Uses Per Token
                  <input type="number" min="1" max="100" value={tokenUses} onChange={(e) => setTokenUses(e.target.value)} className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-3 text-white" />
                </label>
                <label className="text-sm text-zinc-400">
                  Assigned Email (needed for current button)
                  <input type="email" value={tokenEmail} onChange={(e) => setTokenEmail(e.target.value)} placeholder="tester@example.com" className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-3 text-white placeholder-zinc-600" />
                </label>
                <label className="text-sm text-zinc-400">
                  Expiration (optional)
                  <input type="datetime-local" value={tokenExpiry} onChange={(e) => setTokenExpiry(e.target.value)} className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-3 text-white" />
                </label>
                <label className="text-sm text-zinc-400">
                  Notes (optional)
                  <input type="text" value={tokenNotes} onChange={(e) => setTokenNotes(e.target.value)} placeholder="Beta test, YouTube giveaway..." className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-3 text-white placeholder-zinc-600" />
                </label>
              </div>
              <button
                onClick={handleGenerateTokens}
                disabled={isGeneratingTokens || Number(tokenQuantity) < 1}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-green-600 px-5 py-3 font-black text-white hover:bg-green-500 disabled:opacity-50 sm:w-auto"
              >
                {isGeneratingTokens ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Ticket className="w-5 h-5" />}
                {isGeneratingTokens ? 'Generating...' : 'Generate Tokens'}
              </button>
            </div>

            {tokenStatus.message && (
              <div className={`mb-5 rounded-lg p-3 text-sm ${tokenStatus.type === 'success' ? 'bg-green-500/15 text-green-300' : 'bg-red-500/15 text-red-300'}`}>
                {tokenStatus.message}
              </div>
            )}

            <div className="overflow-x-auto rounded-xl border border-zinc-800">
              <table className="w-full min-w-[760px] text-sm">
                <thead className="bg-zinc-800 text-zinc-400">
                  <tr>
                    <th className="px-3 py-3 text-left">Token</th>
                    <th className="px-3 py-3 text-left">Type</th>
                    <th className="px-3 py-3 text-left">Email</th>
                    <th className="px-3 py-3 text-center">Uses</th>
                    <th className="px-3 py-3 text-left">Status</th>
                    <th className="px-3 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {tabTokens.length === 0 ? (
                    <tr><td colSpan="6" className="px-4 py-8 text-center text-zinc-500">No tokens generated yet.</td></tr>
                  ) : tabTokens.map((token) => {
                    const expired = token.expiresAt && new Date(token.expiresAt) <= new Date();
                    const status = !token.active ? 'Disabled' : expired ? 'Expired' : token.usesRemaining <= 0 ? 'Used' : 'Active';
                    return (
                      <tr key={token._id} className="border-t border-zinc-800">
                        <td className="px-3 py-3 font-mono font-bold text-green-300">{token.code}</td>
                        <td className="px-3 py-3 capitalize text-zinc-300">{token.type}</td>
                        <td className="px-3 py-3 text-zinc-400">{token.assignedEmail || 'Not assigned'}</td>
                        <td className="px-3 py-3 text-center text-white">{token.usesRemaining}/{token.usesAllowed}</td>
                        <td className="px-3 py-3"><span className={`rounded-full px-2 py-1 text-xs font-bold ${status === 'Active' ? 'bg-green-500/15 text-green-300' : status === 'Used' ? 'bg-blue-500/15 text-blue-300' : 'bg-red-500/15 text-red-300'}`}>{status}</span></td>
                        <td className="px-3 py-3">
                          <div className="flex justify-end gap-2">
                            <button onClick={() => navigator.clipboard.writeText(token.code)} title="Copy token" className="rounded-lg bg-zinc-800 p-2 text-zinc-300 hover:text-white"><Copy className="w-4 h-4" /></button>
                            <button onClick={() => handleTokenAction(token._id, 'toggle', !token.active)} className="rounded-lg bg-zinc-800 px-3 py-2 text-xs font-bold text-zinc-300 hover:text-white">{token.active ? 'Disable' : 'Enable'}</button>
                            <button onClick={() => confirm('Delete this token permanently?') && handleTokenAction(token._id, 'delete')} className="rounded-lg bg-red-500/10 p-2 text-red-400 hover:bg-red-500/20"><Trash2 className="w-4 h-4" /></button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* DadRock Tabs Quickies Sync */}
"""
if ui_marker not in text:
    raise SystemExit('Token UI insertion marker not found')
text = text.replace(ui_marker, ui_block, 1)

path.write_text(text)

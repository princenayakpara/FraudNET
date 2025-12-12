import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function App() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [distribution, setDistribution] = useState([]);

  // Dummy initial transactions
  useEffect(() => {
    const seed = [
      { id: 1, amount: 1200, device_trust: "high", country: "India", home_country: "India", hour: 14, final_score: 15 },
      { id: 2, amount: 76000, device_trust: "low", country: "USA", home_country: "India", hour: 2, final_score: 85 },
      { id: 3, amount: 4500, device_trust: "medium", country: "India", home_country: "India", hour: 20, final_score: 30 },
      { id: 4, amount: 300000, device_trust: "low", country: "UAE", home_country: "India", hour: 3, final_score: 92 },
    ];
    setTransactions(seed);
    computeDistribution(seed);
  }, []);

  function computeDistribution(list) {
    const bins = [0, 0, 0, 0, 0];
    list.forEach((t) => {
      const s = Math.max(0, Math.min(100, Math.round(t.final_score || 0)));
      if (s <= 20) bins[0]++;
      else if (s <= 40) bins[1]++;
      else if (s <= 60) bins[2]++;
      else if (s <= 80) bins[3]++;
      else bins[4]++;
    });
    setDistribution([
      { name: "0-20", count: bins[0] },
      { name: "21-40", count: bins[1] },
      { name: "41-60", count: bins[2] },
      { name: "61-80", count: bins[3] },
      { name: "81-100", count: bins[4] },
    ]);
  }

  async function sendSampleTransaction() {
    setLoading(true);
    const sample = {
      amount: 60000,
      device_trust: "low",
      country: "USA",
      home_country: "India",
      hour: 2,
    };

    try {
      const res = await fetch("http://127.0.0.1:8000/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sample),
      });

      const data = await res.json();

      const entry = {
        id: Date.now(),
        ...sample,
        rule_score: data.rule_score,
        ml_score: data.ml_score,
        final_score: data.final_score,
      };

      const newList = [entry, ...transactions].slice(0, 50);
      setTransactions(newList);
      computeDistribution(newList);
    } catch (err) {
      console.error(err);
      alert("Backend not running at http://127.0.0.1:8000");
    }

    setLoading(false);
  }

  function riskBadge(score) {
    if (score >= 80)
      return <span className="px-2 py-1 rounded-full text-xs bg-red-600 text-white">High</span>;
    if (score >= 60)
      return <span className="px-2 py-1 rounded-full text-xs bg-orange-500 text-white">Medium-High</span>;
    if (score >= 40)
      return <span className="px-2 py-1 rounded-full text-xs bg-yellow-400 text-black">Medium</span>;
    return <span className="px-2 py-1 rounded-full text-xs bg-green-200 text-black">Low</span>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <header className="max-w-6xl mx-auto mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">FraudNET Dashboard</h1>
            <p className="text-sm text-gray-600">Overview of recent transactions and risk distribution</p>
          </div>

          <button
            onClick={sendSampleTransaction}
            disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg shadow hover:bg-indigo-700 disabled:opacity-60"
          >
            {loading ? "Sending..." : "Send Sample Transaction"}
          </button>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="p-4 bg-white rounded-lg shadow">
            <div className="text-sm text-gray-500">Total Transactions</div>
            <div className="text-2xl font-semibold">{transactions.length}</div>
          </div>

          <div className="p-4 bg-white rounded-lg shadow">
            <div className="text-sm text-gray-500">High Risk (≥80)</div>
            <div className="text-2xl font-semibold">
              {transactions.filter((t) => t.final_score >= 80).length}
            </div>
          </div>

          <div className="p-4 bg-white rounded-lg shadow">
            <div className="text-sm text-gray-500">Average Score</div>
            <div className="text-2xl font-semibold">
              {(
                transactions.reduce((s, t) => s + (t.final_score || 0), 0) /
                Math.max(1, transactions.length)
              ).toFixed(1)}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-3 gap-6">
        <section className="col-span-2 bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-3">Recent Transactions</h2>

          <div className="overflow-auto">
            <table className="w-full text-sm table-auto">
              <thead className="text-left text-gray-500 border-b">
                <tr>
                  <th className="py-2">ID</th>
                  <th>Amount</th>
                  <th>Device</th>
                  <th>Location</th>
                  <th>Hour</th>
                  <th>Score</th>
                  <th>Risk</th>
                </tr>
              </thead>

              <tbody>
                {transactions.map((t) => (
                  <tr key={t.id} className="border-b hover:bg-gray-50">
                    <td className="py-2">{t.id}</td>
                    <td>₹{t.amount.toLocaleString()}</td>
                    <td className="capitalize">{t.device_trust}</td>
                    <td>{t.country}</td>
                    <td>{t.hour}</td>
                    <td>{(t.final_score || 0).toFixed(1)}</td>
                    <td>{riskBadge(t.final_score || 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-3">Score Distribution</h2>

          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={distribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#6366F1" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <p className="mt-4 text-sm text-gray-600">
            Click <strong>Send Sample Transaction</strong> to test your backend.
          </p>
        </aside>
      </main>
    </div>
  );
}

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { format } from "date-fns";

const API = "http://localhost:8000";

export default function Dashboard() {
    const [calls, setCalls] = useState([]);
    const [stats, setStats] = useState({ total_calls: 0, today: 0 });
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000); // Refresh every 10 seconds
        return () => clearInterval(interval);
    }, []);

    async function fetchData() {
        try {
            const [callsRes, statsRes] = await Promise.all([
                axios.get(`${API}/calls/`),
                axios.get(`${API}/calls/stats/summary`),
            ]);
            setCalls(callsRes.data);
            setStats(statsRes.data);
        } catch (err) {
            console.error("Failed to fetch data:", err);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div style={{ minHeight: "100vh", background: "#f0f2f5" }}>
            {/* Header */}
            <div style={{
                background: "#1a1a2e",
                color: "white",
                padding: "1rem 2rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
            }}>
                <div>
                    <h1 style={{ fontSize: "1.4rem", fontWeight: 600 }}>
                        🤖 Receptionist AI
                    </h1>
                    <p style={{ fontSize: "0.8rem", opacity: 0.6, marginTop: "2px" }}>
                        Admin Dashboard
                    </p>
                </div>
                <button
                    onClick={fetchData}
                    style={{
                        background: "#16213e",
                        color: "white",
                        border: "1px solid rgba(255,255,255,0.2)",
                        padding: "0.4rem 1rem",
                        borderRadius: "6px",
                        cursor: "pointer",
                        fontSize: "0.85rem",
                    }}
                >
                    ↻ Refresh
                </button>
            </div>

            <div style={{ padding: "2rem", maxWidth: "1100px", margin: "0 auto" }}>
                {/* Stats cards */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem", marginBottom: "2rem" }}>
                    <StatCard label="Total Calls" value={stats.total_calls} color="#4361ee" />
                    <StatCard label="Calls Today" value={stats.today} color="#7209b7" />
                    <StatCard label="Status" value="🟢 Live" color="#2d6a4f" />
                </div>

                {/* Calls table */}
                <div style={{
                    background: "white",
                    borderRadius: "12px",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                    overflow: "hidden",
                }}>
                    <div style={{
                        padding: "1rem 1.5rem",
                        borderBottom: "1px solid #f0f0f0",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                    }}>
                        <h2 style={{ fontSize: "1rem", fontWeight: 600 }}>Recent Calls</h2>
                        <span style={{ fontSize: "0.8rem", color: "#888" }}>
                            {calls.length} records
                        </span>
                    </div>

                    {loading ? (
                        <div style={{ padding: "3rem", textAlign: "center", color: "#888" }}>
                            Loading calls...
                        </div>
                    ) : calls.length === 0 ? (
                        <div style={{ padding: "3rem", textAlign: "center", color: "#888" }}>
                            No calls yet — make a test call to your Twilio number!
                        </div>
                    ) : (
                        <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                                <tr style={{ background: "#f8f9fa", fontSize: "0.8rem", color: "#666" }}>
                                    <th style={th}>Caller</th>
                                    <th style={th}>Last Message</th>
                                    <th style={th}>AI Reply</th>
                                    <th style={th}>Time</th>
                                    <th style={th}>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {calls.map((call, i) => (
                                    <tr
                                        key={call.call_sid}
                                        style={{
                                            borderTop: "1px solid #f0f0f0",
                                            background: i % 2 === 0 ? "white" : "#fafafa",
                                        }}
                                    >
                                        <td style={td}>
                                            <span style={{
                                                background: "#e8f4fd",
                                                color: "#1a6eb5",
                                                padding: "3px 8px",
                                                borderRadius: "20px",
                                                fontSize: "0.8rem",
                                                fontWeight: 500,
                                            }}>
                                                {call.caller || "Unknown"}
                                            </span>
                                        </td>
                                        <td style={{ ...td, maxWidth: "220px" }}>
                                            <span style={{
                                                display: "block",
                                                overflow: "hidden",
                                                textOverflow: "ellipsis",
                                                whiteSpace: "nowrap",
                                                fontSize: "0.85rem",
                                            }}>
                                                {call.transcript || "—"}
                                            </span>
                                        </td>
                                        <td style={{ ...td, maxWidth: "220px" }}>
                                            <span style={{
                                                display: "block",
                                                overflow: "hidden",
                                                textOverflow: "ellipsis",
                                                whiteSpace: "nowrap",
                                                fontSize: "0.85rem",
                                                color: "#555",
                                            }}>
                                                {call.ai_reply || "—"}
                                            </span>
                                        </td>
                                        <td style={{ ...td, whiteSpace: "nowrap", fontSize: "0.8rem", color: "#888" }}>
                                            {call.created_at
                                                ? format(new Date(call.created_at), "MMM d, h:mm a")
                                                : "—"}
                                        </td>
                                        <td style={td}>
                                            <button
                                                onClick={() => navigate(`/calls/${call.call_sid}`)}
                                                style={{
                                                    background: "#4361ee",
                                                    color: "white",
                                                    border: "none",
                                                    padding: "4px 12px",
                                                    borderRadius: "6px",
                                                    cursor: "pointer",
                                                    fontSize: "0.8rem",
                                                }}
                                            >
                                                View
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}

function StatCard({ label, value, color }) {
    return (
        <div style={{
            background: "white",
            borderRadius: "12px",
            padding: "1.25rem 1.5rem",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            borderLeft: `4px solid ${color}`,
        }}>
            <p style={{ fontSize: "0.8rem", color: "#888", marginBottom: "6px" }}>{label}</p>
            <p style={{ fontSize: "1.8rem", fontWeight: 700, color }}>{value}</p>
        </div>
    );
}

const th = {
    padding: "0.75rem 1.5rem",
    textAlign: "left",
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
};

const td = {
    padding: "0.85rem 1.5rem",
};
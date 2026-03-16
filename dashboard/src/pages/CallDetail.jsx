import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { format } from "date-fns";

const API = "http://localhost:8000";

export default function CallDetail() {
    const { callSid } = useParams();
    const navigate = useNavigate();
    const [call, setCall] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios
            .get(`${API}/calls/${callSid}`)
            .then((res) => setCall(res.data))
            .catch((err) => console.error(err))
            .finally(() => setLoading(false));
    }, [callSid]);

    return (
        <div style={{ minHeight: "100vh", background: "#f0f2f5" }}>
            {/* Header */}
            <div style={{
                background: "#1a1a2e",
                color: "white",
                padding: "1rem 2rem",
                display: "flex",
                alignItems: "center",
                gap: "1rem",
            }}>
                <button
                    onClick={() => navigate("/")}
                    style={{
                        background: "transparent",
                        color: "white",
                        border: "1px solid rgba(255,255,255,0.3)",
                        padding: "0.4rem 1rem",
                        borderRadius: "6px",
                        cursor: "pointer",
                        fontSize: "0.85rem",
                    }}
                >
                    ← Back
                </button>
                <div>
                    <h1 style={{ fontSize: "1.2rem", fontWeight: 600 }}>Call Detail</h1>
                    <p style={{ fontSize: "0.75rem", opacity: 0.5 }}>{callSid}</p>
                </div>
            </div>

            <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
                {loading ? (
                    <div style={{ textAlign: "center", padding: "3rem", color: "#888" }}>
                        Loading...
                    </div>
                ) : !call ? (
                    <div style={{ textAlign: "center", padding: "3rem", color: "#888" }}>
                        Call not found.
                    </div>
                ) : (
                    <>
                        {/* Call info card */}
                        <div style={{
                            background: "white",
                            borderRadius: "12px",
                            padding: "1.5rem",
                            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                            marginBottom: "1.5rem",
                            display: "grid",
                            gridTemplateColumns: "1fr 1fr",
                            gap: "1rem",
                        }}>
                            <InfoRow label="Caller" value={call.caller || "Unknown"} />
                            <InfoRow
                                label="Time"
                                value={call.created_at
                                    ? format(new Date(call.created_at), "MMM d yyyy, h:mm a")
                                    : "—"}
                            />
                            <InfoRow
                                label="Duration"
                                value={call.duration_seconds ? `${call.duration_seconds}s` : "—"}
                            />
                            <InfoRow label="Call SID" value={callSid.slice(0, 20) + "..."} />
                        </div>

                        {/* Transcript card */}
                        <div style={{
                            background: "white",
                            borderRadius: "12px",
                            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                            overflow: "hidden",
                            marginBottom: "1.5rem",
                        }}>
                            <div style={{
                                padding: "1rem 1.5rem",
                                borderBottom: "1px solid #f0f0f0",
                                fontWeight: 600,
                                fontSize: "0.95rem",
                            }}>
                                📞 Caller said
                            </div>
                            <div style={{
                                padding: "1.5rem",
                                fontSize: "0.95rem",
                                lineHeight: 1.7,
                                color: "#333",
                            }}>
                                {call.transcript || "No transcript available."}
                            </div>
                        </div>

                        {/* AI reply card */}
                        <div style={{
                            background: "white",
                            borderRadius: "12px",
                            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                            overflow: "hidden",
                        }}>
                            <div style={{
                                padding: "1rem 1.5rem",
                                borderBottom: "1px solid #f0f0f0",
                                fontWeight: 600,
                                fontSize: "0.95rem",
                            }}>
                                🤖 AI replied
                            </div>
                            <div style={{
                                padding: "1.5rem",
                                fontSize: "0.95rem",
                                lineHeight: 1.7,
                                color: "#333",
                                background: "#f8f9ff",
                            }}>
                                {call.ai_reply || "No reply recorded."}
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

function InfoRow({ label, value }) {
    return (
        <div>
            <p style={{ fontSize: "0.75rem", color: "#888", marginBottom: "4px" }}>
                {label}
            </p>
            <p style={{ fontSize: "0.9rem", fontWeight: 500 }}>{value}</p>
        </div>
    );
}
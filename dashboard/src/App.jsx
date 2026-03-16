import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CallDetail from "./pages/CallDetail";

export default function App() {
    return (
        <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/calls/:callSid" element={<CallDetail />} />
        </Routes>
    );
}
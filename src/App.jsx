import { BrowserRouter, Routes, Route } from "react-router-dom";
import AnimatedBackground from "./components/AnimatedBackground";
import LandingPage        from "./pages/LandingPage";
import Navbar             from "./components/Navbar";
import Dashboard          from "./pages/Dashboard";
import Analytics          from "./pages/Analytics";
import Security           from "./pages/Security";
import VehicleDetail      from "./pages/VehicleDetail";

function MainLayout() {
  return (
    <div style={{ minHeight: "100vh", background: "#020810", position: "relative" }}>
      <AnimatedBackground />
      <div style={{ position: "relative", zIndex: 1 }}>
        <Navbar />
        <Routes>
          <Route path="/"            element={<Dashboard />}     />
          <Route path="/analytics"   element={<Analytics />}     />
          <Route path="/security"    element={<Security />}      />
          <Route path="/vehicle/:id" element={<VehicleDetail />} />
        </Routes>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/landing" element={<LandingPage />} />
        <Route path="*"        element={<MainLayout />}  />
      </Routes>
    </BrowserRouter>
  );
}
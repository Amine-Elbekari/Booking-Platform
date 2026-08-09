import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { GoogleOAuthProvider } from "@react-oauth/google";

import Login from "./pages/Login";
import Register from "./pages/Register";
import CompleteProfile from "./pages/CompleteProfile";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID
// This is the public landing page
function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center bg-gray-50">
      <h1 className="mb-4 text-4xl font-bold text-gray-800">Premium Villa Booking</h1>
      <div className="space-x-4">
        <Link to="/login" className="text-lg text-blue-600 hover:underline">Log In</Link>
        <Link to="/register" className="text-lg text-blue-600 hover:underline">Create Account</Link>
      </div>
    </div>
  );
}

// This will eventually be your beautiful generated UI!
function Dashboard() {
  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.reload(); // Quick way to reset the app state
  };

  return (
    <div className="min-h-screen p-8 bg-gray-100">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Available Villas</h1>
        <button onClick={handleLogout} className="px-4 py-2 text-white bg-red-500 rounded-md">Log Out</button>
      </div>
      {/* Your generated grid of properties will go here */}
      <p>Welcome to the inside of the application!</p>
    </div>
  );
}

// The smart Home component routes them based on authentication
function Home() {
  const isAuthenticated = !!localStorage.getItem("token");
  return isAuthenticated ? <Dashboard /> : <LandingPage />;
}

export default function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <BrowserRouter>
        <Toaster position="top-center" />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/complete-profile" element={<CompleteProfile />} />
        </Routes>
      </BrowserRouter>
    </GoogleOAuthProvider>
  );
}
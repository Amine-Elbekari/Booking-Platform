import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";
import { GoogleLogin } from "@react-oauth/google";
import { authService } from "../api/authService";

export default function Login() {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);

    const loginPromise = authService.login(email, password);

    toast.promise(loginPromise, {
      loading: 'Logging in...',
      success: 'Welcome back!',
      error: (err) => {
        if (axios.isAxiosError(err) && err.response?.status === 401) {
          return 'Invalid email or password';
        }
        return 'Server error. Please try again.';
      }
    });

    try {
      const data = await loginPromise;
      localStorage.setItem("token", data.access_token);
      
      // Check if they need to complete their profile
      if (data.requires_onboarding) {
        navigate("/complete-profile");
      } else {
        navigate("/");
      }
    } catch(err) {
      // Nothing to do here because toast.promise handled the UI errors
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    setIsLoading(true);
    try {
      const data = await authService.googleLogin(credentialResponse.credential);
      localStorage.setItem("token", data.access_token);
      
      toast.success("Google login successful!");
      
      // Check if they need to complete their profile
      if (data.requires_onboarding) {
        navigate("/complete-profile");
      } else {
        navigate("/");
      }
    } catch (err) {
      toast.error("Google authentication failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-md">
        <h2 className="mb-6 text-3xl font-bold text-center text-gray-800">Sign In</h2>
        
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block mb-1 text-sm font-medium text-gray-600">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
              className="w-full px-4 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block mb-1 text-sm font-medium text-gray-600">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
              className="w-full px-4 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-400"
          >
            {isLoading ? "Signing in..." : "Log In"}
          </button>
        </form>

        {/* --- GOOGLE BUTTON SECTION --- */}
        <div className="mt-6 flex flex-col items-center">
          <div className="flex items-center w-full mb-4">
            <div className="flex-grow border-t border-gray-300"></div>
            <span className="px-3 text-sm text-gray-500">Or continue with</span>
            <div className="flex-grow border-t border-gray-300"></div>
          </div>
          
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => toast.error("Google Login closed or failed")}
          />
        </div>

        {/* --- NAVIGATION TO REGISTER --- */}
        <p className="mt-6 text-sm text-center text-gray-600">
          Don't have an account?{" "}
          <Link to="/register" className="font-semibold text-blue-600 hover:underline">
            Sign up
          </Link>
        </p>

      </div>
    </div>
  );
}
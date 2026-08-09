import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";
import { GoogleLogin } from "@react-oauth/google";
import { authService } from "../api/authService";

export default function Register() {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);

    const registerPromise = authService.register(email, password, firstName, lastName);

    toast.promise(registerPromise, {
      loading: 'Creating account...',
      success: 'Account created!',
      error: 'Failed to create account. Email might be in use.'
    });

    try {
      await registerPromise;
      // Auto-login after manual registration
      const loginData = await authService.login(email, password);
      localStorage.setItem("token", loginData.access_token);
      
      if (loginData.requires_onboarding) {
        navigate("/complete-profile");
      } else {
        navigate("/");
      }
    } catch (err) {
      // Handled by toast
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    setIsLoading(true);
    try {
      const data = await authService.googleLogin(credentialResponse.credential);
      localStorage.setItem("token", data.access_token);
      
      toast.success("Google account connected!");
      
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
        <h2 className="mb-6 text-3xl font-bold text-center text-gray-800">Create Account</h2>
        
        <form onSubmit={handleRegister} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block mb-1 text-sm font-medium text-gray-600">First Name</label>
              <input type="text" required disabled={isLoading} className="w-full px-4 py-2 border rounded-md"
                onChange={(e) => setFirstName(e.target.value)} />
            </div>
            <div>
              <label className="block mb-1 text-sm font-medium text-gray-600">Last Name</label>
              <input type="text" required disabled={isLoading} className="w-full px-4 py-2 border rounded-md"
                onChange={(e) => setLastName(e.target.value)} />
            </div>
          </div>

          <div>
            <label className="block mb-1 text-sm font-medium text-gray-600">Email</label>
            <input type="email" required disabled={isLoading} className="w-full px-4 py-2 border rounded-md"
              onChange={(e) => setEmail(e.target.value)} />
          </div>

          <div>
            <label className="block mb-1 text-sm font-medium text-gray-600">Password</label>
            <input type="password" required disabled={isLoading} className="w-full px-4 py-2 border rounded-md"
              onChange={(e) => setPassword(e.target.value)} />
          </div>

          <button type="submit" disabled={isLoading} className="w-full px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-400">
            {isLoading ? "Creating..." : "Sign Up"}
          </button>
        </form>

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

        <p className="mt-6 text-sm text-center text-gray-600">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-blue-600 hover:underline">
            Log in
          </Link>
        </p>

      </div>
    </div>
  );
}
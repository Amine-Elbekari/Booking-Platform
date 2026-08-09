import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import axios from "axios";
import { authService, type CompleteProfileData } from "../api/authService";
import { getNames } from "country-list";

// get the array of all official country strings dynamically
const COUNTRIES = getNames();

export default function CompleteProfile() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<CompleteProfileData>({
    phone_number: "",
    date_of_birth: "",
    city: "",
    country: "",
    gender: "Male"
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await authService.completeProfile(formData);
      toast.success("Profile completed successfully!");
      navigate("/"); // Send them to the main application!
    } catch (err) {
      if (axios.isAxiosError(err)) {
        toast.error(err.response?.data?.detail || "Validation failed.");
      } else {
        toast.error("Something went wrong.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-md">
        <h2 className="mb-2 text-2xl font-bold text-center text-gray-800">Almost there!</h2>
        <p className="mb-6 text-sm text-center text-gray-600">
          Please complete your profile to continue.
        </p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1 text-sm font-medium text-gray-600">Phone Number</label>
            <input type="tel" required disabled={isLoading} className="w-full px-4 py-2 border rounded-md" placeholder="+212 6..."
              onChange={e => setFormData({...formData, phone_number: e.target.value})} />
          </div>
          
          <div>
            <label className="block mb-1 text-sm font-medium text-gray-600">Date of Birth</label>
            <input type="date" required disabled={isLoading} className="w-full px-4 py-2 border rounded-md"
              onChange={e => setFormData({...formData, date_of_birth: e.target.value})} />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block mb-1 text-sm font-medium text-gray-600">City</label>
              <input type="text" required disabled={isLoading} className="w-full px-4 py-2 border rounded-md" placeholder="Casablanca"
                onChange={e => setFormData({...formData, city: e.target.value})} />
            </div>
            <div>
              <label className="block mb-1 text-sm font-medium text-gray-600">Country</label>
              {/* <input type="text" required disabled={isLoading} className="w-full px-4 py-2 border rounded-md" placeholder="Morocco"
                onChange={e => setFormData({...formData, country: e.target.value})} /> */}
              <select
                required
                disabled={isLoading}
                value={formData.country}
                className="w-full px-4 py-2 border rounded-md bg-white"
                onChange={e => setFormData({ ...formData, 
                  country: e.target.value
                })}>
                  <option value="" disabled>Select your country</option>
                  {COUNTRIES.map((country) => (
                    <option key={country} value={country}>
                      {country}
                    </option>
                  ))}
                </select>
            </div>
          </div>

          <div>
            <label className="block mb-1 text-sm font-medium text-gray-600">Gender</label>
            <select disabled={isLoading} className="w-full px-4 py-2 border rounded-md"
              onChange={e => setFormData({...formData, gender: e.target.value})}>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>

          <button type="submit" disabled={isLoading} className="w-full px-4 py-2 mt-4 text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-400">
            {isLoading ? "Saving..." : "Complete Profile"}
          </button>
        </form>
      </div>
    </div>
  );
}
import apiClient from "./client";

export interface LoginResponse {
    access_token: string;
    token_type: string;
    requires_onboarding: boolean;
}

export interface RegisterData {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  phone_number: string;
  date_of_birth: string;
  gender: string;
  location: string;
}

export interface CompleteProfileData {
    phone_number: string;
    date_of_birth: string;
    city: string;
    country: string;
    gender: string;
}

export const authService = {

    login: async (email: string, password: string): Promise<LoginResponse> => {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);
        const response = await apiClient.post<LoginResponse>("/auth/login", formData, {
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });
        return response.data;
    },

    register: async (userData: RegisterData) => {
        // Send only the required fields; CompleteProfile handles the rest
        const response = await apiClient.post("/users", {
            first_name: userData.first_name,
            last_name:  userData.last_name,
            email:      userData.email,
            password:   userData.password,
        });
        return response.data;
    },

    googleLogin: async (googleToken: string): Promise<LoginResponse> => {
        const response = await apiClient.post<LoginResponse>("/auth/google", { token: googleToken });
        return response.data;
    },

    completeProfile: async (data: CompleteProfileData) => {
        const response = await apiClient.patch("/users/me/complete-profile", data, {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        });
        return response.data;
    },
};
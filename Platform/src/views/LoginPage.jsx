import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./landing.css";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = { email, password };

    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        // Store user data in localStorage
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate("/chat"); // Redirect to main page instead of profile settings
      } else {
        alert(data.error || "Invalid credentials. Please try again.");
      }
    } catch (error) {
      console.error("Error during login:", error);
      alert("An error occurred. Please try again later.");
    }
  };

  return (
    <><div className="log w-screen h-screen flex items-center justify-center bg-gray-100">
      <form
        className="bg-white shadow-md rounded px-8 py-6 w-[90%] md:w-[30rem]"
        onSubmit={handleSubmit}
      >
        <h1 className="text-2xl font-bold text-center mb-6">تسجيل الدخول</h1>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">البريد الإلكتروني</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border rounded"
            required />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">كلمة المرور</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border rounded"
            required />
        </div>
        <button
          type="submit"
          className="w-full bg-[#3D1010] text-white py-2 rounded hover:bg-[#5a1919] transition duration-300"
        >
          تسجيل الدخول
        </button>
        <p
          className="text-center mt-4 text-[#3D1010] underline hover:text-[#5a1919] cursor-pointer"
          onClick={() => navigate("/forgot-password")}
        >
          هل نسيت كلمة المرور؟
        </p>
        <div className="text-center mt-4">
          <button
            className="bg-[#3D1010] text-white py-2 px-4 rounded-lg hover:bg-[#5a1919] transition duration-300"
            onClick={() => navigate("/signup")}
          >
            إنشاء حساب جديد
          </button>
        </div>
      </form>
    </div></>

  );
}

export default LoginPage;

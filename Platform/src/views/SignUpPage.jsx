import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./landing.css";
import { getEducationalStages } from '../utils/educationalStages';

function SignUpPage() {
  const [stages, setStages] = useState([]);
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    studyLevel: "HSS3", // Default option
  });

  useEffect(() => {
    setStages(getEducationalStages());
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    // Prepare data for the backend
    const payload = {
      firstname: formData.fullName,
      email: formData.email,
      password: formData.password,
      educational_level: formData.studyLevel,
    };

    try {
      const response = await fetch("http://localhost:5000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('user', JSON.stringify({
          email: payload.email,
          firstname: payload.firstname,
          educational_level: payload.educational_level
        }));
        navigate('/chat'); // Redirect to main page
      } else {
        alert(data.error || "Failed to sign up. Please try again.");
      }
    } catch (error) {
      console.error("Error during signup:", error);
      alert("An error occurred. Please try again later.");
    }
  };

  return (
    <div className="sign w-screen h-screen flex items-center justify-center bg-gray-100">
      <form
        className="bg-white shadow-md rounded px-8 py-6 w-[90%] md:w-[30rem]"
        onSubmit={handleSubmit}
      >
        <h1 className="text-2xl font-bold text-center mb-6">إنشاء حساب</h1>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">الاسم الكامل</label>
          <input
            type="text"
            name="fullName"
            value={formData.fullName}
            onChange={handleChange}
            className="w-full px-4 py-2 border rounded"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">البريد الإلكتروني</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full px-4 py-2 border rounded"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">كلمة المرور</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="w-full px-4 py-2 border rounded"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">تأكيد كلمة المرور</label>
          <input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            className="w-full px-4 py-2 border rounded"
            required
          />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 mb-2">المستوى الدراسي</label>
          <select
            name="studyLevel"
            value={formData.studyLevel}
            onChange={handleChange}
            className="w-full px-4 py-2 border rounded"
            required
          >
            {stages.map(stage => (
              <option key={stage.code} value={stage.code}>
                {stage.name}
              </option>
            ))}
          </select>
        </div>
        <button
          type="submit"
          className="w-full bg-[#3D1010] text-white py-2 rounded hover:bg-[#5a1919] transition duration-300"
        >
          إنشاء حساب
        </button>
      </form>
    </div>
  );
}

export default SignUpPage;

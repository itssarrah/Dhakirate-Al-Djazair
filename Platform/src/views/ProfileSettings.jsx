import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "./landing.css";
import { getEducationalStages } from '../utils/educationalStages';
import Toast from "../components/Toast";

function ProfileSettings() {
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    studyLevel: "",
  });
  const [stages, setStages] = useState([]);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const navigate = useNavigate();

  useEffect(() => {
    setStages(getEducationalStages());
    const userData = localStorage.getItem('user');
    if (!userData) {
      navigate('/login');
      return;
    }

    const user = JSON.parse(userData);
    setFormData({
      fullName: user.firstname || "",
      email: user.email || "",
      studyLevel: user.educational_level || "HSS3",
    });
  }, [navigate]);

  const handleSave = async () => {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData) {
      navigate('/login');
      return;
    }

    const payload = {
      email: userData.email,
      firstname: formData.fullName,
      educational_level: formData.studyLevel,
    };

    try {
      const response = await fetch("http://localhost:5000/update_profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        const updatedUser = {
          ...userData,
          firstname: formData.fullName,
          educational_level: formData.studyLevel
        };
        localStorage.setItem('user', JSON.stringify(updatedUser));

        setToast({
          show: true,
          message: "تم تحديث الملف الشخصي",
          type: 'success'
        });

        // If educational level changed, navigate to Ikhtibar
        if (userData.educational_level !== formData.studyLevel) {
          setTimeout(() => {
            navigate('/ikhtibar');
          }, 1500);
        } else {
          // Force sidebar refresh by triggering a window event
          window.dispatchEvent(new Event('userDataUpdated'));
        }
      } else {
        setToast({
          show: true,
          message: data.error || "Failed to update profile",
          type: 'error'
        });
      }
    } catch (error) {
      console.error("Error updating profile:", error);
      setToast({
        show: true,
        message: "An error occurred. Please try again later.",
        type: 'error'
      });
    }
  };

  return (
    <div className="chat flex h-screen">
      {toast.show && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast({ ...toast, show: false })}
        />
      )}
      <Sidebar />

      {/* Profile Settings Section */}
      <div className="flex-1 flex flex-col items-center justify-center space-y-6 p-6">
        <h2 className="text-3xl font-bold mb-6">إعدادات الحساب</h2>
        <div className="flex flex-col space-y-4 w-full max-w-[50vw]">
          <input
            type="text"
            value={formData.fullName}
            onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
            placeholder="الاسم الكامل"
            className="p-3 rounded-lg border border-gray-300"
          />
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="البريد الإلكتروني"
            className="p-3 rounded-lg border border-gray-300"
          />
          <select
            value={formData.studyLevel}
            onChange={(e) => setFormData({ ...formData, studyLevel: e.target.value })}
            className="p-3 rounded-lg border border-gray-300"
          >
            {stages.map(stage => (
              <option key={stage.code} value={stage.code}>
                {stage.name}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={handleSave}
          className="px-6 py-3 bg-[#3D1010] text-white rounded-lg hover:bg-[#5a1919] transition duration-300"
        >
          حفظ التغييرات
        </button>
      </div>
    </div>
  );
}

export default ProfileSettings;

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "./landing.css";

function LoadingState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center h-screen bg-[#00000010]">
      <div className="text-[#3F1515] text-2xl font-bold mb-4">جاري تحميل الدروس...</div>
      <div className="flex space-x-2">
        <div className="w-3 h-3 bg-[#3F1515] rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-3 h-3 bg-[#3F1515] rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-3 h-3 bg-[#3F1515] rounded-full animate-bounce"></div>
      </div>
    </div>
  );
}

function NoLessonsState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center h-screen">
      <img src="/doros.svg" alt="No Lessons" className="w-24 h-24 mb-4 opacity-50" />
      <div className="text-[#3F1515] text-2xl font-bold text-center">
        لا توجد دروس متاحة في هذه المرحلة
      </div>
      <div className="text-[#3F1515] text-lg mt-2 opacity-75 text-center">
        سيتم إضافة دروس جديدة قريباً
      </div>
    </div>
  );
}

function Doros() {
  const navigate = useNavigate();
  const [topics, setTopics] = useState([]);
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (!storedUser) {
      navigate('/login');
      return;
    }
    setUserData(JSON.parse(storedUser));
  }, [navigate]);

  useEffect(() => {
    const fetchTopics = async () => {
      if (!userData) return;

      try {
        const response = await fetch(
          `http://localhost:5000/topics?educational_stage=${userData.educational_level}`
        );
        if (!response.ok) {
          throw new Error('Failed to fetch topics');
        }
        const data = await response.json();
        setTopics(data.topics || []);
      } catch (error) {
        console.error("Error fetching topics:", error);
        setTopics([]);
      }
    };

    fetchTopics();
  }, [userData]);

  if (!userData) {
    return (
      <div className="chat flex h-screen">
        <Sidebar />
        <LoadingState />
      </div>
    );
  }

  if (topics.length === 0) {
    return (
      <div className="chat flex h-screen">
        <Sidebar />
        <NoLessonsState />
      </div>
    );
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="chat flex-1 p-8 flex flex-col items-center overflow-auto">
        <h1 className="text-4xl font-bold mb-12 text-center">الدروس التعليمية</h1>
        <div className="flex flex-col items-center w-[90%] max-w-4xl space-y-6 overflow-y-auto max-h-[calc(100vh-8rem)] custom-scrollbar">
          {topics.map((topic, index) => (
            <div
              key={index}
              className={`group w-[90%] p-6 text-center cursor-pointer rounded-xl shadow-md transition-all duration-300 ${index % 2 === 0
                ? "bg-[#C08250] hover:bg-[#a9743e]"
                : "bg-[#4e3b31] hover:bg-[#3b2c26]"
                }`}
              onClick={() => navigate(`/topic/${encodeURIComponent(topic.title)}`)}
            >
              <div className="text-2xl font-bold text-white line-clamp-2 group-hover:line-clamp-none transition-all duration-300">
                {topic.title}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Doros;

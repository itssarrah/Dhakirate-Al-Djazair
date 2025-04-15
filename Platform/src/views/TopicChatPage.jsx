import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Chat from "../components/Chat";
import Sidebar from "../components/Sidebar";

function LoadingState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center h-screen bg-[#00000010]">
      <div className="text-[#3F1515] text-2xl font-bold mb-4">جاري التحميل...</div>
      <div className="flex space-x-2">
        <div className="w-3 h-3 bg-[#3F1515] rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-3 h-3 bg-[#3F1515] rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-3 h-3 bg-[#3F1515] rounded-full animate-bounce"></div>
      </div>
    </div>
  );
}

function TopicChatPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [topic, setTopic] = useState(null);
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
    const fetchTopicDetails = async () => {
      if (!userData) return;

      try {
        const response = await fetch(
          `http://localhost:5000/topic-content?educational_stage=${userData.educational_level}&topic=${encodeURIComponent(id)}`
        );
        const data = await response.json();
        setTopic(data);
      } catch (error) {
        console.error("Error fetching topic details:", error);
      }
    };

    fetchTopicDetails();
  }, [id, userData]);

  if (!topic) {
    return (
      <div className="chat flex h-screen">
        <Sidebar />
        <LoadingState />
      </div>
    );
  }

  return (
    <div className="chat flex h-screen">
      <Sidebar />
      <div className="flex-1">
        {/* Fixed header section with back button */}
        <div className="h-24 flex items-center justify-center">
          <button
            onClick={() => navigate(`/topic/${encodeURIComponent(id)}`)}
            className="bg-[#3F1515] hover:bg-[#2a0f0f] text-white px-6 py-3 rounded-lg flex items-center gap-2 transition-colors"
          >
            <span className="text-lg">العودة إلى الدرس</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              className="w-5 h-5 transform rotate-90"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
        </div>

        {/* Chat section */}
        <div className="flex-1 flex items-center justify-center">
          <Chat topic={topic.title} topicTitle={topic.title} />
        </div>
      </div>
    </div>
  );
}

export default TopicChatPage;

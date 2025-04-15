import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Chat from "../components/Chat";
import "./landing.css";

function ChatScreen() {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedSession, setSelectedSession] = useState(null);

  useEffect(() => {
    // Check for authenticated user
    const userData = localStorage.getItem('user');
    if (!userData) {
      navigate('/login');
      return;
    }

    // Make user data available to Chat component
    const user = JSON.parse(userData);
    // You could pass this as props to Chat if needed
    window.chatUserData = {
      email: user.email,
      educational_level: user.educational_level
    };
  }, [navigate]);

  const handleSessionSelect = (session) => {
    console.log("[ChatScreen] Session selected:", session);
    setSelectedSession(session);
    if (location.pathname !== '/chat') {
      navigate('/chat');
    }
  };

  // Add debug effect
  useEffect(() => {
    console.log("[ChatScreen] Current selected session:", selectedSession);
  }, [selectedSession]);

  return (
    <div className="chat flex h-screen overflow-hidden">
      <Sidebar onSessionSelect={handleSessionSelect} currentSession={selectedSession} />
      <div className="flex-1 flex items-center justify-center p-4">
        <Chat
          session={selectedSession}
          key={selectedSession?.session_nonce || 'new'}
        />
      </div>
    </div>
  );
}

export default ChatScreen;
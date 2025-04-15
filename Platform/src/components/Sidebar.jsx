import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

function Sidebar({ onSessionSelect, currentSession }) {
  const [user, setUser] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [sessions, setSessions] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const loadUserData = () => {
      const userData = localStorage.getItem("user");
      if (userData) {
        setUser(JSON.parse(userData));
      } else {
        navigate("/login");
      }
    };

    loadUserData();

    // Add listener for profile updates
    window.addEventListener('userDataUpdated', loadUserData);

    return () => {
      window.removeEventListener('userDataUpdated', loadUserData);
    };
  }, [navigate]);

  // Add debounced refresh function
  const refreshSessions = useCallback(async () => {
    const userData = localStorage.getItem("user");
    if (userData) {
      const user = JSON.parse(userData);
      try {
        const response = await fetch(`http://localhost:5000/sessions?email=${user.email}`);
        if (response.ok) {
          const data = await response.json();
          // Only update if there are actually changes
          const newSessions = data.sessions.sort((a, b) =>
            new Date(b.last_activity) - new Date(a.last_activity)
          );
          
          // Compare with current sessions
          const hasChanges = JSON.stringify(newSessions) !== JSON.stringify(sessions);
          if (hasChanges) {
            setSessions(newSessions);
          }
        }
      } catch (error) {
        console.error("Error loading sessions:", error);
      }
    }
  }, [sessions]);

  // Initial load of sessions
  useEffect(() => {
    refreshSessions();
  }, [refreshSessions]);

  // Set up periodic refresh with longer interval
  useEffect(() => {
    // Refresh every 30 seconds instead of 5
    const intervalId = setInterval(refreshSessions, 30000);
    
    // Add event listener for window focus
    const handleFocus = () => {
      refreshSessions();
    };
    
    window.addEventListener('focus', handleFocus);
    
    return () => {
      clearInterval(intervalId);
      window.removeEventListener('focus', handleFocus);
    };
  }, [refreshSessions]);

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  const handleNavigation = (path) => navigate(path);

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ar-DZ', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const handleSessionClick = (session) => {
    console.log("Sidebar: Clicking session", session);
    navigate('/chat'); // Navigate first
    
    // Short timeout to ensure we're on chat page before triggering selection
    setTimeout(() => {
      if (typeof onSessionSelect === 'function') {
        console.log("Sidebar: Triggering session select", session);
        onSessionSelect(session);
        setIsChatOpen(false);
      } else {
        console.error("onSessionSelect not available - current location:", window.location.pathname);
      }
    }, 100);
  };

  return (
    <div
      className="w-64 bg-[#78553F] text-white p-4 flex flex-col drop-shadow-lg rounded-r-xl"
      style={{
        transform: window.innerWidth <= 1280 ? "scale(0.8)" : "scale(1)",
      }}
    >
      <div className="mb-12 mt-6">
        <div className="flex flex-col items-center space-y-3 relative">
          {/* Add settings icon in top-right corner of profile section */}
          <div
            className="absolute top-0 right-0 p-2 cursor-pointer hover:bg-[#3F1515] rounded-full transition-all duration-300"
            onClick={() => navigate("/profilesettings")}
          >
            <img
              src="/settings.svg"
              alt="Settings"
              className="w-6 h-6 hover:rotate-90 transition-transform duration-300 invert"
            />
          </div>

          <img
            src="/username.png"
            alt="User"
            className="rounded-full cursor-pointer"
            onClick={() => navigate("/profilesettings")}
          />
          <p className="text-xl">{user?.firstname || "User"}</p>
          <span className="text-gray-700 bg-white/60 px-4 py-1 rounded-full">
            {user?.educational_level || "Loading..."}
          </span>
        </div>
      </div>
      <hr />
      <ul className="flex-col space-y-8 mt-12 text-4xl h-fit mb-8">
        <li
          className="flex flex-row-reverse items-center cursor-pointer hover:underline"
          onClick={() => handleNavigation("/doros")}
        >
          <img src="/doros.svg" alt="Doros" className="ml-12 w-8 h-8" />
          <span>دروس</span>
        </li>
        <li
          className="flex flex-row-reverse items-center cursor-pointer hover:underline"
          onClick={() => handleNavigation("/ikhtibar")}
        >
          <img src="/ikhtibar.svg" alt="Ikhtibar" className="ml-12 w-8 h-8" />
          <span>اختبارات</span>
        </li>
        <li
          className="flex flex-row-reverse items-center cursor-pointer hover:underline"
          onClick={() => handleNavigation("/taqarir")}
        >
          <img src="/taqarir.svg" alt="Taqarir" className="ml-12 w-8 h-8" />
          <span>تقارير</span>
        </li>
      </ul>
      <hr />
      <div className="mt-8">
        <div
          className={`flex items-center justify-around px-4 py-4 drop-shadow-sm cursor-pointer transition-all duration-300 ease-in-out ${isChatOpen
            ? "bg-[#3F1515] py-6 rounded-t-3xl"
            : "rounded-3xl bg-[#3F1515]"
            }`}
          onClick={toggleChat}
          dir='rtl' >
          <img
            src="/chevron.svg"
            alt="Chevron"
            className={`w-5 h-5 transform transition-transform duration-300 ease-in-out ${isChatOpen ? "rotate-180" : ""
              }`}
          />
          <h3 className="text-lg font-bold mb-2">ذاكرة</h3>
          <img src="/chat.svg" alt="Chat" className="w-8 h-8" />
        </div>

        <div
          className={`overflow-hidden transition-all duration-500 ease-in-out bg-[#3F1515] ${isChatOpen ? "max-h-[400px]" : "max-h-0"
            }`}
          dir='rtl' >
          <ul className="p-2 rounded-lg space-y-2 max-h-[350px] overflow-y-auto custom-scrollbar">
            <li className={`p-2 rounded-xl cursor-pointer hover:bg-[#DF9B6B] ${
                !currentSession ? 'bg-[#DF9B6B]' : 'bg-[rgba(223,155,107,0.15)]'
              }`}
              onClick={() => handleSessionClick(null)}>
              محادثة جديدة
            </li>
            {sessions.map((session) => (
              <li
                key={session.session_nonce} // Use session_nonce as key instead of index
                className={`p-2 rounded-xl cursor-pointer hover:bg-[#DF9B6B] ${
                  currentSession?.session_nonce === session.session_nonce 
                    ? 'bg-[#DF9B6B]' 
                    : 'bg-[rgba(223,155,107,0.15)]'
                }`}
                onClick={() => handleSessionClick(session)}
              >
                <div className="text-sm">
                  <div>{session.first_question}</div>
                  <div className="text-xs text-gray-300 mt-1">
                    {formatDate(session.created_at)} • {session.questions_count} رسائل
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="flex items-center justify-center mt-4 cursor-pointer hover:opacity-75"
          onClick={handleLogout}>
          <button className="w-full rounded transition-all duration-300 ease-in-out text-gray-300 hover:text-red-700">
            تسجيل الخروج
          </button>
          <img src="/logout.svg" alt="Logout" className="w-8 h-8" />
        </div>
      </div>
    </div>
  );
}

export default Sidebar;

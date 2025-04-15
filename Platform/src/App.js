import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ChatScreen from "./views/ChatScreen";
import LandingPage from "./views/LandingPage";
import LoginPage from "./views/LoginPage";
import SignUpPage from "./views/SignUpPage";
import ProfileSettings from "./views/ProfileSettings";

import Ikhtibar from "./views/Ikhtibar";
import Quiz1 from "./components/Quiz1";
import Quiz2 from "./components/Quiz2";
import Quiz3 from "./components/Quiz3";
import Doros from "./views/Doros";
import Molakhas from "./views/Molakhas";
import Taqarir from "./views/Taqarir";
import Quiz1Levels from "./components/Quiz1Levels";
import TopicPage from "./views/TopicPage";
import TopicChatPage from "./views/TopicChatPage";

function App() {
  return (
    <>
      <Router>
        <Routes>
          {/* Define the ChatScreen route */}
          <Route path="/chat" element={<ChatScreen />} />
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/profilesettings" element={<ProfileSettings />} />
          <Route path="/ikhtibar" element={<Ikhtibar />} />
          <Route path="/quiz1" element={<Quiz1 />} />
          <Route path="/quiz1levels" element={<Quiz1Levels />} />
          <Route path="/quiz2" element={<Quiz2 />} />
          <Route path="/quiz3" element={<Quiz3 />} />
          <Route path="/doros" element={<Doros />} />
          <Route path="/molakhas" element={<Molakhas />} />
          <Route path="/taqarir" element={<Taqarir />} />
          <Route path="/topic/:id" element={<TopicPage />} />
          <Route path="/topicchat/:id" element={<TopicChatPage />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;

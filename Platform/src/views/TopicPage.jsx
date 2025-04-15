import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Sidebar from "../components/Sidebar";
import "./landing.css";

function LoadingState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center h-screen bg-[#00000010]">
      <div className="text-[#3F1515] text-2xl font-bold mb-4">جاري تحميل الدرس...</div>
      <div className="flex space-x-2">
        <div className="w-3 h-3 bg-[#3F1515] rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-3 h-3 bg-[#3F1515] rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-3 h-3 bg-[#3F1515] rounded-full animate-bounce"></div>
      </div>
    </div>
  );
}

function TopicPage() {
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
    const fetchTopicContent = async () => {
      if (!userData) return;

      try {
        const response = await fetch(
          `http://localhost:5000/topic-content?educational_stage=${userData.educational_level}&topic=${encodeURIComponent(id)}`
        );
        const data = await response.json();
        setTopic(data);
      } catch (error) {
        console.error("Error fetching topic content:", error);
      }
    };

    fetchTopicContent();
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
      <div className="flex-1 flex flex-col relative">
        <div className="flex-1 px-8 pt-8 pb-24">
          <h1 className="text-4xl font-bold mb-8 text-center text-[#3F1515]">{topic?.title}</h1>
          <div
            className="w-full mx-auto overflow-auto custom-scrollbar prose prose-lg rtl px-8
              prose-headings:text-[#3F1515] 
              prose-headings:font-bold 
              prose-h2:text-3xl 
              prose-h3:text-2xl
              prose-p:text-right
              prose-p:text-xl
              prose-p:text-black
              prose-strong:text-black 
              prose-blockquote:text-black
              prose-blockquote:border-[#3F1515]
              prose-ul:text-right
              prose-ul:text-black
              prose-ol:text-right
              prose-ol:text-black
              prose-li:text-black
              prose-li:text-right
              max-w-none" /* Remove max-width constraint */
            style={{ maxHeight: "calc(100vh - 16rem)" }}
            dir="rtl"
          >
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h2: ({ node, ...props }) => <h2 className="text-3xl font-bold mt-8 mb-4 text-right text-[#3F1515]" {...props} />,
                h3: ({ node, ...props }) => <h3 className="text-2xl font-bold mt-6 mb-3 text-right text-[#3F1515]" {...props} />,
                blockquote: ({ node, ...props }) => (
                  <blockquote className="border-r-4 border-[#3F1515] pr-4 my-4 italic text-right text-black" {...props} />
                ),
                ul: ({ node, ...props }) => <ul className="list-disc pr-5 my-4 text-right text-black" {...props} />,
                ol: ({ node, ...props }) => <ol className="list-decimal pr-5 my-4 text-right text-black" {...props} />,
                p: ({ node, ...props }) => <p className="my-4 leading-relaxed text-right text-black text-xl" {...props} />,
                li: ({ node, ...props }) => <li className="text-right mb-2 text-black" {...props} />
              }}
            >
              {topic?.content}
            </ReactMarkdown>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-8 flex justify-center">
          <button
            onClick={() => navigate(`/topicchat/${encodeURIComponent(id)}`)}
            className="px-10 py-4 text-xl font-bold bg-[#3F1515] text-white rounded-lg hover:bg-[#2a0f0f] transition-colors"
          >
            ذاكرة
          </button>
        </div>
      </div>
    </div>
  );
}

export default TopicPage;

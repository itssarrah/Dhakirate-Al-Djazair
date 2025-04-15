import React, { useState, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";

function Chat({
  session = null,
  topic = false,
  topicTitle = "مرحبًا بك في ذاكرة: دعنا نستكشف تاريخ الجزائر معًا!",
}) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isFirstMessageSent, setIsFirstMessageSent] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState(null);
  const [sessionNonce, setSessionNonce] = useState(null);
  const [userData, setUserData] = useState(null);
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUserData(JSON.parse(storedUser));
    }
  }, []);

  useEffect(() => {


    const loadContent = async () => {
      if (session && userData) {
        setSessionNonce(session.session_nonce);
        setIsFirstMessageSent(true);

        try {
          const response = await fetch(
            `http://localhost:5000/session-content?email=${userData.email}&session_nonce=${session.session_nonce}`
          );


          if (response.ok) {
            const data = await response.json();

            if (data.content && Array.isArray(data.content)) {
              const formattedMessages = [];

              // Process messages in pairs to maintain conversation flow
              data.content.forEach((msg) => {
                // Add user message if it exists
                if (msg.question) {
                  formattedMessages.push({
                    id: Date.now() + Math.random(),
                    sender: "user",
                    text: msg.question
                  });
                }

                // Add bot message if it exists
                if (msg.answer) {
                  formattedMessages.push({
                    id: Date.now() + Math.random(),
                    sender: "bot",
                    text: msg.answer
                  });
                }
              });

              setMessages(formattedMessages);

              // Scroll to bottom
              setTimeout(() => {
                const chatDiv = document.querySelector('.custom-scrollbar');
                if (chatDiv) {
                  chatDiv.scrollTop = chatDiv.scrollHeight;
                }
              }, 100);
            }
          }
        } catch (error) {
          console.error("[Chat] Error loading session:", error);
        }
      } else {
        setSessionNonce(null);
        setMessages([]);
        setIsFirstMessageSent(false);
      }
    };

    loadContent();
  }, [session, userData]);

  const streamBotMessage = (fullText) => {
    setIsStreaming(true); // Disable user input while streaming
    setStreamingText(""); // Reset streaming text
    let index = 0;

    const messageId = Date.now(); // Unique ID for each streaming message
    setStreamingMessageId(messageId);

    const interval = setInterval(() => {
      if (index < fullText.length) {
        setStreamingText((prev) => prev + fullText[index]);
        index++;
      } else {
        clearInterval(interval);

        setMessages((prevMessages) => {
          const filteredMessages = prevMessages.filter(
            (msg) => msg.id !== messageId
          );
          return [
            ...filteredMessages,
            { id: messageId, sender: "bot", text: fullText },
          ];
        });

        setIsStreaming(false);
        setStreamingText("");
      }
    }, 30); // 50ms delay for each character
  };

  const handleAddMessage = (sender, text) => {
    const isDuplicate = messages.some((msg) => msg.text === text);
    if (!isDuplicate) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { id: Date.now(), sender, text },
      ]);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isStreaming || !userData || isWaitingForResponse) return;

    const userMessage = input;
    handleAddMessage("user", userMessage);
    setInput(""); // Clear input immediately
    setIsFirstMessageSent(true);
    setIsWaitingForResponse(true); // Start loading

    try {
      const response = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: userData.email,
          question: userMessage,
          educational_stage: userData.educational_level,
          historical_era: null,
          session_nonce: sessionNonce,
          topic: topic || null,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.session_nonce) {
          setSessionNonce(data.session_nonce);
        }
        const botMessage = data.answer || "عذراً، حدث خطأ في معالجة طلبك.";
        streamBotMessage(botMessage);
      } else {
        throw new Error("Failed to fetch response");
      }
    } catch (error) {
      console.error("Error:", error);
      handleAddMessage("bot", "عذراً، حدث خطأ في معالجة طلبك.");
      setIsStreaming(false);
    } finally {
      setIsWaitingForResponse(false); // Stop loading
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !isStreaming) {
      handleSend();
    }
  };

  return (
    <div className="w-[85%] bg-[#3F1515] rounded-xl shadow-lg h-[90vh] flex flex-col rtl" dir='rtl'>
      <div className={`flex flex-col h-full ${!isFirstMessageSent ? 'justify-center' : ''}`}>
        {/* Title section - fixed at top when messages present */}
        <div className={`transition-all duration-300 ease-in-out 
          ${isFirstMessageSent ? 'py-4' : 'py-8'}`}>
          {!isFirstMessageSent && (
            <img
              src="/chatlogo.png"
              alt="logo"
              className="w-24 h-24 mx-auto mb-4"
            />
          )}
          <h1 className={`font-bold text-center text-white transition-all duration-300 ease-in-out 
            ${isFirstMessageSent ? 'text-2xl md:text-3xl' : 'text-5xl md:text-6xl'}`}>
            {topicTitle}
          </h1>
        </div>

        {/* Messages section - flexible height */}
        <div className={`flex-1 overflow-y-auto p-4 transition-all duration-300 ease-in-out custom-scrollbar
          ${isFirstMessageSent ? 'opacity-100' : 'opacity-0 hidden'}`}>
          {messages.map((message, index) => (
            <div key={index} className="mb-4 flex items-start justify-end" >
              {message.sender === "user" ? (
                // User's message with profile picture
                <div className="flex flex-row-reverse items-start" >
                  <img
                    src="/username.png"
                    alt="User"
                    className="w-12 h-12 rounded-full border-2 border-gray-300 ml-4"
                  />
                  <div className="bg-gray-300 text-black font-jost text-lg rounded-lg py-2 px-8 max-w-[90%] text-right" dir='rtl'>
                    {message.text}
                  </div>
                </div>
              ) : (
                // Bot's message
                <div className="text-right text-white bg-[rgba(223,155,107,0.15)] mt-8 w-[95%] p-2 rounded-lg text-xl" dir="rtl">
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                </div>
              )}
            </div>
          ))}

          {streamingText && (
            <div className="text-right text-white bg-[rgba(223,155,107,0.15)] mt-8 w-[95%] p-2 rounded-lg text-xl">
              <ReactMarkdown>{streamingText}</ReactMarkdown>
            </div>
          )}

          {isWaitingForResponse && (
            <div className="text-right text-white bg-[rgba(223,155,107,0.15)] mt-8 w-[95%] p-2 rounded-lg text-xl" dir="rtl">
              <div className="flex items-center justify-start gap-2">
                <div className="animate-bounce">.</div>
                <div className="animate-bounce animation-delay-200">.</div>
                <div className="animate-bounce animation-delay-400">.</div>
              </div>
            </div>
          )}
        </div>

        {/* Input section - fixed at bottom */}
        <div className={`p-4 transition-all duration-300 ease-in-out
          ${isFirstMessageSent ? 'opacity-100 bottom-1' : 'opacity-50 top-0'}`}>
          <div className="flex bg-[rgba(200,181,181,0.58)] rounded-3xl mx-auto max-w-4xl">
            {!isStreaming && !isWaitingForResponse && (
              <button
                onClick={handleSend}
                className="bg-transparent text-white flex items-center pl-4"
              >
                <img src="/send.svg" alt="Send" className="w-12 h-12" />
              </button>
            )}
            <input
              type="text"
              placeholder="... اكتب هنا "
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className={`flex-grow py-6 text-gray-300 text-xl bg-transparent pr-8 outline-none text-right
                ${isStreaming || isWaitingForResponse ? "cursor-not-allowed" : ""}`}
              disabled={isStreaming || isWaitingForResponse}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chat;

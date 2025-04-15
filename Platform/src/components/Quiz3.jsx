import React, { useState, useEffect } from "react";
import { useDrag, useDrop, DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { ClipLoader } from "react-spinners";
import Sidebar from "../components/Sidebar";
import "../styles/quiz3.css";
import "../views/landing.css";
import { useNavigate } from "react-router-dom";

function Quiz3() {
  const [personalities, setPersonalities] = useState([]);
  const [descriptions, setDescriptions] = useState([]);
  const [placedCharacters, setPlacedCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (!storedUser) {
      navigate('/login');
      return;
    }
    setUserData(JSON.parse(storedUser));
  }, [navigate]);

  useEffect(() => {
    const fetchQuiz = async () => {
      if (!userData) return;

      try {
        const response = await fetch(
          "http://localhost:5000/personality/quiz/generate",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: userData.email,
              educational_stage: userData.educational_level,
              num_questions: 4,
            }),
          }
        );

        const data = await response.json();
        if (response.ok) {
          setPersonalities(data.quiz.personalities);
          setDescriptions(data.quiz.descriptions);
          setPlacedCharacters(
            new Array(data.quiz.descriptions.length).fill(null)
          );
        } else {
          setError(data.error);
        }
      } catch (err) {
        setError("Failed to fetch quiz");
      } finally {
        setLoading(false);
      }
    };

    fetchQuiz();
  }, [userData]);

  const handleDrop = (targetIndex, draggedCharacter) => {
    const newPlacedCharacters = [...placedCharacters];
    const existingIndex = newPlacedCharacters.findIndex(
      (char) => char && char.id === draggedCharacter.id
    );
    if (existingIndex !== -1) {
      newPlacedCharacters[existingIndex] = null;
    }
    newPlacedCharacters[targetIndex] = draggedCharacter;
    setPlacedCharacters(newPlacedCharacters);
  };

  const handleClear = (index) => {
    const newPlacedCharacters = [...placedCharacters];
    newPlacedCharacters[index] = null;
    setPlacedCharacters(newPlacedCharacters);
  };

  const handleSubmit = async () => {
    if (!userData || quizSubmitted) {
      window.location.reload(); // Refresh the page to retake the quiz
      return;
    }
    const matches = placedCharacters
      .map((char, index) => {
        if (!char) return null;
        return {
          personality_id: char.id,
          description_id: descriptions[index].id,
          personality_name: char.name,
          description: descriptions[index].text,
          image_link: char.image_link,
        };
      })
      .filter((match) => match !== null);

    try {
      const response = await fetch(
        "http://localhost:5000/personality/quiz/submit",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: userData.email,
            educational_stage: userData.educational_level,
            matches,
          }),
        }
      );

      const data = await response.json();
      if (response.ok) {
        const results = data.results;

        const updatedCharacters = placedCharacters.map((char, index) => {
          if (!char) return char;
          const isCorrect = results[index]?.correct;
          return { ...char, isCorrect };
        });

        setPlacedCharacters(updatedCharacters);
        setQuizSubmitted(true); // Mark the quiz as submitted
      } else {
        alert("حدث خطأ أثناء إرسال الإجابات");
      }
    } catch (err) {
      alert("حدث خطأ في الاتصال بالخادم");
    }
  };

  const getScale = () => {
    const width = window.innerWidth;
    if (width <= 1024) return 0.6;
    if (width <= 1280) return 0.8;
    return 1;
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="chat flex h-screen">
        <Sidebar />
        <div className={`flex-1 p-8 flex flex-col items-center ${loading ? "justify-center" : ""}`}>
          {loading ? (
            <div className="flex flex-col items-center justify-center">
              <ClipLoader color="#FFF" size={100} />
              <p className="mt-4 text-lg font-semibold">جاري التحميل...</p>
            </div>
          ) : error ? (
            <div className="text-red-500 text-lg">{error}</div>
          ) : (
            <div style={{
              transform: `scale(${getScale()})`,
              transformOrigin: 'top center',
              width: '100%',
              minHeight: '100vh'
            }}>
              <h1 className="text-3xl font-bold mb-20 text-center">
                اختبار الشخصيات التاريخية
              </h1>

              <div className="characters-container mb-20">
                {personalities.map((personality) => (
                  <DraggableCharacter
                    key={personality.id}
                    character={{
                      id: personality.id,
                      name: personality.name,
                      image: personality.image_link,
                    }}
                    isPlaced={placedCharacters.some(
                      (char) => char && char.id === personality.id
                    )}
                  />
                ))}
              </div>

              <div className="placeholders-container">
                {descriptions.map((description, index) => (
                  <DropTarget
                    key={description.id}
                    index={index}
                    onDrop={handleDrop}
                  >
                    <div
                      className={`placeholder-parent flex flex-col items-center space-y-2 shadow-2xl ${placedCharacters[index]?.isCorrect === true
                        ? "correct "
                        : placedCharacters[index]?.isCorrect === false
                          ? "incorrect"
                          : ""
                        }`}
                    >
                      <div className="placeholder mt-8">
                        {placedCharacters[index] && (
                          <div
                            className={`placed-character w-[100px] h-[100px] `}
                          >
                            <img
                              src={placedCharacters[index].image}
                              alt={placedCharacters[index].name}
                            />
                          </div>
                        )}
                      </div>
                      <p className="font-bold">{description.text}</p>
                      {!quizSubmitted && placedCharacters[index] && (
                        <button
                          className="bg-red-500 text-white py-2 px-4 mt-2 rounded-lg"
                          onClick={() => handleClear(index)}
                        >
                          مسح
                        </button>
                      )}
                    </div>
                  </DropTarget>
                ))}
              </div>

              <div className="flex justify-center">
                <button
                  className="bg-[#C08250] text-white py-3 px-6 rounded-lg mt-48"
                  onClick={handleSubmit}
                  disabled={
                    !quizSubmitted &&
                    placedCharacters.some((char) => char === null)
                  }
                >
                  {quizSubmitted ? "إعادة الاختبار" : "تحقق"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </DndProvider>
  );
}

function DraggableCharacter({ character, isPlaced }) {
  const [{ isDragging }, drag] = useDrag({
    type: "character",
    item: character,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  return (
    <div
      ref={drag}
      className={`character ${isDragging ? "dragging" : ""} ${isPlaced ? "opacity-50" : ""
        }`}
    >
      <img src={character.image} alt={character.name} />
      <p>{character.name}</p>
    </div>
  );
}

function DropTarget({ children, index, onDrop }) {
  const [{ isOver }, drop] = useDrop({
    accept: "character",
    drop: (item) => onDrop(index, item),
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  });

  return (
    <div ref={drop} className={`drop-target ${isOver ? "bg-green-100" : ""}`}>
      {children}
    </div>
  );
}

export default Quiz3;

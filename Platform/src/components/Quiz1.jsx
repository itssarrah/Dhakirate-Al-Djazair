import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import "../views/landing.css";
import { useNavigate, useLocation } from "react-router-dom";

function Quiz1() {
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [answeredQuestions, setAnsweredQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [userData, setUserData] = useState(null);
  const [quizResults, setQuizResults] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [quizKey, setQuizKey] = useState(0); // Add this new state
  const [autoAdvanceProgress, setAutoAdvanceProgress] = useState(100);
  const AUTO_ADVANCE_DELAY = 2000; // 2 seconds delay

  const navigate = useNavigate();
  const location = useLocation();
  const selectedLevel = location.state?.level || 1; // Default to level 1 if not passed

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
        setQuestions([]); // Clear questions while loading
        console.log(selectedLevel);
        const response = await fetch("http://localhost:5000/quiz/generate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: userData.email,
            educational_stage: userData.educational_level,
            level: selectedLevel, // Use the selected level here
            num_questions: 5,
            use_cache: false,
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to fetch quiz data");
        }

        const data = await response.json();
        console.log(data);
        const formattedQuestions = data.quiz.map((q) => ({
          id: q.id,
          question: q.question,
          options: q.answers.map((answer) => answer.optionLabel),
          correct: q.answers.find((answer) => answer.isCorrect === 1)
            ?.optionLabel,
          answers: q.answers,
        }));
        setQuestions(formattedQuestions);
      } catch (error) {
        console.error("Error fetching quiz:", error);
      }
    };

    fetchQuiz();
  }, [selectedLevel, userData, quizKey]); // Add quizKey as dependency

  const handleAnswer = (selectedOption, selectedIndex) => {
    const currentQuestion = questions[currentQuestionIndex];
    if (!answeredQuestions.includes(currentQuestionIndex)) {
      setAnsweredQuestions((prev) => [...prev, currentQuestionIndex]);

      // Save the answer for submission
      setAnswers((prevAnswers) => ({
        ...prevAnswers,
        [currentQuestion.id]: selectedIndex,
      }));

      if (selectedOption === currentQuestion.correct) {
        setScore((prevScore) => prevScore + 1);
        setFeedback("إجابة صحيحة! 🎉");
      } else {
        setFeedback("إجابة خاطئة. 😢");
      }

      // Reset and start the progress bar
      setAutoAdvanceProgress(100);
      const startTime = Date.now();

      const progressInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const remaining = Math.max(0, 100 * (1 - elapsed / AUTO_ADVANCE_DELAY));
        setAutoAdvanceProgress(remaining);
      }, 16); // Update roughly every frame

      // Check if this was the last question
      if (currentQuestionIndex === questions.length - 1) {
        setTimeout(() => {
          clearInterval(progressInterval);
          setQuizCompleted(true);
          submitQuiz();
        }, AUTO_ADVANCE_DELAY);
      } else {
        // If not the last question, go to next question after a short delay
        setTimeout(() => {
          clearInterval(progressInterval);
          setCurrentQuestionIndex(prev => prev + 1);
          setFeedback("");
          setAutoAdvanceProgress(100);
        }, AUTO_ADVANCE_DELAY);
      }
    }
  };

  // Remove the auto-submission from goToNextQuestion
  const goToNextQuestion = () => {
    if (currentQuestionIndex + 1 < questions.length) {
      setCurrentQuestionIndex((prevIndex) => prevIndex + 1);
      setFeedback("");
    } else {
      setQuizCompleted(true);
    }
  };

  // Add this new helper function
  const areAllQuestionsAnswered = () => {
    return questions.length > 0 &&
      Object.keys(answers).length === questions.length;
  };

  const submitQuiz = async () => {
    if (!userData || isSubmitting) return;
    setIsSubmitting(true);

    const formattedAnswers = {};
    Object.entries(answers).forEach(([questionId, selectedOptionIndex]) => {
      formattedAnswers[parseInt(questionId)] = selectedOptionIndex;
    });

    const payload = {
      email: userData.email,
      educational_stage: userData.educational_level,
      level: selectedLevel,
      answers: formattedAnswers,
      quiz_data: questions.map((q) => ({
        id: q.id,
        question: q.question,
        answers: q.answers,
      })),
    };

    try {
      const response = await fetch("http://localhost:5000/quiz/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error("Failed to submit quiz");

      const data = await response.json();
      setQuizResults(data);
    } catch (error) {
      console.error("Error submitting quiz:", error);
      alert("حدث خطأ أثناء إرسال الإجابات");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetake = () => {
    setCurrentQuestionIndex(0);
    setScore(0);
    setQuizCompleted(false);
    setFeedback("");
    setAnsweredQuestions([]);
    setAnswers({});
    setQuizResults(null);
    setQuizKey(prev => prev + 1); // This will trigger a new quiz fetch
  };

  const CompletionScreen = () => (
    <div className="text-center max-w-[60vw]">
      <h1 className="text-3xl font-bold text-green-600 mb-6">
        شكراً لإكمال الاختبار! 🎉
      </h1>

      {!areAllQuestionsAnswered() ? (
        <div className="bg-white p-6 rounded-lg shadow-lg mb-8 rtl" dir="rtl">
          <h2 className="text-2xl font-bold mb-4 text-yellow-600">تنبيه</h2>
          <p className="mb-4">يجب الإجابة على جميع الأسئلة قبل تقديم الاختبار.</p>
          <button
            className="bg-[#78553F] text-white px-6 py-3 rounded-lg hover:bg-[#C08250] transition"
            onClick={() => {
              setQuizCompleted(false);
              setCurrentQuestionIndex(
                questions.findIndex(
                  (_, index) => !answeredQuestions.includes(index)
                )
              );
            }}
          >
            العودة للأسئلة غير المجابة
          </button>
        </div>
      ) : isSubmitting ? (
        <div className="bg-white p-6 rounded-lg shadow-lg mb-8 rtl" dir="rtl">
          <h2 className="text-2xl font-bold mb-4">جاري معالجة النتائج...</h2>
          <div className="flex justify-center items-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#78553F]"></div>
          </div>
        </div>
      ) : quizResults ? (
        <>
          <div className="bg-white p-6 rounded-lg shadow-lg mb-8 rtl" dir="rtl">
            <h2 className="text-2xl font-bold mb-4">النتائج</h2>
            <div className="flex justify-between items-center mb-4">
              <span>الإجابات الصحيحة:</span>
              <span className="text-green-600 font-bold">{quizResults.summary.correct_answers}</span>
            </div>
            <div className="flex justify-between items-center mb-6">
              <span>الدقة:</span>
              <span className="font-bold">{Math.round(quizResults.summary.accuracy)}%</span>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <h3 className="text-lg font-bold mb-2">تقدم المستوى {selectedLevel}</h3>
              <div className="bg-gray-200 rounded-full h-4 overflow-hidden">
                <div
                  className="h-full bg-yellow-500 transition-all duration-500"
                  style={{ width: `${quizResults.level_progress || 0}%` }}
                ></div>
              </div>
              <span className="text-sm mt-1">{quizResults.level_progress || 0}%</span>
            </div>
          </div>

          <div className="flex justify-center space-x-4">
            <button
              className="bg-[#78553F] text-white px-6 py-3 rounded-lg hover:bg-[#C08250] transition"
              onClick={handleRetake}
            >
              إعادة الاختبار
            </button>
            <button
              className="bg-[#3F1515] text-white px-6 py-3 rounded-lg hover:bg-[#5a1919] transition"
              onClick={() => navigate('/quiz1levels')}
            >
              العودة للمستويات
            </button>
          </div>
        </>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow-lg mb-8 rtl" dir="rtl">
          <h2 className="text-xl font-bold mb-4">هل أنت مستعد لتقديم الاختبار؟</h2>
          <button
            onClick={submitQuiz}
            className="bg-[#78553F] text-white px-6 py-3 rounded-lg hover:bg-[#C08250] transition mt-4"
          >
            تقديم الاختبار
          </button>
        </div>
      )}
    </div>
  );

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="chat flex-1 flex flex-col items-center justify-center p-8">
        {questions.length === 0 ? (
          <p>جاري تحميل الأسئلة...</p>
        ) : !quizCompleted ? (
          <div className="max-w-[60vw] w-full text-center">
            <h1 className="text-3xl font-bold mb-4">
              اختبار 1: أسئلة متعددة الخيارات
            </h1>
            <p className="text-lg mb-4">
              السؤال {currentQuestionIndex + 1} من {questions.length}
            </p>

            {/* Question */}
            <div className="bg-[#DF9B6B] text-white p-6 rounded-lg mb-6">
              <h2 className="text-2xl">
                {questions[currentQuestionIndex].question}
              </h2>
            </div>

            {/* Options */}
            <div className="space-y-4">
              {questions[currentQuestionIndex].options.map((option, index) => (
                <button
                  key={index}
                  className={`w-full py-3 rounded-lg transition ${answeredQuestions.includes(currentQuestionIndex)
                    ? option === questions[currentQuestionIndex].correct
                      ? "bg-green-500 text-white"
                      : "bg-gray-300 text-gray-600 cursor-not-allowed"
                    : "bg-[#78553F] text-white hover:bg-[#C08250]"
                    }`}
                  onClick={() => handleAnswer(option, index)}
                  disabled={answeredQuestions.includes(currentQuestionIndex)}
                >
                  {option}
                </button>
              ))}
            </div>

            {/* Add the auto-advance progress bar */}
            {feedback && (
              <div className="relative w-full h-1 bg-gray-200 mt-4">
                <div
                  className="absolute top-0 left-0 h-full bg-[#78553F] transition-all duration-[16ms] ease-linear"
                  style={{ width: `${autoAdvanceProgress}%` }}
                />
              </div>
            )}

            {/* Feedback */}
            {feedback && (
              <div
                className={`mt-2 text-lg font-semibold ${feedback.includes("صحيحة") ? "text-green-600" : "text-red-600"
                  }`}
              >
                {feedback}
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="mt-8 flex justify-between">
              <button
                className="bg-gray-400 text-white px-4 py-2 rounded-lg hover:bg-gray-500 transition disabled:opacity-50"
                onClick={() => setCurrentQuestionIndex((prev) => prev - 1)}
                disabled={currentQuestionIndex === 0}
              >
                السابق
              </button>
              <button
                className="bg-[#78553F] text-white px-4 py-2 rounded-lg hover:bg-[#C08250] transition"
                onClick={goToNextQuestion}
              >
                التالي
              </button>
            </div>
          </div>
        ) : (
          <CompletionScreen />
        )}
      </div>
    </div>
  );
}

export default Quiz1;

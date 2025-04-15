import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Toast from "../components/Toast";
import { getNextStage, isHighSchoolChoice, getStageNameForDisplay } from "../utils/educationalStages";
import "../views/landing.css";

const StageAdvanceModal = ({ isOpen, onClose, currentStage, onConfirm, nextStages }) => {
  if (!isOpen) return null;

  const isHighSchool = Array.isArray(nextStages);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <h2 className="text-2xl font-bold mb-4 text-center text-[#3F1515]">ترقية المرحلة التعليمية</h2>
        <p className="text-lg mb-6 text-center">
          {`أنت على وشك الانتقال من ${getStageNameForDisplay(currentStage)}`}
        </p>

        {isHighSchool ? (
          <div className="space-y-4">
            <p className="text-center mb-4">اختر المسار الدراسي:</p>
            <div className="flex flex-col gap-3">
              <button
                onClick={() => onConfirm(nextStages[0])}
                className="bg-[#3F1515] hover:bg-[#190808] text-white py-3 px-6 rounded-lg transition-all"
              >
                {getStageNameForDisplay(nextStages[0])}
              </button>
              <button
                onClick={() => onConfirm(nextStages[1])}
                className="bg-[#78553F] hover:bg-[#C08250] text-white py-3 px-6 rounded-lg transition-all"
              >
                {getStageNameForDisplay(nextStages[1])}
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            <button
              onClick={() => onConfirm(nextStages)}
              className="bg-[#3F1515] hover:bg-[#190808] text-white py-3 px-6 rounded-lg transition-all"
            >
              {`الانتقال إلى ${getStageNameForDisplay(nextStages)}`}
            </button>
          </div>
        )}

        <button
          onClick={onClose}
          className="mt-4 w-full border-2 border-[#3F1515] text-[#3F1515] py-2 px-6 rounded-lg hover:bg-gray-100 transition-all"
        >
          إلغاء
        </button>
      </div>
    </div>
  );
};

const Quiz1Levels = () => {
  const [progressData, setProgressData] = useState([
    { level: 1, progress: 0 },
    { level: 2, progress: 0 },
    { level: 3, progress: 0 },
  ]);
  const [userData, setUserData] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      navigate("/login");
      return;
    }
    setUserData(JSON.parse(storedUser));
  }, [navigate]);

  useEffect(() => {
    const fetchProgressData = async () => {
      if (!userData) return;

      try {
        const response = await fetch(
          `http://localhost:5000/quiz/progress?email=${userData.email}&educational_stage=${userData.educational_level}`
        );
        const data = await response.json();

        const transformedData = Object.entries(data.progress).map(
          ([level, levelData]) => ({
            level: parseInt(level),
            progress: levelData.progress,
            masteryScore: levelData.mastery_score,
            totalCorrect: levelData.total_correct,
            questionsAttempted: levelData.questions_attempted
          })
        );

        setProgressData(transformedData);
      } catch (error) {
        console.error("Error fetching progress data:", error);
      }
    };

    fetchProgressData();
  }, [userData]);

  const isLevelLocked = (level) => {
    if (level === 1) return false;
    const previousLevel = progressData.find((item) => item.level === level - 1);
    return previousLevel?.progress < 80;
  };

  const handleCardClick = (level) => {
    if (isLevelLocked(level)) return;
    navigate(`/quiz1`, { state: { level } });
  };

  const handleStageAdvance = async (nextStage) => {
    try {
      const payload = {
        email: userData.email,
        firstname: userData.firstname,
        educational_level: nextStage,
      };

      const response = await fetch("http://localhost:5000/update_profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        setShowModal(false);
        const updatedUser = { ...userData, educational_level: nextStage };
        localStorage.setItem("user", JSON.stringify(updatedUser));
        setToast({
          show: true,
          message: `تم الانتقال إلى ${getStageNameForDisplay(nextStage)}`,
          type: 'success'
        });
        setTimeout(() => navigate(0), 1500); // Give time for toast to be seen
      } else {
        setToast({
          show: true,
          message: "لم يتم تحديث المرحلة التعليمية",
          type: 'error'
        });
      }
    } catch (error) {
      console.error("Error advancing educational stage:", error);
      setToast({
        show: true,
        message: "حدث خطأ في النظام",
        type: 'error'
      });
    }
  };

  const allLevelsComplete = progressData.every((item) => item.progress >= 80);

  return (
    <div className="flex h-screen">
      {toast.show && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast({ ...toast, show: false })}
        />
      )}
      <Sidebar />
      <div className="chat flex-1 flex flex-col items-center justify-center p-8">
        <h1 className="text-3xl font-bold mb-8 text-center">اختيار المستوى</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {progressData.map((item) => {
            const locked = isLevelLocked(item.level);
            const isComplete = item.progress === 100;
            return (
              <div
                key={item.level}
                className={`card-container rounded-lg shadow-lg p-4 text-center relative ${locked ? "opacity-60" : ""
                  }`}
                onClick={() => handleCardClick(item.level)}
                style={{
                  cursor: locked ? "not-allowed" : "pointer",
                  border: `8px solid ${locked ? "#666" : isComplete ? "#4CAF50" : "#3F1515"}`,
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                {locked ? (
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex flex-col items-center justify-center z-10">
                    <div className="text-white text-xl mb-2">🔒</div>
                    <p className="text-white text-lg px-4">
                      أكمل المستوى {item.level - 1} بنسبة 80٪ لفتح هذا المستوى
                    </p>
                  </div>
                ) : isComplete && (
                  <div className="absolute top-2 right-2 left-2 bg-green-100 rounded-lg p-2 z-10">
                    <p className="text-green-700 text-sm mb-1">
                      يمكنك الحصول على أسئلة جديدة للتدرب أكثر! 🎯
                    </p>
                    <div className="flex justify-between text-xs text-green-600">
                      <span>نقاط الإتقان: {item.masteryScore}</span>
                      <span>إجابات صحيحة: {item.totalCorrect}</span>
                    </div>
                  </div>
                )}

                <img
                  src="/card.png"
                  alt={`Level ${item.level}`}
                  className={`w-full rounded-md mb-4 ${locked ? "filter grayscale" : ""
                    }`}
                />
                <h2 className="text-2xl font-bold mb-10">
                  المستوى {item.level}
                </h2>
                <div className="progress-bar bg-gray-300 rounded-full h-4 overflow-hidden">
                  <div
                    className={`h-full ${locked ? "bg-gray-500" : isComplete ? "bg-green-500" : "bg-yellow-500"
                      }`}
                    style={{ width: `${item.progress}%` }}
                  ></div>
                </div>
                <p className="mt-4 text-2xl text-jost">{item.progress}%</p>
                {isComplete && (
                  <div className="mt-2 text-sm text-gray-600">
                    <div className="flex justify-between items-center">
                      <span>محاولات:</span>
                      <span>{item.questionsAttempted}</span>
                    </div>
                    <div className="flex justify-between items-center text-green-600">
                      <span>معدل النجاح:</span>
                      <span>{Math.round((item.totalCorrect / item.questionsAttempted) * 100)}%</span>
                    </div>
                  </div>
                )}
                <button
                  className={`${locked
                    ? "bg-gray-500 cursor-not-allowed"
                    : isComplete
                      ? "bg-green-600 hover:bg-green-700"
                      : "bg-[#78553F] hover:bg-[#C08250]"
                    } text-white mt-4 px-8 py-2 rounded-lg`}
                  disabled={locked}
                >
                  {locked ? "مقفل" : isComplete ? `تدرب أكثر (${item.masteryScore})` : "اختبر"}
                </button>
              </div>
            );
          })}
        </div>
        {allLevelsComplete && (
          <button
            onClick={() => setShowModal(true)}
            className="bg-[#3F1515] hover:bg-[#190808] text-white mt-12 px-10 py-4 rounded-lg transition-all ease-in-out duration-500"
          >
            الانتقال إلى المرحلة التعليمية التالية
          </button>
        )}
      </div>
      <StageAdvanceModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        currentStage={userData?.educational_level}
        nextStages={getNextStage(userData?.educational_level)}
        onConfirm={handleStageAdvance}
      />
    </div>
  );
};

export default Quiz1Levels;

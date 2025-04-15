import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEducationalStages } from '../utils/educationalStages';
import Sidebar from "../components/Sidebar";
import "./landing.css";

function Ikhtibar() {
  const navigate = useNavigate();
  const [hasExtendedQuizzes, setHasExtendedQuizzes] = useState(false);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const user = JSON.parse(userData);
      const stages = getEducationalStages();
      const userStage = stages.find(s => s.code === user.educational_level);
      setHasExtendedQuizzes(userStage?.hasExtendedQuizzes || false);
    }
  }, []);

  const quizzes = [
    { title: "اختبار 1: أسئلة متعددة الخيارات", route: "/quiz1levels" },
    ...(hasExtendedQuizzes ? [
      { title: "اختبار 2: حدث وتاريخ", route: "/quiz2" },
      { title: "اختبار 3: شخصيات تاريخية", route: "/quiz3" },
    ] : [])
  ];

  return (
    <div className="chat flex h-screen">
      <Sidebar />
      <div className="flex-1 flex items-center justify-center ">
        <div className="flex flex-col items-center w-full max-w-[50vw]">
          <h1 className="text-4xl font-bold mb-8">اختبارات</h1>
          <div className="grid grid-cols-1 gap-6 w-full">
            {quizzes.map((quiz, index) => (
              <div
                key={index}
                className="p-6 bg-[#78553F] rounded-lg cursor-pointer hover:bg-[#C08250] text-center "
                onClick={() => navigate(quiz.route)}
              >
                <h2 className="text-2xl font-semibold text-white">
                  {quiz.title}
                </h2>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Ikhtibar;

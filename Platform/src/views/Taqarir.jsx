import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { getStageNameForDisplay } from "../utils/educationalStages";
import "./landing.css";

function Taqarir() {
  const navigate = useNavigate();
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const userData = JSON.parse(localStorage.getItem('user'));
        if (!userData) {
          navigate('/login');
          return;
        }

        const response = await fetch(`http://localhost:5000/quiz/detailed-stats?email=${userData.email}`);
        if (!response.ok) throw new Error('Failed to fetch statistics');

        const data = await response.json();
        setStatistics(data.statistics);
      } catch (err) {
        console.error('Error fetching statistics:', err);
        setError('Failed to load statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStatistics();
  }, [navigate]);

  if (loading) return <div className="flex h-screen items-center justify-center">Loading...</div>;
  if (error) return <div className="flex h-screen items-center justify-center text-red-500">{error}</div>;
  if (!statistics) return <div className="flex h-screen items-center justify-center">No data available</div>;

  return (
    <div className="text-right flex h-screen" >
      <Sidebar />
      <div className="chat flex-1 p-8 flex flex-col items-center justify-center" dir="rtl">
        <h1 className="text-3xl font-bold mb-8 text-gray-800">
          التقارير الخاصة بالاختبارات
        </h1>
        <div className="w-full bg-[#3F1515] shadow-lg rounded-lg p-6">
          {Object.keys(statistics).map((stageCode, index) => (
            <div key={index} className="mb-8">
              <h2 className="text-2xl font-bold mb-4 text-white">
                {getStageNameForDisplay(stageCode)}
              </h2>
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-200">
                    <th className="border border-gray-300 px-4 py-2 text-right">
                      المستوى
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-right">
                      الإجابات الصحيحة
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-right">
                      الإجابات الخاطئة
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-right">
                      نسبة النجاح
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(statistics[stageCode]).map(
                    ([level, stats], levelIndex) => (
                      <tr key={levelIndex} className="text-center text-white">
                        <td className="border border-gray-300 px-4 py-2">
                          {level}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {stats[0]}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {stats[1]}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {stats[2]}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Taqarir;

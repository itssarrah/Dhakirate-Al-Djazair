import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import "../styles/quiz2.css";
import "../views/landing.css";
import { ClipLoader } from "react-spinners";
import { useNavigate } from "react-router-dom";

function Quiz2() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [fetchTrigger, setFetchTrigger] = useState(0);
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

  const [dateRanges, setDateRanges] = useState({});
  const [yearRanges, setYearRanges] = useState({});
  const [dateInputs, setDateInputs] = useState({});

  const months = [
    { value: "01", label: "جانفي" },
    { value: "02", label: "فيفري" },
    { value: "03", label: "مارس" },
    { value: "04", label: "أفريل" },
    { value: "05", label: "ماي" },
    { value: "06", label: "جوان" },
    { value: "07", label: "جويلية" },
    { value: "08", label: "أوت" },
    { value: "09", label: "سبتمبر" },
    { value: "10", label: "أكتوبر" },
    { value: "11", label: "نوفمبر" },
    { value: "12", label: "ديسمبر" },
  ];

  // Function to format date for backend
  const formatDate = (date) => {
    if (!date) return "";
    return `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(
      2,
      "0"
    )}/${String(date.getDate()).padStart(2, "0")}`;
  };

  // Function to format date range for backend
  const formatDateRange = (startDate, endDate) => {
    if (!startDate || !endDate) return "";
    return `${formatDate(startDate)}-${formatDate(endDate)}`;
  };

  const isYearOnlyInterval = (date) => {
    return date?.includes("-") && date?.split("-").every((d) => d.length === 4);
  };

  const formatYear = (year) => {
    return year?.toString();
  };

  const formatYearRange = (startYear, endYear) => {
    if (!startYear || !endYear) return "";
    return `${startYear}-${endYear}`;
  };

  const YearPicker = ({ value, onChange, placeholder }) => {
    return (
      <input
        type="number"
        min="1"
        max={new Date().getFullYear()}
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        className="timeline-input"
        placeholder={placeholder}
      />
    );
  };

  const handleDateChange = (
    questionId,
    date,
    isRange = false,
    isStart = true
  ) => {
    if (isRange) {
      setDateRanges((prev) => ({
        ...prev,
        [questionId]: {
          ...prev[questionId],
          [isStart ? "start" : "end"]: date,
        },
      }));

      const range = dateRanges[questionId] || {};
      const startDate = isStart ? date : range.start;
      const endDate = isStart ? range.end : date;

      if (startDate && endDate) {
        handleInputChange(questionId, formatDateRange(startDate, endDate));
      }
    } else {
      handleInputChange(questionId, formatDate(date));
    }
  };

  const handleYearChange = (
    questionId,
    year,
    isRange = false,
    isStart = true
  ) => {
    if (isRange) {
      setYearRanges((prev) => ({
        ...prev,
        [questionId]: {
          ...prev[questionId],
          [isStart ? "start" : "end"]: year,
        },
      }));

      const range = yearRanges[questionId] || {};
      const startYear = isStart ? year : range.start;
      const endYear = isStart ? range.end : year;

      if (startYear && endYear) {
        handleInputChange(questionId, formatYearRange(startYear, endYear));
      }
    } else {
      handleInputChange(questionId, formatYear(year));
    }
  };

  const getDaysInMonth = (year, month) => {
    if (!year || !month) return Array.from({ length: 31 }, (_, i) => i + 1);
    return Array.from(
      { length: new Date(year, month, 0).getDate() },
      (_, i) => i + 1
    );
  };

  const currentYear = new Date().getFullYear();
  const years = Array.from(
    { length: currentYear - 1899 },
    (_, i) => currentYear - i
  );

  const SingleDateInput = ({ questionId }) => {
    const hasDay =
      questions.find((q) => q.id === questionId)?.date?.split("/").length === 3;

    const handleDatePartChange = (part, value) => {
      setDateInputs((prev) => ({
        ...prev,
        [questionId]: {
          ...prev[questionId],
          [part]: value,
        },
      }));

      const currentInputs = {
        ...dateInputs[questionId],
        [part]: value,
      };

      // Format date string based on whether day is required
      if (hasDay) {
        if (currentInputs.year && currentInputs.month && currentInputs.day) {
          handleInputChange(
            questionId,
            `${currentInputs.year}/${currentInputs.month}/${currentInputs.day}`
          );
        }
      } else {
        if (currentInputs.year && currentInputs.month) {
          handleInputChange(
            questionId,
            `${currentInputs.year}/${currentInputs.month}`
          );
        }
      }
    };

    // Generate days array based on month and year
    const getDaysInMonth = (year, month) => {
      if (!year || !month) return Array.from({ length: 31 }, (_, i) => i + 1);
      return Array.from(
        { length: new Date(year, month, 0).getDate() },
        (_, i) => i + 1
      );
    };

    const currentYear = new Date().getFullYear();
    const years = Array.from(
      { length: currentYear - 1899 },
      (_, i) => currentYear - i
    );

    return (
      <div className="date-parts-input">
        {hasDay && (
          <select
            className="timeline-input date-select"
            value={dateInputs[questionId]?.day || ""}
            onChange={(e) =>
              handleDatePartChange("day", e.target.value.padStart(2, "0"))
            }
          >
            <option value="">اليوم</option>
            {getDaysInMonth(
              dateInputs[questionId]?.year,
              dateInputs[questionId]?.month
            ).map((day) => (
              <option key={day} value={day.toString().padStart(2, "0")}>
                {day}
              </option>
            ))}
          </select>
        )}

        <select
          className="timeline-input date-select"
          value={dateInputs[questionId]?.month || ""}
          onChange={(e) => handleDatePartChange("month", e.target.value)}
        >
          <option value="">الشهر</option>
          {months.map((month) => (
            <option key={month.value} value={month.value}>
              {month.label}
            </option>
          ))}
        </select>

        <select
          className="timeline-input date-select"
          value={dateInputs[questionId]?.year || ""}
          onChange={(e) => handleDatePartChange("year", e.target.value)}
        >
          <option value="">السنة</option>
          {years.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>
    );
  };

  const DateIntervalInput = ({ questionId }) => {
    const hasDay =
      questions.find((q) => q.id === questionId)?.date?.split("/")[0].length ===
      10;

    const handleIntervalChange = (position, part, value) => {
      setDateInputs((prev) => ({
        ...prev,
        [questionId]: {
          ...prev[questionId],
          [position]: {
            ...prev[questionId]?.[position],
            [part]: value,
          },
        },
      }));

      const currentInputs = {
        ...dateInputs[questionId],
        [position]: {
          ...dateInputs[questionId]?.[position],
          [part]: value,
        },
      };

      // Format interval string if both dates are complete
      const start = currentInputs.start;
      const end = currentInputs.end;

      if (hasDay) {
        if (
          start?.year &&
          start?.month &&
          start?.day &&
          end?.year &&
          end?.month &&
          end?.day
        ) {
          handleInputChange(
            questionId,
            `${start.year}/${start.month}/${start.day}-${end.year}/${end.month}/${end.day}`
          );
        }
      } else {
        if (start?.year && start?.month && end?.year && end?.month) {
          handleInputChange(
            questionId,
            `${start.year}/${start.month}-${end.year}/${end.month}`
          );
        }
      }
    };

    const DatePartInputs = ({ position }) => (
      <div className="date-parts-group">
        {hasDay && (
          <select
            className="timeline-input date-select"
            value={dateInputs[questionId]?.[position]?.day || ""}
            onChange={(e) =>
              handleIntervalChange(
                position,
                "day",
                e.target.value.padStart(2, "0")
              )
            }
          >
            <option value="">اليوم</option>
            {getDaysInMonth(
              dateInputs[questionId]?.[position]?.year,
              dateInputs[questionId]?.[position]?.month
            ).map((day) => (
              <option key={day} value={day.toString().padStart(2, "0")}>
                {day}
              </option>
            ))}
          </select>
        )}

        <select
          className="timeline-input date-select"
          value={dateInputs[questionId]?.[position]?.month || ""}
          onChange={(e) =>
            handleIntervalChange(position, "month", e.target.value)
          }
        >
          <option value="">الشهر</option>
          {months.map((month) => (
            <option key={month.value} value={month.value}>
              {month.label}
            </option>
          ))}
        </select>

        <select
          className="timeline-input date-select"
          value={dateInputs[questionId]?.[position]?.year || ""}
          onChange={(e) =>
            handleIntervalChange(position, "year", e.target.value)
          }
        >
          <option value="">السنة</option>
          {years.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>
    );

    return (
      <div className="date-interval-input">
        <DatePartInputs position="start" />
        <span className="interval-separator">إلى</span>
        <DatePartInputs position="end" />
      </div>
    );
  };

  const renderDateInput = (question) => {
    if (question.type === 1) {
      // Event → Date question
      if (isYearOnlyInterval(question.date)) {
        // Keep the year interval handling
        return (
          <div className="date-range-input">
            <YearPicker
              value={yearRanges[question.id]?.start}
              onChange={(year) =>
                handleYearChange(question.id, year, true, true)
              }
              placeholder="سنة البداية"
            />
            <span>إلى</span>
            <YearPicker
              value={yearRanges[question.id]?.end}
              onChange={(year) =>
                handleYearChange(question.id, year, true, false)
              }
              placeholder="سنة النهاية"
            />
          </div>
        );
      } else if (question.date?.includes("-")) {
        // Use new interval input instead of DatePicker
        return <DateIntervalInput questionId={question.id} />;
      } else {
        // Replace DatePicker with our new SingleDateInput
        return <SingleDateInput questionId={question.id} />;
      }
    } else {
      // Keep the event input handling
      return (
        <input
          type="text"
          className="timeline-input"
          placeholder="أدخل الحدث"
          value={answers[question.id] || ""}
          onChange={(e) => handleInputChange(question.id, e.target.value)}
          dir="rtl"
        />
      );
    }
  };

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      navigate("/login");
      return;
    }
    setUserData(JSON.parse(storedUser));
  }, [navigate]);

  useEffect(() => {
    let mounted = true;

    const fetchQuiz = async () => {
      if (!userData) return;

      try {
        const response = await fetch(
          "http://localhost:5000/events/quiz/generate",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: userData.email,
              educational_stage: userData.educational_level,
              num_questions: 3,
            }),
          }
        );

        const data = await response.json();
        if (mounted && response.ok) {
          setQuestions(data.quiz);
          const initialAnswers = {};
          data.quiz.forEach((q) => {
            initialAnswers[q.id] = "";
          });
          setAnswers(initialAnswers);
          setLoading(false);
        } else {
          setError(data.error);
          setLoading(false);
        }
      } catch (err) {
        if (mounted) {
          setError("Failed to fetch quiz");
          setLoading(false);
        }
      }
    };

    fetchQuiz();

    return () => {
      mounted = false;
    };
  }, [fetchTrigger, userData]);

  const handleInputChange = (questionId, value) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: value,
    }));
  };

  const handleSubmit = async () => {
    if (!userData) return;

    try {
      const formattedAnswers = Object.entries(answers).map(
        ([questionId, answer]) => {
          const question = questions.find((q) => q.id === parseInt(questionId));
          return {
            question_id: parseInt(questionId),
            type: question.type,
            answer: answer.trim(),
          };
        }
      );

      const response = await fetch("http://localhost:5000/events/quiz/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: userData.email,
          educational_stage: userData.educational_level,
          answers: formattedAnswers,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        const correctCount = data.results.filter(
          (result) => result.correct
        ).length;
        setFeedback(
          `النتيجة النهائية: ${correctCount} من أصل ${questions.length} إجابة صحيحة`
        );
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError("Failed to submit answers");
    }
  };

  if (loading)
    return (
      <>
        <div className="chat flex h-screen">
          <Sidebar />
          <div className="flex flex-col items-center justify-center mx-auto">
            <ClipLoader color="#FFF" size={100} />
            <p className="mt-4 text-lg font-semibold">جاري التحميل...</p>
          </div>
        </div>
      </>
    );
  if (error) return <div>حدث خطأ: {error}</div>;

  return (
    <div className="chat flex h-screen">
      <Sidebar />
      <div className="flex-1 p-8 flex flex-col items-center justify-center">
        <h1 className="text-3xl font-bold mb-20">اختبار التواريخ والأحداث</h1>

        <div className="timeline-container">
          <div
            className={`labels-above-timeline  items-center ${
              questions.filter((question) => question.type === 0).length === 2
                ? "gap-[28rem]"
                : "gap-0"
            }`}
          >
            {questions
              .filter((question) => question.type === 0)
              .map((question) => (
                <div key={question.id} className="timeline-label">
                  <p>التاريخ: {question.date}</p>
                  {renderDateInput(question)}
                </div>
              ))}
          </div>

          <div className="timeline drop-shadow-xl"></div>

          <div
            className={`labels-below-timeline  items-center ${
              questions.filter((question) => question.type !== 0).length === 2
                ? "gap-[28rem]"
                : "gap-0"
            }`}
          >
            {questions
              .filter((question) => question.type !== 0)
              .map((question) => (
                <div key={question.id} className="timeline-label">
                  <p>الحدث: {question.event}</p>
                  {renderDateInput(question)}
                </div>
              ))}
          </div>
        </div>

        <button
          className="bg-[#C08250] text-white py-3 px-6 rounded-lg mt-20"
          onClick={handleSubmit}
          disabled={Object.values(answers).some((answer) => !answer.trim())}
        >
          تحقق
        </button>

        {feedback && (
          <div className="feedback mt-4">
            <p>{feedback}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Quiz2;

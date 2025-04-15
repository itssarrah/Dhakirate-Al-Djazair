import React from "react";
import { useNavigate } from "react-router-dom";
import "./landing.css";

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="all w-screen h-screen overflow-hidden flex flex-col items-center">
      <img
        src="/generallogo.png"
        alt="logo"
        className="w-[10rem] mx-auto mt-20 md:mt-8"
      />
      <img
        src="/dakiratext.png"
        alt="logo"
        className="w-[25rem] md:w-[35rem] mx-auto mt-20 md:mt-10"
      />
      <h2 className="text-center text-xl md:text-4xl text-almarai mt-6">
        اكتشف وتعلم تاريخ الجزائر بطريقة ممتعة ومبتكرة
      </h2>
      <button
        className="mt-10 px-6 py-3 text-white text-lg rounded-full bg-[#3D1010] hover:bg-[#5a1919] transition duration-300 ease-in-out"
        onClick={() => navigate("/signup")}
      >
        سجّل الآن
      </button>
      <button
        className="mt-4 text-[#3D1010] text-lg underline hover:text-[#5a1919] transition duration-300 ease-in-out"
        onClick={() => navigate("/login")}
      >
        تسجيل الدخول
      </button>
    </div>
  );
}

export default LandingPage;

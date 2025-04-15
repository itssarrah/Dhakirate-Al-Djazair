import React from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";

function Molakhas() {
  const navigate = useNavigate();

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 p-8 flex flex-col items-center">
        <h1 className="text-3xl font-bold mb-8">molakhas</h1>
      </div>
    </div>
  );
}

export default Molakhas;

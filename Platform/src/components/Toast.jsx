import React, { useEffect } from 'react';

const Toast = ({ message, type = 'success', onClose }) => {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, 3000);

        return () => clearTimeout(timer);
    }, [onClose]);

    const baseStyles = "fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-500 ease-in-out";
    const typeStyles = {
        success: "bg-green-100 text-green-800 border-l-4 border-green-500",
        error: "bg-red-100 text-red-800 border-l-4 border-red-500",
    };

    return (
        <div className={`${baseStyles} ${typeStyles[type]} animate-slide-in`}>
            {message}
        </div>
    );
};

export default Toast;

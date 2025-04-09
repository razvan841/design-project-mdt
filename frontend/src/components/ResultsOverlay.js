import React from "react";
import "./ResultsOverlay.css";
import DisplayCode from "../assets/DisplayCode.svg"

const Overlay = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null; // Don't render if closed

  return (
    <div className="overlay" onClick={onClose}>
      <div className="overlay-background">
        <div className="overlay-container">
          <div className="overlay-controls">
              <button className="overlay-close" type="button" onClick={onClose}>
                <img src={DisplayCode}></img>
              </button>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
};

export default Overlay;
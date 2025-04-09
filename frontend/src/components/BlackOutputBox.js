import React from "react";
import "./BlackOutputBox.css";

// terminal
const BlackOutputBox = ({children, title}) => {
  return (
    <div className="output-container">
      <div className="output-tab">{title}</div>
      <div className={`output-box ${title}`}>
        {children}
      </div>
    </div>
  );
};

export default BlackOutputBox;

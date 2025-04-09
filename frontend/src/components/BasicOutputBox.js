import React from "react";
import "./BasicOutputBox.css";

// terminal for program output
const BasicOutputBox = ({ title, children }) => {
  return (
    <div className="box">
      <h2 className="box-title">{title}</h2>
      <div className="box-content">{children}</div>
    </div>
  );
};

export default BasicOutputBox;

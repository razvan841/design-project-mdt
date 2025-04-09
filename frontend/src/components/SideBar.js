import React from "react";
import "./SideBar.css";
import Logo from "../assets/Logo.svg"
import Settings from "../assets/Settings.svg"
import AddCell from "../assets/AddCell.svg"
import Start from "../assets/Start.svg"
import Save from "../assets/Save.svg"
import Import from "../assets/Import.svg"
import { useNavigate } from "react-router-dom";
import '../app.css';
import showDiff from "../assets/showDiff.svg"
import Help from "../assets/Help.svg"

// side bar component 
const Sidebar = (props) => {
    const pressHelp = () => {
        // Open the PDF from the public folder
        const base = window.location.href.split('#')[0].replace('index.html', '');
        window.open(`${base}/UserManual.pdf`);
      };

  return (
    <div className="sidebar">
      <div className="top">
        <div className="sidebar-logo-container top" onClick={props.pressLogo}>
          <img src={Logo} alt="Logo with text" />
        </div>
        <button className="sidebar-item" onClick={props.runCodeCells}>
          <img src={Start} />
        </button>
        <button className="sidebar-item" onClick={props.addCodeCell}>
          <img src={AddCell} />
        </button>
        {props.data && <button className="sidebar-item" onClick={props.setDiff}>
          <img src={showDiff} />
        </button>}
      </div>
      <div className="bottom">
        {window.location.hash !== "#/Settings" && (
          <>
            <button className="sidebar-item" onClick={props.pressSave}>
              <img src={Save} />
            </button>
            <button className="sidebar-item" onClick={props.handleImportClick}>
              <input
                type="file"
                accept=".json"
                style={{ display: 'none' }}
                ref={props.inputRef}
                onChange={props.pressImport}
              />
              <img src={Import} />
            </button>
          </>
        )}
        <button className="sidebar-item" onClick={props.pressSettings}>
          <img src={Settings} />
        </button>
        <button className="sidebar-item" onClick={pressHelp}>
          <img src={Help} />
        </button>
      </div>
    </div>
  );
};
export default Sidebar;
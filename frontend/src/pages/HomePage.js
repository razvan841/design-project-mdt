import "../app.css"
import {useRef} from "react";
import Button from "../components/ConfirmButton"
import "./HomePage.css"
import FolderImg from "../assets/CreateNewProject.png"
import OpenFolder from "../assets/OpenExistingProject.svg"
import { useNavigate } from 'react-router-dom'
import {Link} from "react-router-dom"

export default function HomePage() {
    const inputRef = useRef(null);
    const navigate = useNavigate();
    
    const handleImportClick = () => {
      inputRef.current.click();
    };
    
    const importFullSession = (event) => {
      const file = event.target.files?.[0];
      if (!file) return;
  
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const sessionData = JSON.parse(e.target.result);
          sessionStorage.clear();
          for (const [key, value] of Object.entries(sessionData)) {
            sessionStorage.setItem(key, value);
  
            if (key === "data_response") {
                console.log(value);
                sessionStorage.setItem(key, JSON.stringify(value));
            }

            if (key === "finalValues") {
              sessionStorage.setItem("finalValues", JSON.stringify(value))
              sessionStorage.setItem("draftValues", JSON.stringify(value))
            }
  
            if (key === "codeCells") {
              sessionStorage.setItem("codeCells", JSON.stringify(value));
  
              for (let i = 0; i < value.length; i++) {
                const cell = value[i];
                sessionStorage.setItem(`codecell-${i}`, cell.codeText);
                sessionStorage.setItem(`option-Language-${i}`, cell.language);
                sessionStorage.setItem(`option-Version-${i}`, cell.version);
                sessionStorage.setItem(`option-Compiler-${i}`, cell.compiler);
              }
            }
          }
          // window.location.reload(); // Optional
          navigate('CodePage');
          window.location.reload();

        } catch (err) {
          console.error("Failed to load full session:", err);
        }
      };
      reader.readAsText(file);
  
    };
    return (
    <div className="mainHPContainer">
        <div className="logoContainer">
            <img src={require("../assets/LogoWide.png")} alt="Logo with text"/>
        </div>
        <div className="buttonsContainer">
            <Link to="/CodePage">
                <Button footerText={"Create New Project"} imgSrc={FolderImg} altText={"Create new project icon"}/>
            </Link>
            <h1 style={{ fontFamily: "Roboto", fontSize: "24px", fontWeight: "bold", color: "white", textAlign: "center", justifyContent: "center", alignContent: "center", margin: "10px" }}>OR</h1>
            <div className="buttonTextContainer">
                <button onClick= {handleImportClick} className = "buttonIconContainer">
                    <input
                    type="file"
                    accept=".json"
                    style={{ display: 'none' }}
                    ref={inputRef}
                    onChange={importFullSession}
                    />
                    <img className="buttonIcon" src={OpenFolder} alt = {"Open existing project icon"}/>
                </button>
                <span className="buttonText"> Open Existing Project</span>
            </div>
        </div>
    </div>
    );
}
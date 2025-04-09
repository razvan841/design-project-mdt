import { useState } from "react";
import "./HeaderCodeCell.css"

// row in header - language, version, compiler 
export default function HeaderRow({ id, title, options = [], setOption }) {
    // keep in session storage which button was selected for each cell 
    const [selected, setSelected] = useState(sessionStorage.getItem(`option-${title}-${id}`) || " ")

    return (
        <div className="headerRow">
            <div className="title headerText"> {title} </div>
            {/* list of options in section */}
            <div className="options headerText">
                {options.map((option) => (
                    <div key={option} className={`option ${selected === option ? "selected" : ""}`} onClick={() => {
                        setSelected(option);
                        sessionStorage.setItem(`option-${title}-${id}`, option);
                        if (title === "Language") {
                            switch (option) {
                                case "python":
                                    if (!sessionStorage.getItem(`option-Version-${id}`)) {
                                        sessionStorage.setItem(`option-Version-${id}`, "3.10");
                                    }
                                    break;
                                case "cpp":
                                    if (!sessionStorage.getItem(`option-Compiler-${id}`)) {
                                        sessionStorage.setItem(`option-Compiler-${id}`, "gcc");
                                    }
                                    break;
                                case "javascript":
                                    if (!sessionStorage.getItem(`option-Version-${id}`)) {
                                        sessionStorage.setItem(`option-Version-${id}`, "node:19");
                                    }
                                    break;
                                case "php":
                                    if (!sessionStorage.getItem(`option-Version-${id}`)) {
                                        sessionStorage.setItem(`option-Version-${id}`, "php:8.3");
                                    }
                                    break;
                                case "java":
                                    if (!sessionStorage.getItem(`option-Version-${id}`)) {
                                        sessionStorage.setItem(`option-Version-${id}`, "21");
                                    }
                                    if (!sessionStorage.getItem(`option-Compiler-${id}`)) {
                                        sessionStorage.setItem(`option-Compiler-${id}`, "amazoncorretto");
                                    }
                                    break;
                                default:
                                    console.log("how did you get here?")

                            }
                        }
                        setOption(option)
                    }}>
                        {option}
                    </div>
                ))}
            </div>
        </div>
    );
}
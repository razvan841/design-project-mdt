import { useRef, useState } from "react"
import "./CodeFileReader.css"
import "../app.css"

// reader compoennt for code files chosen by user 
export default function CodeFileReader(props) {
    const fileInputRef = useRef(null)

    return (
        <>
            <button className="fileUploadButton" onClick={() => fileInputRef.current.click()}>
                <input type="file" accept=".cpp, .py, .php, .js" onChange={props.handleFileChange} ref={fileInputRef} />
                <span> Upload Code </span>
            </button>
        </>
    );

}
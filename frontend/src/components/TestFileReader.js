import { useRef, useState } from "react"
import "./CodeFileReader.css"
import "../app.css"

// reader component for test files 
export default function TestFileReader(props) {
    const fileInputRef = useRef(null)

    return (
        <>
            <button onClick={() => fileInputRef.current.click()}>
                <input type="file" accept=".txt" onChange={props.handleFileChange} ref={fileInputRef} />
                <span> Upload Test File </span>
            </button>
        </>
    );

}
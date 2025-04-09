import { useState, useRef, useEffect } from "react";
import "../app.css"
import "./CodeCell.css"
import { Editor } from "@monaco-editor/react";
import HeaderCodeCell from "./HeaderCodeCell"
import DisplayOverlay from "../assets/DisplayOverlay.svg"
import Overlay from "./ResultsOverlay"
import Output from "./OverlayContent"

// solution for ResizeObserver issue found on https://github.com/microsoft/vscode/issues/183324
    // Save a reference to the original ResizeObserver
    const OriginalResizeObserver = window.ResizeObserver;

    // Create a new ResizeObserver constructor
    window.ResizeObserver = function (callback) {
    const wrappedCallback = (entries, observer) => {
        window.requestAnimationFrame(() => {
        callback(entries, observer);
        });
    };

    // Create an instance of the original ResizeObserver
    // with the wrapped callback
    return new OriginalResizeObserver(wrappedCallback);
    };

    // Copy over static methods, if any
    for (let staticMethod in OriginalResizeObserver) {
    if (OriginalResizeObserver.hasOwnProperty(staticMethod)) {
        window.ResizeObserver[staticMethod] = OriginalResizeObserver[staticMethod];
    }
    }

export default function CodeCell(props) {
    // check if there is a data response from backend 
    const hasData = props.data && props.data[props.id]
    // const isLoading = props.isLoading

    // state of results overlay 
    const [isOverlayOpen, setIsOverlayOpen] = useState(false)
    const [headerOpen, setHeaderOpen] = useState(false);

    // state of selected language by user - used for highlighting
    const [language, setLanguage] = useState(sessionStorage.getItem(`option-Language-${props.id}`) || "python")

    // code editor 
    const editorRef = useRef(null); // editor reference
    const value = sessionStorage.getItem(`codecell-${props.id}`) || "# insert code here"; // initial session storage to maintain each cell's contents

    function handleEditorMount(editor, monaco) {
        editorRef.current = editor
    }

    const handleChange = () => {
        sessionStorage.setItem(`codecell-${props.id}`,editorRef.current.getValue()) // change value of cell's content in storage
        props.setCodeText(editorRef.current.getValue()) // send new cell content to CodePage
    }

    const statusPercentage = props.status * 100;

    return (
        <div className={props.className} id={props.id}>
            <HeaderCodeCell data={props.data} id = {props.id} setLanguage={props.setLanguage} setCompiler={props.setCompiler} setVersion={props.setVersion} headerOpen={headerOpen} setHeaderOpen={setHeaderOpen}/>
            <Editor
                theme="vs-dark"
                defaultLanguage = {language}
                defaultValue = {value}
                options={{minimap: {enabled:false}}}

                onMount={handleEditorMount}
                onChange={handleChange}
            />
            {props.isLoading && <div className="loading-screen">
                <div className="loading-spinner"></div>
                <div className="loading-bar-container">
                <div
                    className="loading-bar"
                    style={{ width: `${statusPercentage}%` }}
                ></div>
                </div>
            </div>}
            {hasData && !headerOpen && <div className="overlay-button-container">
                <button className="overlay-button" onClick={() => setIsOverlayOpen(!isOverlayOpen)}><img src={DisplayOverlay}></img></button>
            </div>}
            {hasData && <Overlay id={props.id} isOpen={isOverlayOpen} onClose={() => setIsOverlayOpen(!isOverlayOpen)}>
                {Object.keys(props.data[props.id].outputs).map((key) => (
                    <Output key={key} data={props.data[props.id].outputs[key]} id={key} />
                ))}
            </Overlay>}
        </div>
    )
}


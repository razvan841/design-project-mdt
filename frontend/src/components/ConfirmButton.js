import "./ConfirmButton.css"

export default function Button({footerText, imgSrc, altText}) {
    return (
    <div className="buttonTextContainer">
        <button className = "buttonIconContainer"> 
            <img className="buttonIcon" src={imgSrc} alt = {altText}/>
        </button>
        <span className="buttonText"> {footerText} </span>
    </div>
    );
} 


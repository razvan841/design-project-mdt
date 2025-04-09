// dropdown button for configuration menu in code cell header 
export default function DropdownButton(props) {

    return (
        <div onClick={props.dropdownToggle} style={{cursor: "pointer"}}>
            <img src={require("../assets/dropDropArrow.png")} alt="drop down arrow"/>
        </div>
        
    );
}
import React, { useState, useEffect } from 'react';
import "./OverlayContent.css";
import Box from "./BasicOutputBox"
import BlackBox from "./BlackOutputBox"

const Output = ({data, id, key}) => {

    const defaultOverlayConfig = {
        showTimeMetric: true,
        showStorageMetric: true,
        showBlackBox: true,
      };

    const hasError = data.error_msg
    const hasOutput = data.value
    
    const [config, setConfig] = useState(defaultOverlayConfig);

    useEffect(() => {
        const storedConfig = localStorage.getItem('overlayConfig');
        if (storedConfig) {
        setConfig(JSON.parse(storedConfig));
        }
    }, []);

    return (
        <div class="rows-container">
            {(config.showTimeMetric||config.showStorageMetric) && (<div className="output-row-first">
                {config.showTimeMetric && (<Box title="Execution Time">{data.defaultMetrics.executionTime}</Box>)}
                {config.showStorageMetric && (<Box title="Memory Usage">{data.defaultMetrics.memoryUsage}</Box>)}
            </div>)}
            {config.showBlackBox && hasOutput && <BlackBox title={"output"}>{data.value}</BlackBox>}
            {config.showBlackBox && hasError && <BlackBox title={"errors"}>{data.error_msg}</BlackBox>}
    </div>
    )
}
    
export default Output;
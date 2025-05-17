import './ch3.css';
import "../../pages/Page.css";
import Step2_3 from './Step2_3';
import Step2_basic from './Step2_basic';

function Step3() {

    const data = {
     title: "Expert 1 Suggestions ",
     sub_title: "Very good at ... /n Enhanced to do ...",
     content: "Based on the approved project and the recommended Islamic contract type, our AI will: Formulate a detailed financing scenario that describes how the contract will be applied in practice. Use real-world Islamic finance structuring logic (e.g., parallel Istisna’a, Murabaha markup, Ijarah with purchase option). Ensure the contract follows AAOIFI guidelines and reflects the actual project structure — without inventing values or assumptions. Output",
    };

    return (
        <div>
            <div className="grid">
                <div className="left-panel">
                    <h3 className='titles'>3.AI Validating the suggestions</h3>              
                </div>
            </div>
            <div className="grid_3">
                <Step2_3 title={data.title} sub_title={data.sub_title} content={data.content} />
                <Step2_3 title={data.title} sub_title={data.sub_title} content={data.content} />
                <Step2_3 title={data.title} sub_title={data.sub_title} content={data.content} />
            </div>
            <div className="grid">                 
                <Step2_basic title={data.title}  content={data.content} />
            </div>
                
        </div>
    );
}


export default Step3;

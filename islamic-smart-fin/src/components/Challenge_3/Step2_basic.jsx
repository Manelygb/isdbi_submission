function Step2_basic({ title, content }) {  
    return (
        <div className="left-panel">
                    <p className='sub_titles bold'>
                        {title}
                    </p>

                    <div className="text-area major-text">
                        {content}
                    </div>
      </div>
    );
}
export default Step2_basic;
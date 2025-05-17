function Step2_3({ title, sub_title, content }) {  
    return (
        <div className="item">
            <p className='sub_titles'>
                {title}
            </p>
            <p className='major-text'>
                {sub_title}
            </p>
            <div className="text-area major-text">
                {content}
            </div>
        </div>
    );
}

export default Step2_3;
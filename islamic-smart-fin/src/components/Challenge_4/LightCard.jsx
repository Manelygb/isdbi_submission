import React from 'react';
import item_bg from '../../assets/bg_image.svg';
import './ch4.css';

function LightCard({ onClick , title , desc }) {
  return (
    <div className="bg_light" onClick={onClick} style={{ cursor: 'pointer' }}>
      <img src={item_bg} alt="" className="background-img" />
      <div className="text-content">
        <p className="titles bold z-10">
        {title}
        </p>
        <p className="major-text">
        {desc}
        </p>
      </div>
      <button className="action-btn submit-button button-34">
        Run Flow Now
      </button>
    </div>
  );
}

export default LightCard;

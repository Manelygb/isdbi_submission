import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';
import i1 from '../assets/icons/i1.svg';
import i1_h from '../assets/icons/i1_h.svg';
import i2 from '../assets/icons/i2.svg';
import i2_h from '../assets/icons/i2_h.svg';
import i3 from '../assets/icons/i3.svg';
import i3_h from '../assets/icons/i3_h.svg';
import i4 from '../assets/icons/i4.svg';
import i4_h from '../assets/icons/i4_h.svg';

function Sidebar() {
  return (
    <div className="sidebar">
      <h3 className='title-side'>Islamic Smart Fin</h3>

      <div className='line'></div>

      <ul>
        <li>
          <NavLink
            to="/"
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            <img 
              src={i1} 
              alt="Use Cases" 
              className="nav-icon" 
            />
            <img 
              src={i1_h} 
              alt="Use Cases Hovered" 
              className="nav-icon-hover" 
            />
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/reverse-audit"
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            <img 
              src={i2} 
              alt="Reverse Audit" 
              className="nav-icon" 
            />
            <img 
              src={i2_h} 
              alt="Reverse Audit Hovered" 
              className="nav-icon-hover" 
            />
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/standards-lab"
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            <img 
              src={i3} 
              alt="Standards Lab" 
              className="nav-icon" 
            />
            <img 
              src={i3_h} 
              alt="Standards Lab Hovered" 
              className="nav-icon-hover" 
            />
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/smart-advisor"
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            <img 
              src={i4} 
              alt="Smart Advisor" 
              className="nav-icon" 
            />
            <img 
              src={i4_h} 
              alt="Smart Advisor Hovered" 
              className="nav-icon-hover" 
            />
          </NavLink>
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;

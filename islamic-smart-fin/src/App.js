import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ReverseAudit from './pages/ReverseAudit';
import UseCases from './pages/UseCases';
import StandardsLab from './pages/StandardsLab';
import SmartAdvisor from './pages/SmartAdvisor';
import './App.css';
import Sidebar from './components/Sidebar';

function App() {
  return (
    <Router>
    <div style={{ display: 'flex' }}>
      <Sidebar />
      <div style={{ padding: 20, flex: 1 }}>
        <Routes>
        <Route path="/" element={<UseCases />} />
            <Route path="/reverse-audit" element={<ReverseAudit />} />
            <Route path="/standards-lab" element={<StandardsLab />} />
            <Route path="/smart-advisor" element={<SmartAdvisor />} />
        </Routes>
      </div>
    </div>
  </Router>
  );
}

export default App;

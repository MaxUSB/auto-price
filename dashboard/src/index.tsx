import './index.css';
import React from 'react';
import ReactDOM from 'react-dom';
import Start from './pages/start';
import Predict from './pages/predict';
import { BrowserRouter, Routes, Route } from "react-router-dom";

ReactDOM.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Start/>}/>
      <Route path="/predict" element={<Predict/>}/>
    </Routes>
  </BrowserRouter>,
  document.getElementById('app')
);

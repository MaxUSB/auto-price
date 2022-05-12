import './index.css';
import React from 'react';
import Start from './pages/start';
import Predict from './pages/predict';
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

const root = createRoot(document.getElementById('app')!);
root.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Start/>}/>
      <Route path="/predict" element={<Predict/>}/>
    </Routes>
  </BrowserRouter>
);

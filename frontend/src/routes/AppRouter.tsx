import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from '../pages/Login';
import Home from '../pages/Home';
// ... tus otras importaciones

const AppRouter: React.FC = () => (
  <BrowserRouter>
    <Routes>
      {/* públicas */}
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Home />} />
    </Routes>
  </BrowserRouter>
);

export default AppRouter;
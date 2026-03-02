import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from '../pages/Login';
import Home from '../pages/Home';
import Register from '../pages/Register';
import Layout from '../components/Layout';
import CreateQueja from '../pages/CreateQueja';
import PrivateRoute from './PrivateRoute';

const AppRouter: React.FC = () => (
  <BrowserRouter>
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<PrivateRoute/>}>
          <Route path="/create-queja" element={<CreateQueja/>} />
        </Route>
      </Route>
    </Routes>
  </BrowserRouter>
);

export default AppRouter;
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from '../pages/Login';
import Home from '../pages/Home';
import Register from '../pages/Register';
import Layout from '../components/Layout';
import QuejaCreate from '../pages/QuejaCreate';
import PrivateRoute from './PrivateRoute';
import QuejaDetail from '../pages/QuejaDetail';
import PerfilDetail from '../pages/PerfilDetail';

const AppRouter: React.FC = () => (
  <BrowserRouter>
    <Routes>

      <Route element={<Layout />}>

        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/quejas/:id" element={<QuejaDetail />} />

        {/* Rutas privadas */}
        <Route element={<PrivateRoute />}>
          <Route path="/create-queja" element={<QuejaCreate />} />
          <Route path="/perfil/:id" element={<PerfilDetail />} />
        </Route>

      </Route>

    </Routes>
  </BrowserRouter>
);

export default AppRouter;
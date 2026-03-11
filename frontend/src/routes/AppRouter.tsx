import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from '../pages/Login';
import Home from '../pages/Home';
import Register from '../pages/Register';
import Layout from '../components/Layout';
import QuejaCreate from '../pages/QuejaCreate';
import QuejaUpdate from '../pages/QuejaUpdate';
import PrivateRouteCrearQueja from './PrivateRouteCrearQueja';
import QuejaDetail from '../pages/QuejaDetail';
import PerfilDetail from '../pages/PerfilDetail';
import PerfilUpdate from '../pages/PerfilUpdate';
import PrivateRoute from './PrivateRoute';
import RutaProhibida from '../pages/RutaProhibida';
import ChangePassword from '../pages/ChangePassword';

const AppRouter: React.FC = () => (
  <BrowserRouter>
    <Routes>

      <Route element={<Layout />}>

        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/quejas/:id" element={<QuejaDetail />} />
        <Route path="/perfil/:id" element={<PerfilDetail />} />
        <Route path="/ruta-prohibida" element={<RutaProhibida />} />
        <Route path="/quejas/:id/update" element={<QuejaUpdate />} />

        {/* Rutas privadas */}
        <Route element={<PrivateRouteCrearQueja />}>
          <Route path="/create-queja" element={<QuejaCreate />} />
        </Route>
        <Route element={<PrivateRoute/>}>
          <Route path="perfil/:id/update/"element={<PerfilUpdate/>}/>
          <Route path="perfil/:id/change-password/"element={<ChangePassword/>}/>
        </Route>

      </Route>

    </Routes>
  </BrowserRouter>
);

export default AppRouter;
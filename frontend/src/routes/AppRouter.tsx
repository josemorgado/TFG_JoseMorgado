import React from "react";
import { Routes, Route } from "react-router-dom";

import Login from "../pages/Login";
import Home from "../pages/Home";
import Register from "../pages/Register";
import Layout from "../components/Layout";
import QuejaCreate from "../pages/QuejaCreate";
import QuejaUpdate from "../pages/QuejaUpdate";
import QuejaDetail from "../pages/QuejaDetail";
import PerfilDetail from "../pages/PerfilDetail";
import PerfilUpdate from "../pages/PerfilUpdate";
import PrivateRoute from "./PrivateRoute";
import RutaProhibida from "../pages/RutaProhibida";
import ChangePassword from "../pages/ChangePassword";
import QuejasList from "../pages/QuejasList";
import ResetPassword from "../pages/ResetPassword";
import EnterToken from "../pages/EnterToken";
import NewPassword from "../pages/NewPassword";
import Stats from "../pages/Stats";
import Notificaciones from "../pages/Notificaciones";
import QuejaRespuestasPage from "../pages/QuejaRespuestas";
import QuejaResponder from "../pages/QuejaResponder";
import Contacto from "../pages/Contacto";
import ModeradorOptions from "../pages/ModeradorOptions";
import EditarCategoria from "../pages/EditarCategoria";
import EditarDistrito from "../pages/EditarDistrito";
import PrivateRouteModerador from "./PrivateRouteModerator";

const AppRouter: React.FC = () => (
  <Routes>
    <Route element={<Layout />}>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/quejas/" element={<QuejasList />} />
      <Route path="/quejas/:id" element={<QuejaDetail />} />
      <Route path="/contact" element={<Contacto />} />
      <Route path="/stats/" element={<Stats />} />
      <Route path="/quejas/:quejaId/respuestas" element={<QuejaRespuestasPage />} />
      <Route path="/ruta-prohibida" element={<RutaProhibida />} />
      <Route path="/reset-password/" element={<ResetPassword />} />
      <Route path="/enter-token/" element={<EnterToken />} />
      <Route path="/new-password/" element={<NewPassword />} />
      <Route element={<PrivateRouteModerador />}>
        <Route path="/quejas/:quejaId/responder" element={<QuejaResponder />} />
        <Route path="/moderador" element={<ModeradorOptions />} />
        <Route path="/moderador/categorias/:id/editar" element={<EditarCategoria />} />
        <Route path="/moderador/distritos/:id/editar" element={<EditarDistrito />} />

      </Route>

      <Route element={<PrivateRoute reason="create-queja" />}>
        <Route path="/create-queja" element={<QuejaCreate />} />
      </Route>

      <Route element={<PrivateRoute reason="edit-queja" />}>
        <Route path="/quejas/:id/update" element={<QuejaUpdate />} />
      </Route>

      <Route element={<PrivateRoute reason="change-password" />}>
        <Route path="/perfil/:id/change-password" element={<ChangePassword />} />
      </Route>


      <Route element={<PrivateRoute />}>
        <Route path="/perfil/:id/update/" element={<PerfilUpdate />} />
        <Route path="/perfil/:id/change-password/" element={<ChangePassword />} />
        <Route path="/notificaciones/" element={<Notificaciones />} />
        <Route path="/perfil/:id/" element={<PerfilDetail />} />
      </Route>
    </Route>
  </Routes>
);

export default AppRouter;
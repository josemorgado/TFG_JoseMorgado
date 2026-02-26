import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLocation, useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation() as any;

  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = location.state?.from?.pathname ?? '/';

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(form);
      navigate(from, { replace: true });
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Usuario o contraseña incorrectos');
      } else {
        setError('Error del servidor, inténtalo de nuevo más tarde');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 420, margin: '6rem auto' }}>
      <h1>Iniciar sesión</h1>
      <form onSubmit={onSubmit}>
        <label>
          Usuario
          <input
            value={form.username}
            onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
            autoComplete="username"
            required
          />
        </label>
        <label style={{ display: 'block', marginTop: 8 }}>
          Contraseña
          <input
            type="password"
            value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
            autoComplete="current-password"
            required
          />
        </label>
        <button disabled={loading} type="submit" style={{ marginTop: 12 }}>
          {loading ? 'Entrando…' : 'Entrar'}
        </button>
        {error && <p style={{ color: 'crimson' }}>{error}</p>}
      </form>
    </div>
  );
};

export default Login;
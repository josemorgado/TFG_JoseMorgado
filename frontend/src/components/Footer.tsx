import "../styles/Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer__inner">

        {/* Izquierda */}
        <div className="footer__left">
          © {new Date().getFullYear()} Alcalde Escúchame — Todos los derechos reservados.
        </div>

        {/* Derecha */}
        <div className="footer__right">


          {/* Correo */}
          <a href="mailto:010Lineasevilla@sevilla.org" title="Enviar correo">
            <svg className="icon" viewBox="0 0 24 24">
              <path fill="currentColor"
                d="M4 4h16a2 2 0 012 2v1l-10 6L2 7V6a2 2 0 012-2zm18 5l-10 6L2 9v9a2 2 0 002 2h16a2 2 0 002-2V9z"/>
            </svg>
          </a>

          {/* X (Twitter) */}
          <a href="https://x.com/Ayto_Sevilla" target="_blank" rel="noopener noreferrer">
            <svg className="icon" viewBox="0 0 24 24">
              <path fill="currentColor"
                d="M4 4l7.5 8.5L4 20h3l6-7 6 7h3l-7.5-7.5L20 4h-3l-6 7-6-7H4z"/>
            </svg>
          </a>

          {/* Instagram */}
          <a href="https://www.instagram.com/ayto_sevilla/" target="_blank" rel="noopener noreferrer">
            <svg className="icon" viewBox="0 0 24 24">
              <path fill="currentColor"
                d="M7 2h10a5 5 0 015 5v10a5 5 0 01-5 5H7a5 5 0 01-5-5V7a5 5 0 015-5zm5 5a5 5 0 100 10 5 5 0 000-10zm6.5-1.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"/>
            </svg>
          </a>

        </div>
      </div>
    </footer>
  );
};

export default Footer;
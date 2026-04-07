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
          <a href="/contact" className="footer__contacto">
            Contacto
          </a>
        </div>

      </div>
    </footer>
  );
};

export default Footer;
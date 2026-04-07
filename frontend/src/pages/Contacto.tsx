import "../styles/contacto.css";

export default function Contacto() {
  return (
    <div className="contacto-page">
      <header className="contacto-header">
        <h1>Contacto</h1>
        <p>
          Canales oficiales y académicos relacionados con el proyecto
          <strong> “Alcalde, escúchame”</strong>.
        </p>
      </header>

      <div className="contacto-grid">
        {/* Ayuntamiento */}
        <section className="contacto-card">
          <h2>🏛 Ayuntamiento de Sevilla</h2>
          <p>
            Plataforma integrada en un sistema de participación ciudadana
            orientado a mejorar la comunicación entre los vecinos y el
            Ayuntamiento de Sevilla.
          </p>

          <ul className="contacto-list">
            <li>
              <strong>📍 Dirección:</strong>
              <span>Plaza Nueva, 1 – 41001 Sevilla</span>
            </li>
            <li>
              <strong>☎ Teléfono:</strong>
              <span>010</span>
            </li>
            <li>
              <strong>✉ Email:</strong>
              <a href="mailto:atencionciudadana@sevilla.org">
                atencionciudadana@sevilla.org
              </a>
            </li>
            <li>
              <strong>🌐 Web:</strong>
              <a
                href="https://www.sevilla.org"
                target="_blank"
                rel="noreferrer"
              >
                www.sevilla.org
              </a>
            </li>
          </ul>
        </section>

        {/* Autor */}
        <section className="contacto-card contacto-autor">
          <h2>👨‍💻 Autor del proyecto</h2>
          <p>
            Trabajo Fin de Grado. Para cuestiones técnicas o académicas puedes
            contactar directamente conmigo.
          </p>

          <ul className="contacto-list">
            <li>
              <strong>Nombre:</strong>
              <span>José María Morgado Prudencio</span>
            </li>
            <li>
              <strong>📱 Teléfono:</strong>
              <a href="tel:630974036">630 974 036</a>
            </li>
            <li>
              <strong>✉ Email:</strong>
              <a href="mailto:josemaria1.jmmp@gmail.com">
                josemaria1.jmmp@gmail.com
              </a>
            </li>
            <li>
              <strong>LinkedIn:</strong>
              <a
                href="https://www.linkedin.com/in/jose-morgado-prudencio-79b539257/"
                target="_blank"
                rel="noreferrer"
              >
                Ver perfil
              </a>
            </li>
            <li>
              <strong>GitHub:</strong>
              <a
                href="https://github.com/josemorgado"
                target="_blank"
                rel="noreferrer"
              >
                github.com/josemorgado
              </a>
            </li>
          </ul>
        </section>

        {/* Universidad */}
        <section className="contacto-card contacto-us">
          <h2>🎓 Universidad de Sevilla</h2>
          <p>
            Enlaces relacionados con la Universidad de Sevilla y el entorno
            académico del proyecto.
          </p>

          <ul className="contacto-links">
            <li>
              <a href="https://www.us.es" target="_blank" rel="noreferrer">
                🌐 Universidad de Sevilla
              </a>
            </li>
            <li>
              <a
                href="https://etsi.us.es"
                target="_blank"
                rel="noreferrer"
              >
                🏫 ETS Ingeniería Informática
              </a>
            </li>
            <li>
              <a
                href="https://bib.us.es"
                target="_blank"
                rel="noreferrer"
              >
                📚 Biblioteca Universitaria
              </a>
            </li>
            <li>
              <a
                href="https://sevius4.us.es"
                target="_blank"
                rel="noreferrer"
              >
                🧑‍🎓 Secretaría Virtual (SEVIUS)
              </a>
            </li>
            <li>
              <a
                href="https://www.us.es/estudios/grado"
                target="_blank"
                rel="noreferrer"
              >
                📄 Estudios de Grado
              </a>
            </li>
          </ul>
        </section>
      </div>
    </div>
  );
}
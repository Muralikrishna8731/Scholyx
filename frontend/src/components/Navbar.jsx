
import { useState } from "react";
import { Link } from "react-router-dom";

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="navbar">
      <Link to="/" className="logo">
        Schol<span>yx</span>
      </Link>

      <button
        className="menu-toggle"
        onClick={() => setMenuOpen(!menuOpen)}
        aria-label="Toggle navigation menu"
        aria-expanded={menuOpen}
      >
        ☰
      </button>

      <div className={`nav-links ${menuOpen ? "active" : ""}`}>
        <a href="#scholarships" onClick={() => setMenuOpen(false)}>
          Scholarships
        </a>
        <a href="#about" onClick={() => setMenuOpen(false)}>
          About
        </a>

        <div className="nav-buttons">
          <Link to="/login" className="login-btn">
            Login
          </Link>
          <Link to="/register" className="get-started-btn">
            Get Started
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;

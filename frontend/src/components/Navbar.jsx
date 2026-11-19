
import { useState } from "react";
import { Link } from "react-router-dom";

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => setMenuOpen(false);

  return (
    <nav className="navbar">
      <Link to="/" className="logo" onClick={closeMenu}>
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
        <Link to="/scholarships" onClick={closeMenu}>
          Scholarships
        </Link>

        <Link to="/#about" onClick={closeMenu}>
          About
        </Link>

        <div className="nav-buttons">
          <Link to="/login" className="login-btn" onClick={closeMenu}>
            Login
          </Link>

          <Link to="/register" className="get-started-btn" onClick={closeMenu}>
            Get Started
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;

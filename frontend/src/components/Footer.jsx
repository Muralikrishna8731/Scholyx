
import { Link } from "react-router-dom";

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-brand">
          <Link to="/" className="logo">
            Schol<span>yx</span>
          </Link>
          <p>
            Discover scholarships, check your eligibility,
            and take the next step towards your dreams.
          </p>
        </div>

        <div className="footer-links">
          <h3>Quick Links</h3>
          <a href="#scholarships">Scholarships</a>
          <a href="#about">About Us</a>
          <Link to="/login">Login</Link>
          <Link to="/register">Get Started</Link>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© {new Date().getFullYear()} Scholyx. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;

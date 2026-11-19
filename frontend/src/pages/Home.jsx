
import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import ScholarshipCard from "../components/ScholarshipCard";

function Home() {
  const [scholarships, setScholarships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchScholarships = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/scholarships/"
        );

        if (!response.ok) {
          throw new Error("Unable to load scholarships.");
        }

        const data = await response.json();
        setScholarships(
          Array.isArray(data) ? data : data.results || []
        );
      } catch (err) {
        setError(err.message || "Something went wrong.");
      } finally {
        setLoading(false);
      }
    };

    fetchScholarships();
  }, []);

  const filteredScholarships = scholarships.filter((scholarship) =>
    scholarship.name?.toLowerCase().includes(search.toLowerCase()) ||
    scholarship.provider?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <Navbar />

      <main>
        <section className="hero">
          <div className="hero-content">
            <span className="hero-tag">YOUR FUTURE STARTS HERE</span>

            <h1>
              Find the Right Scholarship.
              <span> Shape Your Future.</span>
            </h1>

            <p>
              Discover scholarship opportunities that match your goals.
              Check your eligibility and move closer to your dreams.
            </p>

            <div className="hero-search">
              <input
                type="text"
                placeholder="Search scholarships..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />

              <button
                onClick={() =>
                  document.getElementById("scholarships")?.scrollIntoView({
                    behavior: "smooth",
                  })
                }
              >
                Explore Scholarships
              </button>
            </div>

            <div className="hero-note">
              <span>✓</span> Discover opportunities in one place
            </div>
          </div>

          <div className="hero-visual">
            <div className="visual-card">
              <div className="visual-icon">🎓</div>
              <h3>Your Education</h3>
              <p>Deserves Every Opportunity</p>
              <div className="visual-line"></div>
              <div className="visual-line short"></div>
              <span className="visual-badge">
                Explore. Apply. Achieve.
              </span>
            </div>
          </div>
        </section>

        <section className="scholarships-section" id="scholarships">
          <div className="section-heading">
            <span className="section-tag">OPPORTUNITIES FOR YOU</span>
            <h2>Featured Scholarships</h2>
            <p>
              Explore available scholarships and find the right opportunity.
            </p>
          </div>

          {loading ? (
            <p className="status-message">Loading scholarships...</p>
          ) : error ? (
            <p className="status-message error">{error}</p>
          ) : filteredScholarships.length === 0 ? (
            <p className="status-message">
              {search
                ? "No scholarships match your search."
                : "No scholarships available at the moment. Please check back later."}
            </p>
          ) : (
            <div className="scholarship-grid">
              {filteredScholarships.slice(0, 6).map((scholarship) => (
                <ScholarshipCard
                  key={scholarship.id}
                  scholarship={scholarship}
                />
              ))}
            </div>
          )}
        </section>

        <section className="how-section" id="about">
          <div className="section-heading">
            <span className="section-tag">SIMPLE AND EASY</span>
            <h2>How Scholyx Works</h2>
            <p>
              Three simple steps to discover your scholarship opportunities.
            </p>
          </div>

          <div className="steps-grid">
            <div className="step-card">
              <div className="step-icon">🔍</div>
              <span className="step-number">01</span>
              <h3>Explore Scholarships</h3>
              <p>Browse scholarship opportunities available on Scholyx.</p>
            </div>

            <div className="step-card">
              <div className="step-icon">👤</div>
              <span className="step-number">02</span>
              <h3>Create Your Profile</h3>
              <p>Add your academic and personal details to your profile.</p>
            </div>

            <div className="step-card">
              <div className="step-icon">✓</div>
              <span className="step-number">03</span>
              <h3>Check Eligibility</h3>
              <p>Find scholarships that match your eligibility criteria.</p>
            </div>
          </div>
        </section>

        <section className="cta-section">
          <h2>Ready to Find Your Opportunity?</h2>
          <p>Create your profile and start exploring scholarships today.</p>

          <button
            onClick={() => window.location.href = "/register"}
            className="cta-button"
          >
            Get Started →
          </button>
        </section>
      </main>

      <Footer />
    </>
  );
}

export default Home;

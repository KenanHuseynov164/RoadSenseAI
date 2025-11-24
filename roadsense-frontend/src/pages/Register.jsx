import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { registerUser } from "../api";
import "../assets/signup.css";

function Register() {
  const nav = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMsg("");

    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    try {
      await registerUser(email, name, password);
      setMsg("Registration successful! Redirecting to login...");
      setTimeout(() => nav("/login"), 1500);
    } catch (err) {
      if (err.response?.data?.detail === "Email already registered") {
        setError("This email is already registered.");
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Registration failed. Try again.");
      }
    }
  };

  return (
    <div className="login-container">
      <header>
        <h1 className="logo">Know Your Rights</h1>
        <p>Join drivers who know their rights.</p>
      </header>

      <main className="login-box">
        <h2>Driver Sign Up</h2>
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="name">Full Name</label>
            <input
              id="name"
              type="text"
              placeholder="Enter your full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">Create Password</label>
            <input
              id="password"
              type="password"
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="confirm-password">Confirm Password</label>
            <input
              id="confirm-password"
              type="password"
              placeholder="Re-enter your password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
            />
          </div>

          {error && <p className="error-text">{error}</p>}
          {msg && <p className="success-text">{msg}</p>}

          <button type="submit" className="login-btn">
            Sign Up
          </button>
        </form>

        <div className="social-login">
          <p className="separator-text">or sign up with</p>
          <div className="social-btn-group">
            <button className="social-btn google">
              <i className="fab fa-google" /> Google
            </button>
            <button className="social-btn apple">
              <i className="fab fa-apple" /> Apple
            </button>
            <button className="social-btn facebook">
              <i className="fab fa-facebook-f" /> Facebook
            </button>
          </div>
        </div>

        <div className="aux-links">
          <a href="#">Forgot Password?</a>
          <span className="separator">|</span>
          <Link to="/login">Already a Member? Log In</Link>
        </div>
      </main>

      <footer>
        <p>&copy; 2025 Know Your Rights Project</p>
      </footer>
    </div>
  );
}

export default Register;

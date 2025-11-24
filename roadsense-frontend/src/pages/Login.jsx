import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { loginUser } from "../api";
import "../assets/login.css";

function Login() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await loginUser(email, password);
      localStorage.setItem("token", res.data.access_token);
      nav("/");
    } catch {
      setError("Invalid email or password");
    }
  };

  return (
    <div className="login-container">
      <header>
        <h1 className="logo">Know Your Rights</h1>
        <p>Empowering drivers one conversation at a time.</p>
      </header>

      <main className="login-box">
        <h2>Driver Login</h2>

        <form id="login-form" onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <p className="error-text">{error}</p>}

          <div className="remember-me">
            <input type="checkbox" id="remember" />
            <label htmlFor="remember">Remember Me</label>
          </div>

          <button type="submit" className="login-btn">
            Log In
          </button>
        </form>

        <div className="social-login">
          <p className="separator-text">or log in with</p>

          <div className="social-btn-group">
            <button className="social-btn google">
              <i className="fab fa-google"></i> Google
            </button>
            <button className="social-btn apple">
              <i className="fab fa-apple"></i> Apple
            </button>
            <button className="social-btn facebook">
              <i className="fab fa-facebook-f"></i> Facebook
            </button>
          </div>
        </div>

        <div className="aux-links">
          <a href="#">Forgot Password?</a>
          <span className="separator">|</span>
          <Link to="/register">New Driver? Sign Up</Link>
        </div>
      </main>

      <footer>
        <p>&copy; 2025 Know Your Rights Project</p>
      </footer>
    </div>
  );
}

export default Login;

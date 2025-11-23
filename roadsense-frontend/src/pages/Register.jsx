import { useState } from "react";
import { registerUser } from "../api";
import { useNavigate } from "react-router-dom";

function Register() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await registerUser(email, password);
      setMsg("Registration successful! You can now log in.");
      setTimeout(() => nav("/login"), 1500);
    } catch (err) {
      setError("Email already registered");
    }
  };

  return (
    <div className="auth-container">
      <h2>Register</h2>

      <form onSubmit={handleRegister}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p className="error">{error}</p>}
        {msg && <p className="success">{msg}</p>}

        <button type="submit">Register</button>
      </form>
    </div>
  );
}

export default Register;

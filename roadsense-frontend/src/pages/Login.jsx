import { useState } from "react";
import { loginUser } from "../api";
import { useNavigate } from "react-router-dom";

function Login() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await loginUser(email, password);
      localStorage.setItem("token", res.data.access_token);
      nav("/");
    } catch (err) {
      setError("Invalid email or password");
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>

      <form onSubmit={handleLogin}>
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

        <button type="submit">Login</button>
      </form>

      <p>
        Don’t have an account?{" "}
        <a onClick={() => nav("/register")} style={{ cursor: "pointer" }}>
          Register
        </a>
      </p>
    </div>
  );
}

export default Login;

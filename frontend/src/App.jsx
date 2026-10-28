import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import RouteDetail from "./pages/RouteDetail";
import PublishRoute from "./pages/PublishRoute";

export default function App() {
  return (
    <>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/routes/:id" element={<RouteDetail />} />
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/routes/:id" element={<RouteDetail />} />
          <Route path="/publish" element={<PublishRoute />} />
        </Routes>
      </main>
    </>
  );
}